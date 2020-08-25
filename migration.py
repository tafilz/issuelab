import datetime
import requests
import json
import sys
import gitlab

from enum import Enum
from typing import List
from youtrack.connection import Connection as YouTrack


# TODO
class GitLabPlan(Enum):
    FREE_CORE = 0
    BRONZE_STARTER = 1
    SILVER_PREMIUM = 2
    GOLD_ULTIMATE = 3


class GitLabProject:
    def __init__(self, host: str, project_id: int, token: str):
        self._instance = gitlab.Gitlab(host, private_token=token)
        self.project = self._instance.projects.get(project_id)


class YouTrackProject:
    def __init__(self, host: str, project_id: str, token: str):
        self._instance = YouTrack(host, token=token)
        self.issues = self._instance.getAllIssues(project_id)


class YouTrackMapper:
    def __init__(self, user_names: dict = None, user_ids: dict = None):
        self.user_names = user_names
        if self.user_names is None:
            with open("user_map_name.json") as file:
                self.user_names = json.load(file)

        self.user_ids = user_ids
        if self.user_ids is None:
            with open("user_map_id.json") as file:
                self.user_ids = json.load(file)

    def get_gitlab_id(self, yt_username: str):
        return self.user_ids[yt_username]

    def get_gitlab_username(self, yt_username: str):
        return self.user_names[yt_username]

    @staticmethod
    def minutes_to_human_readable(minutes):
        minutes = int(minutes)
        if minutes > 60:
            time = float(minutes) / 60.0
            time_hours = int(time)
            time_minutes = int((time - time_hours) * 60)
            return f"{time_hours}h{time_minutes}m"
        else:
            return f"{minutes}m"

    @staticmethod
    def get_sprint(sprints):
        """
        Sprint name must be 'Sprint X'
        Returns the highest sprint
        """
        if type(sprints) == str:
            sprints = [sprints]

        # get highest sprint number
        values = []
        for sprint in sprints:
            values.append(int(sprint.replace("Sprint ", "")))

        return f"Sprint {max(values)}"

    @staticmethod
    def get_iso_timestamp(timestamp: str):
        return datetime.datetime.utcfromtimestamp(int(timestamp) / 1000).isoformat()


class AttachmentMap:
    def __init__(self, name, gitlab_file):
        self.name = name
        self.gitlab_file = gitlab_file
        self.replaced = False


