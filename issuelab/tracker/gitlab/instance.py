import json
import gitlab
import requests

from typing import List

from issuelab.tracker.connector import TargetInstance
from issuelab.base.milestone import Milestone
from issuelab.base.issue import Issue, IssueState
from issuelab.base.helper import get_iso_timestamp, minutes_to_human_readable
from issuelab.base.attachment import Attachment
from issuelab.base.comment import Comment
from issuelab.base.label import Label

class GitLabTarget(TargetInstance):
    def __init__(self, host: str, token: str, project_id: str):
        super().__init__(host, token, project_id)
        self.host = host
        self.token = token
        self.project_id = int(project_id)
        self._instance = gitlab.Gitlab(host, private_token=token)
        self.project = self._instance.projects.get(project_id)

        self.reference_prefix = None
        
    def push_milestone(self, milestone: Milestone):
        new_gl_milestone = {
                'title': milestone.title,
                'description': milestone.description,
                'due_date': get_iso_timestamp(milestone.due_date) if milestone.due_date else None,
                'start_date': get_iso_timestamp(milestone.start_date) if milestone.start_date else None
            }
        
        new_gl_milestone = {k: v for k, v in new_gl_milestone.items() if v is not None}
        
        gl_milestone = self.project.milestones.create(new_gl_milestone)

        if milestone.start_date and milestone.due_date:
            if milestone.due_date > milestone.start_date:
                gl_milestone.state_event = 'close'
                gl_milestone.save()
            
        
        
    def push_issue(self, issue: Issue):
        # Create GitLab issue
        new_gitlab_issue = {
            'title': issue.title,
            'description': issue.description,
            'created_at': get_iso_timestamp(issue.created_at),
            'iid': issue.id
        }

        # Push issue attachments and append to issue text
        new_gitlab_issue['description'] += self.push_attachments(issue)
                
        # Assignees
        if issue.assignees:
            if issue.author in issue.assignees:
                gl_user = self._instance.users.list(search=issue.author.username)[0]
                new_gitlab_issue['assignee_ids'] = [ gl_user.id ]
            else:
                gl_user = self._instance.users.list(search=issue.assignees[0].username)[0]
                new_gitlab_issue['assignee_ids'] = [ gl_user.id ]
              
        # Sprint / Milestone
        if issue.sprint:
            milestone = self.project.milestones.list(title=issue.sprint)
            if milestone:
                new_gitlab_issue['milestone_id'] = milestone[0].id

               
        # Create issue
        new_gitlab_issue['description'] = self.fix_references(new_gitlab_issue['description'])
        gl_issue = self.project.issues.create(new_gitlab_issue, sudo=issue.author.username)

        # After issue creation
        # State
        if issue.state == IssueState.CLOSED:
            gl_issue.state_event = 'close'
            gl_issue.save(sudo=issue.author.username)
        elif issue.state == IssueState.LOCKED:
            gl_issue.discussion_locked = True
            gl_issue.save(sudo=issue.author.username)
        # Time Tracking
        if issue.estimation:
            gl_issue.time_estimate(minutes_to_human_readable(issue.estimation))
        if issue.time_spent:
            gl_issue.add_spent_time(minutes_to_human_readable(issue.time_spent))
            gl_issue.save(sudo=issue.author.username)
        # Labels
        if issue.labels:
            labels = []
            for label in issue.labels:
                labels.append(self.push_label(label))

            gl_issue.labels = labels
            gl_issue.save(sudo=issue.author.username)



        # Comments
        self.push_comments(gl_issue, issue)
        
        
    def push_attachments(self, issue: Issue):
        # push attachment
        text = ""
        if issue.attachments:
            text = "\n## Attachments\n"
            for attachment in issue.attachments:
                gitlab_file = self.project.upload(attachment.filename, filepath=attachment.url)
                text += f"* {gitlab_file['markdown']}\n"

        return text
    
    def push_comments(self, gl_issue, issue: Issue):
        # push attachments
        
        for comment in issue.comments:
            text = ""
            if comment.attachments:
                text = "\n## Attachments\n"
                for attachment in comment.attachments:
                    gitlab_file = self.project.upload(attachment.filename, filepath=attachment.url)
                    text += f"* {gitlab_file['markdown']}\n"
        
            # alter comment
            comment.text += text
        
            if comment.text == "":
                comment.text = "Comment deleted"

            # push comment
            comment.text = self.fix_references(comment.text)
            gitlab_note = {
                    'body': comment.text,
                    'created_at': get_iso_timestamp(comment.created_at),
            }
            gl_issue.notes.create(gitlab_note, sudo=comment.author.username)

       
    
    def push_label(self, label: Label):
        # check if label exists -> skip
        tags = self.project.labels.list()
        tags = [label.name for label in tags]
        for tag in tags:
            if label.name == tag:
                return tag
        
        # push label
        new_label = {
            'name': label.name,
            'color': label.color_hex
        }
        self.project.labels.create(new_label)


        return label.name

    def set_reference_prefix(self, prefix: str):
        self.reference_prefix = prefix

    def fix_references(self, text:str):
        if self.reference_prefix:
            return text.replace(issue_tag, "#")
        else:
            return text

        