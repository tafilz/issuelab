import os
import json

from pathlib import Path
from enum import Enum
from pydantic import BaseModel

from issuelab.project import SupportedTracker, ProjectFile, ProjectConnection, project_path, issue_path, milestone_path


def init_command(args):
    project_name = args.name
    target = args.target
    source = args.source

    project = ProjectFile(
        name=project_name,
        source=ProjectConnection(type=source),
        target=ProjectConnection(type=target)
    )

    if source == target:
        raise Exception("CANT BE THE SAME")


    if not os.path.exists(issue_path):
        os.mkdir(issue_path)
    else:
        os.rmdir(issue_path)
        os.mkdir(issue_path)
        
    if not os.path.exists(milestone_path):
        os.mkdir(milestone_path)
    else:
        os.rmdir(milestone_path)
        os.mkdir(milestone_path)

    with open(project_path / "project.json", 'w') as save_file:
        json.dump(project.dict(), save_file, indent=4)
