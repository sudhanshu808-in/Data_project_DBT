import time
from pathlib import Path

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv
from databricks.sdk.service.jobs import RunLifeCycleState, RunResultState

# Load DATABRICKS_HOST and DATABRICKS_TOKEN from airflow/.env
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

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
    time.sleep(10)  # Wait for 10 seconds before checking the job run status again
