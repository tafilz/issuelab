import os
import json

from pathlib import Path
from pydantic import BaseModel, BaseSettings
from enum import Enum

cwd = Path(os.getcwd())
project_path = cwd
env_file_path = project_path / "project.json"
issue_path = project_path / "issues"
milestone_path = project_path / "milestones"
user_map_path = project_path / "usermap.json"

class SupportedTracker(str, Enum):
    gitlab = 'gitlab'
    youtrack = 'youtrack'

    def __str__(self):
        return self.value


class ProjectConnection(BaseModel):
    type: SupportedTracker
    host: str = ""
    token: str = ""
    project_id: str = ""
    agile_id: str = None


class ProjectFile(BaseSettings):
    name: str = "UNNAMED MIGRATION PROJECT"
    source: ProjectConnection
    target: ProjectConnection

    class Config:
        case_sensitive = True


    

def get_project_file(path) -> ProjectFile:
    path = str(path)
    if os.path.isfile(path):
        with open(path, 'r') as read_file:
            data = json.load(read_file)
            config = ProjectFile.parse_obj(data)
    else:
        raise Exception("No project found!")

    return config
