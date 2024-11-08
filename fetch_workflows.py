import os
import requests
import json
from datetime import datetime


GH_PAT = os.environ["GH_PAT"]
OWNER = "ktulu2602"

REPOS = [
    "dashboard-test-repo-01",
    "dashboard-test-repo-02"
]


HEADERS = {
    "Authorization": f"Bearer {GH_PAT}",
    "Accept": "application/vnd.github.v3+json"
}

def write_workflow_runs_to_file(workflow_runs: list) -> None:
    workflow_runs_dict = {
        "results": workflow_runs
    }

    with open("workflow_runs_results.json", "w") as json_file:
        json.dump(workflow_runs_dict , json_file, indent=2)

def calculate_run_duration(start: str, end: str) -> str:
    start_time = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
    end_time = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')

    duration = end_time - start_time

    # Get the duration in seconds
    duration_in_seconds = int(duration.total_seconds())

    # Convert seconds to HH:MM:SS format
    hours, remainder = divmod(duration_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"

    return duration_formatted

def get_workflows(repo_name: str, per_page: str=100):
    """Get all workflows for a GitHub repository, handling pagination."""
    workflows = []
    page = 1
    
    while True:
        url = f"https://api.github.com/repos/{OWNER}/{repo_name}/actions/workflows"
        params = {"per_page": per_page, "page": page}
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        
        data = response.json().get("workflows", [])
        
        # Break the loop if no more workflows are found
        if not data:
            break

        workflows.extend(data)
        page += 1
    
    return workflows

def get_latest_workflow_run_status(repo_name, workflow_id):
    """Get the latest run status of a specific workflow."""
    url = f"https://api.github.com/repos/{OWNER}/{repo_name}/actions/workflows/{workflow_id}/runs?per_page=1"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    # pprint(response.json())
    wf_runs = response.json().get("workflow_runs", [])
    if wf_runs:
        return {
            "repo_name": repo_name,
            "conclusion": wf_runs[0]["conclusion"],
            "status": wf_runs[0]["status"],
            "url": wf_runs[0]["url"],
            "name": wf_runs[0]["name"],
            "timestamp_a": wf_runs[0]["run_started_at"],
            "timestamp_z": wf_runs[0]["updated_at"],
            "run_duration": calculate_run_duration(start=wf_runs[0]["run_started_at"], end=wf_runs[0]["updated_at"])
        }

    return {}

def get_workflows_and_statuses(repos):
    """Get workflows and latest run statuses for a list of repositories."""
    all_workflows = []
    for repo in repos:
        workflows = get_workflows(repo)

        for workflow in workflows:
            workflow_name = workflow["name"]
            workflow_id = workflow["id"]
            latest_wf_run = get_latest_workflow_run_status(repo, workflow_id)
            if latest_wf_run:
                all_workflows.append(latest_wf_run)

    # pprint(all_workflows)
    return all_workflows

workflows_and_statuses = get_workflows_and_statuses(REPOS)

write_workflow_runs_to_file(workflow_runs=workflows_and_statuses)