class YouTrackToGitLab:
    def __init__(self, gitlab: GitLabProject, youtrack: YouTrackProject, mapper: YouTrackMapper):
        self.gitlab = gitlab
        self.youtrack = youtrack
        self.plan = GitLabPlan.FREE_CORE
        self.mapper = mapper

    def migrate(self, plan: GitLabPlan = GitLabPlan.FREE_CORE):
        counter = 1
        for issue in self.youtrack.issues:
            # Epic unsupported
            if issue.Type == "Epic":
                print(
                    f"[{counter}/{len(self.youtrack.issues)}] Migrating issue {issue.id} -> #{iid}")
                print(f"\t--SKIPPED (unsupported)")
                counter += 1
                continue

            # GitLab User
            reporter = issue.getReporter()
            gitlab_user = self.mapper.get_gitlab_username(reporter.login)

            # Issue id
            iid = int(issue.id[3:])

            print(
                f"[{counter}/{len(self.youtrack.issues)}] Migrating issue {issue.id} -> #{iid}")
            print(f"\t--Author '{reporter.login}' -> {gitlab_user}")

            print("\t--Uploading attachments")
            # Upload attachments
            attachments = self.upload_attachments(issue)

            print("\t--Converting description:")
            # Convert description text
            if hasattr(issue, 'description'):
                description = issue.description
                print("\t\tReplace uploads")
                description = self._attachment_markdown_replacer(
                    description, attachments)
                print("\t\tReplace mentions")
                description = self._at_user_replacer(description)
            else:
                description = ""

            # Milestone
            milestone = self.get_milestone(
                issue.Sprints) if hasattr(issue, 'Sprints') else -1
            if milestone != -1:
                print(
                    f"\t--Using milestone '{self.gitlab.project.milestones.get(milestone).title}' for '{issue.Sprints}'")

            # Create GitLab issue
            new_gitlab_issue = {
                'title': issue.summary,
                'description': description,
                'created_at': self.mapper.get_iso_timestamp(issue.created),
                'iid': iid,
                'assignee_ids': self._get_assignees(issue),
                'milestone_id': milestone
            }

            print("\t--Add issue to gitlab:")
            print(f"\t\tCreate {iid}")
            gl_issue = self.gitlab.project.issues.create(
                new_gitlab_issue, sudo=gitlab_user)

            # Data after creation
            if issue.tags:
                gl_issue.labels = issue.tags
                print(f"\t\tAdd tags {gl_issue.labels}")

            # Time tracking
            if hasattr(issue, 'Estimation'):
                print(f"\t\tAdd estimation {issue.Estimation}m")
                gl_issue.time_estimate(
                    self.mapper.minutes_to_human_readable(issue.Estimation))

            if hasattr(issue, 'Spent time'):
                print(f"\t\tAdd spent time {getattr(issue, 'Spent time')}m")
                gl_issue.add_spent_time(
                    self.mapper.minutes_to_human_readable(getattr(issue, 'Spent time')))

            # Add comments
            print("\t--Add comments")
            self.add_comments(gl_issue, issue, attachments)

            # Issue status (en, de)
            closed = [
                'closed', 'done', 'duplicate',
                'geschlossen', 'erledigt', 'duplikat' ]
            if issue.State.lower() in closed:
                gl_issue.state_event = "close"

            # Add attachments leftover into description
            print("\t--Add leftover attachments to description")
            gl_issue.description = self._append_attachments_to_description(
                gl_issue.description, attachments)
            gl_issue.save(sudo=gitlab_user)
            print("\t--DONE")
            counter += 1

        print("DONE")

    def clean_issue_system(self, milestones=False):
        print("Purging issue board... (may take a while)")
        # issues (20 at a time)
        for x in range(0, 1000):
            if len(self.gitlab.project.issues.list()) == 0:
                break
            for issue in self.gitlab.project.issues.list():
                issue.delete()

        # milestones
        if milestones:
            for milestone in self.gitlab.project.milestones.list():
                milestone.delete()

    def add_comments(self, gl_issue, yt_issue, attachments: List[AttachmentMap]):
        comments = yt_issue.getComments()

        for comment in comments:
            gitlab_user = self.mapper.get_gitlab_username(comment.author)

            if hasattr(comment, 'text'):
                text = comment.text
                text = self._attachment_markdown_replacer(text, attachments)
                text = self._at_user_replacer(text)
            else:
                text = ""

            if text == '':
                text = '(attachment comment)'

            gitlab_note = {
                'issue_iid': gl_issue.iid,
                'body': text,
                'created_at': datetime.datetime.utcfromtimestamp(int(comment.created) / 1000).isoformat(),
            }

            gl_issue.notes.create(gitlab_note, sudo=gitlab_user)

    def get_milestone(self, sprints):
        sprint = self.mapper.get_sprint(sprints)

        for milestone in self.gitlab.project.milestones.list():
            if sprint == milestone.title:
                return milestone.id

        # create if not existent
        new_milestone = self.gitlab.project.milestones.create(
            {'title': sprint})
        return new_milestone.id

    def upload_attachments(self, issue) -> List[AttachmentMap]:
        attachments = []
        for attachment in issue.getAttachments():
            filename = attachment.name
            url = attachment.url
            headers = self.youtrack._instance.headers

            r = requests.get(url, headers=headers, allow_redirects=True)
            with open(f"attachments/{filename}", "wb") as f:
                f.write(r.content)

            uploaded_file = self.gitlab.project.upload(
                filename, filepath=f"attachments/{filename}")
            attachments.append(AttachmentMap(filename, uploaded_file))

        return attachments

    def _get_assignees(self, issue):
        try:
            assignees = issue.getAssignee()
            if isinstance(assignees, list):
                ids = []
                for assignee in assignees:
                    gitlab_id = self.mapper.get_gitlab_id(assignee.login)
                    ids.append(gitlab_id)

                return ids

            else:
                return [self.mapper.get_gitlab_id(assignees.login)]
        except:
            return []

    def _attachment_markdown_replacer(self, text: str, attachments: List[AttachmentMap]):
        for attachment in attachments:
            if attachment.name in text:
                text.replace(attachment.name, attachment.gitlab_file['url'])
                attachment.replaced = True

        return text

    def _append_attachments_to_description(self, text: str, attachments: List[AttachmentMap]):
        left_over = []
        for attachment in attachments:
            if not attachment.replaced:
                left_over.append(attachment)

        if len(left_over) > 0:
            if text is None:
                text = ""
            text += "\n# Attachments\n"
            for attachment in left_over:
                text += f"* {attachment.gitlab_file['markdown']}\n"

        return text

    def _at_user_replacer(self, text: str):
        for name in self.mapper.user_names:
            if name in text:
                text = text.replace(
                    name, self.mapper.get_gitlab_username(name))

        return text


# Load environment
with open("environment.json") as file:
    env = json.load(file)

GITLAB_HOST = env['gitlab']['host']
GITLAB_PROJECT_ID = env['gitlab']['project_id']
GITLAB_TOKEN = env['gitlab']['token']

YOUTRACK_HOST = env['youtrack']['host']
YOUTRACK_PROJECT_ID = env['youtrack']['project_id']
YOUTRACK_TOKEN = env['youtrack']['token']

gl_project = GitLabProject(GITLAB_HOST, GITLAB_PROJECT_ID, GITLAB_TOKEN)
yt_project = YouTrackProject(
    YOUTRACK_HOST, YOUTRACK_PROJECT_ID, YOUTRACK_TOKEN)
yt_mapper = YouTrackMapper()

instance = YouTrackToGitLab(gl_project, yt_project, yt_mapper)
instance.clean_issue_system()
instance.migrate()
