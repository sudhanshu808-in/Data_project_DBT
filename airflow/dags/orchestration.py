import time

from airflow.sdk import dag, task
from airflow.operators.bash import BashOperator
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import RunLifeCycleState, RunResultState

@dag(schedule=None, catchup=False, tags=["walmart"])
def orchestrate():

    @task
    def ingest_cdc():
        # Reads DATABRICKS_HOST and DATABRICKS_TOKEN from the environment (airflow/.env)
        ws = WorkspaceClient()

        job_trigger = ws.jobs.run_now(job_id=96927723205045)

        while True:
            job_run = ws.jobs.get_run(job_trigger.run_id)
            print(f"Job run state: {job_run.state.life_cycle_state}, result state: {job_run.state.result_state}")
            if job_run.state.result_state == RunResultState.SUCCESS:
                print("Job run completed successfully.")
                break
            if job_run.state.life_cycle_state in [RunLifeCycleState.TERMINATED, RunLifeCycleState.SKIPPED, RunLifeCycleState.INTERNAL_ERROR]:
                raise Exception(f"Job run failed with state: {job_run.state.life_cycle_state}, result: {job_run.state.result_state}")
            time.sleep(10)
        return "CDC ingestion completed successfully."
    
    @task.bash
    def clean_target():
        return "rm -rf /opt/airflow/walmart_project/target && rm -rf /opt/airflow/walmart_project/logs"
    
    @task.bash
    def source_freshness():
        return "rm -rf /opt/airflow/walmart_project/target && cd /opt/airflow/walmart_project && dbt source freshness"

    silver_technical = BashOperator(
        task_id = 'silver_technical',
        bash_command = 'cd /opt/airflow/walmart_project && dbt run --select silver_t'
    )
    
    silver_technical_tests = BashOperator(
        task_id = 'silver_technical_tests',
        bash_command = 'cd /opt/airflow/walmart_project && dbt test --select silver_t'
    )

    silver_buisness = BashOperator(
        task_id = 'silver_buisness',
        bash_command = 'cd /opt/airflow/walmart_project && dbt run --select silver_b'
    )

    silver_buisness_tests = BashOperator(
        task_id = 'silver_buisness_test',
        bash_command = 'cd /opt/airflow/walmart_project && dbt test --select silver_b'
    )

    gold_ephemeral = BashOperator(
        task_id = 'gold_ephemeral',
        bash_command = 'cd /opt/airflow/walmart_project && dbt run --select gold/ephemeral '
    )

    gold_dimensions = BashOperator(
        task_id = 'gold_dimensions',
        bash_command = 'cd /opt/airflow/walmart_project && dbt snapshot'
    )

    gold_facts = BashOperator(
        task_id = 'gold_facts',
        bash_command = 'cd /opt/airflow/walmart_project && dbt run --select gold/facts'
    )


    ingest_cdc() >> clean_target() >> source_freshness() >> silver_technical >> silver_technical_tests >> silver_buisness >> silver_buisness_tests >> gold_ephemeral >> gold_dimensions >> gold_facts


orchestrate_dag = orchestrate()
