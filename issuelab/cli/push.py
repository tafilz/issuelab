import os
import json
import shutil
import re

from pathlib import Path
from typing import List

from issuelab.tracker.gitlab import GitLabTarget
from issuelab.project import ProjectConnection, get_project_file, issue_path, milestone_path, env_file_path, project_path, user_map_path
from issuelab.base.milestone import Milestone, MilestoneState
from issuelab.base.issue import Issue
from issuelab.base.user import User

def push_command(args):
    project = get_project_file(env_file_path)
    
    push_gitlab(project.target, project.source)
    
def push_gitlab(target: ProjectConnection, source: ProjectConnection):
    gitlab = GitLabTarget(target.host, target.token, target.project_id)
    gitlab.set_reference_prefix(f"{source.project_id}-")
    
    # issues (20 at a time)
    for x in range(0, 1000):
        if len(gitlab.project.issues.list()) == 0:
            break
        for issue in gitlab.project.issues.list():
            issue.delete()
            
    for x in range(0, 1000):
        if len(gitlab.project.milestones.list()) == 0:
            break
        for milestone in gitlab.project.milestones.list():
            milestone.delete()
    
    # milestone
    milestone_files = []
    for (dirpath, dirnames, filenames) in os.walk(milestone_path):
        milestone_files.extend(filenames)
        break
    
    for file in milestone_files:
        with open(milestone_path / file) as data:
            milestone = Milestone.parse_obj(json.load(data))

        gitlab.push_milestone(milestone)
    
    # issues
    issue_ids = []
    for (dirpath, dirnames, filenames) in os.walk(issue_path):
        issue_ids.extend(dirnames)
        break
    issue_ids.sort(key=int)
        
    # usermap
    with open(user_map_path) as data:
        usermap = json.load(data) 
    
    

    for num, issue_id in enumerate(issue_ids, start=1):
        print(f"Pushing {num}/{len(issue_ids)}\n")
        with open(issue_path / issue_id / "issue.json") as data:
            issue = Issue.parse_obj(json.load(data))
            
        # replace 
        issue = replace_user(issue, usermap)
        
        gitlab.push_issue(issue)
        
        
def replace_user(issue: Issue, usermap):
    data = json.dumps(issue.dict(), ensure_ascii=False)
    
    for user in usermap:
        data = data.replace(user, usermap[user])
        
    return Issue.parse_obj(json.loads(data))