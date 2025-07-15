from dagster import graph, ScheduleDefinition, Definitions
import sys
from pathlib import Path
sys.path.append('../scripts')
from scrapy import start_scrape
from load_data import load_channel
import dagster as dg

from dagster_dbt import dbt_cli_resource, load_assets_from_dbt_project

# Assuming your dbt project is in a 'dbt_project' subdirectory
# and your profiles.yml is within the dbt_project directory (or a 'profiles' sub-directory)
DBT_PROJECT_DIR = Path(__file__).parent.joinpath("../my_project")
DBT_PROFILES_DIR = "/home/mikiask/.dbt/" # or DBT_PROJECT_DIR.joinpath("profiles") if you have a separate profiles folder
print(DBT_PROJECT_DIR)
# Load dbt assets
dbt_assets = load_assets_from_dbt_project(
    project_dir=str(DBT_PROJECT_DIR),
    profiles_dir=str(DBT_PROFILES_DIR),
)

# Define the dbt CLI resource
my_dbt_resource = dbt_cli_resource.configured({
    "project_dir": str(DBT_PROJECT_DIR),
    "profiles_dir": str(DBT_PROFILES_DIR),
})

@graph
def pipeline():
    start_scrape()
    load_channel()


@dg.job(resource_defs={"dbt":my_dbt_resource})
def full_data_pipeline():
    pipeline()

pipeline_job = pipeline.to_job()
Daily_schedule = ScheduleDefinition(
    job=pipeline_job,
    cron_schedule="1 * * * *"
)

defs = Definitions(
    assets=[*dbt_assets],
    resources={
        "dbt":my_dbt_resource
    },
    jobs=[pipeline_job],
    schedules=[Daily_schedule]
)