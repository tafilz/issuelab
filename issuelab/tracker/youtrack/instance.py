import json
import requests

from typing import List
from youtrack.connection import Connection as YouTrack

from issuelab.tracker.youtrack.entities import *
from issuelab.tracker.connector import SourceInstance, TargetInstance

from issuelab.base.attachment import Attachment


class YouTrackSource(SourceInstance):
    def __init__(self, host: str, token: str, project_id: str, agile_id: str):
        super().__init__(host, token, project_id)
        self.agile_id = agile_id
        self._instance = YouTrack(host, token=token)
        
    def get_all_issues(self) -> List[YouTrackIssue]:
        response, content = self._instance._req('GET',
                                      self._instance.url + f'/api/admin/projects/{self.project_id}/?fields=issues({YouTrackIssue.get_query_fields()})',
                                      ignoreStatus=404,
                                      content_type='application/json')
        
        issues: List[YouTrackIssue] = []
        
        issues_json = json.loads(content)['issues']
        
        for issue in issues_json:
            issues.append(YouTrackIssue.parse_obj(issue))
            
        return issues

        

    def get_all_sprints(self) -> List[YouTrackSprint]:
        response, content = self._instance._req('GET',
                                      self._instance.url + f'/api/agiles/{self.agile_id}?fields=sprints({YouTrackSprint.get_query_fields()})',
                                      ignoreStatus=404,
                                      content_type='application/json')
        
        sprints = json.loads(content)['sprints']
        sprint_objects = []
        for sprint in sprints:
            sprint_objects.append(YouTrackSprint.parse_obj(sprint))
            
        return sprint_objects

    def download_attachment(self, attachment: Attachment):
        url = self._instance.url + attachment.url
        headers = self._instance.headers
            
        r = requests.get(url, headers=headers, allow_redirects=True)

        return r.content


class YouTrackTarget(TargetInstance):
    pass



