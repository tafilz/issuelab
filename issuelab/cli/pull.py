import os
import json
import shutil
from pathlib import Path

from issuelab.project import ProjectConnection, get_project_file, issue_path, milestone_path, env_file_path, user_map_path
from issuelab.tracker.youtrack import YouTrackSource
from issuelab.tracker.youtrack.entities import YouTrackIssue
from issuelab.tracker.youtrack.converter import sprint_to_base, issue_to_base
from issuelab.base.user import User
from issuelab.base.issue import extract_users


def pull_command(args):
    project = get_project_file(env_file_path)

    clear_milestone_dir()
    pull_youtrack(project.source)
    
def clear_milestone_dir():
    if os.path.exists(milestone_path):
        shutil.rmtree(milestone_path)
        os.mkdir(milestone_path)

def pull_youtrack(source: ProjectConnection):
    users = []
    
    youtrack = YouTrackSource(source.host, source.token, source.project_id, source.agile_id)
    
    # Milestones / Sprints
    sprints = youtrack.get_all_sprints()
    for sprint in sprints:
        milestone = sprint_to_base(sprint)
        with open(milestone_path / f"{milestone.title}.json", 'w', encoding="utf8") as save_file:
            json.dump(milestone.dict(), save_file, indent=4, ensure_ascii=False)
    
    # Issues
    issues = youtrack.get_all_issues()
    shutil.rmtree(issue_path, ignore_errors=True)
    os.mkdir(issue_path)
    for issue in issues:
        issue = issue_to_base(issue)

        users.extend(extract_users(issue))
        
        tmp_path = issue_path / str(issue.id)
        os.mkdir(tmp_path)

        ## Attachments
        for attachment in issue.attachments:
            with open(tmp_path / attachment.filename , "wb") as attachment_file:
                data = youtrack.download_attachment(attachment)
                attachment_file.write(data)
                attachment.url = str(tmp_path / attachment.filename)
        for comment in issue.comments:
            for number, attachment in enumerate(comment.attachments, start=1):
                file_path = tmp_path / f"{number}-{attachment.filename}"
                with open(file_path, "wb") as attachment_file:
                    data = youtrack.download_attachment(attachment)
                    attachment_file.write(data)
                    attachment.url = str(file_path)


        ## Issue data file
        with open(tmp_path / "issue.json", "w", encoding="utf8") as save_file:
            json.dump(issue.dict(), save_file, indent=4, ensure_ascii=False)

        

    
        
  
    generate_user_map_file(users)
        
def generate_user_map_file(users):
    # remove duplicates
    users = set(users)
    user_map = {}
    for user in users:
        user_map[user.username] = user.username
    
    with open(user_map_path, 'w', encoding="utf8") as save_file:
        json.dump(user_map, save_file, indent=4, ensure_ascii=False)
        