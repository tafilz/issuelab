from typing import List
from natsort import natsorted

from issuelab.base.milestone import Milestone, MilestoneState
from issuelab.base.issue import Issue, IssueState
from issuelab.base.comment import Comment
from issuelab.base.user import User
from issuelab.base.label import Label
from issuelab.base.attachment import Attachment

from issuelab.tracker.youtrack.entities import *

closed_text = ['Done', 'Duplicate', 'Geschlossen']

def sprint_to_base(sprint: YouTrackSprint) -> Milestone:    
    return Milestone(
        id = int(sprint.id[sprint.id.find('-') + 1:]),
        title = sprint.name,
        description = "" if not sprint.goal else sprint.goal,
        state = MilestoneState.CLOSED if sprint.archived else MilestoneState.ACTIVE,
        start_date = None if not sprint.start else float(sprint.start),
        due_date =  None if not sprint.finish else float(sprint.finish)
    )
    
def issue_to_base(issue: YouTrackIssue) -> Issue:
    comments: List[Comment] = []
    labels: List[Label] = []
    
    # comments
    for comment in issue.comments:
        comments.append(comment_to_base(comment))
        
    # labels
    for label in issue.tags:
        labels.append(label_to_base(label))
        
        
    state = IssueState.OPEN
    estimation = None
    time_spent = None
    sprint = None
    
    assignees: List[User] = []
    
    for field in issue.customFields:
        if field.name == "Priority":
            pass
        elif field.name == "Type":
            pass
        elif field.name == "State":
            state = IssueState.CLOSED if field.value.name in closed_text else IssueState.OPEN
        elif field.name == "Assignee":
            if type(field.value) == list:
                for user in field.value:
                    assignees.append(User(id=-1,
                                          name=user.name,
                                          username=user.login))
            elif field.value.login:
                assignees.append(User(id=-1,
                                      name=field.value.name,
                                      username=field.value.login))
        elif field.name == "Sprints":
            if type(field.value) == list:
                assigned_sprints = []
                for sp in field.value:
                    assigned_sprints.append(sp.name)
                assigned_sprints = natsorted(assigned_sprints)
                sprint = assigned_sprints[-1]
            else:
                sprint = field.value.name
        elif field.name == "Estimation":
            if field.value:
                estimation = field.value.minutes
        elif field.name == "Spent time":
            if field.value:
                time_spent = field.value.minutes
    
    converted_issue = Issue(
        id=int(issue.idReadable[issue.idReadable.find('-') + 1:]),
        title=issue.summary,
        description=issue.description if issue.description else "",
        author=User(
            id=-1,
            name=issue.reporter.fullName,
            username=issue.reporter.login
            ),
        created_at=float(issue.created) if issue.created else 0,
        updated_at=float(issue.updated) if issue.updated else None,
        labels=labels,
        comments=comments,
        
        state=state,
        
        assignees=assignees,
        
        estimation=estimation,
        time_spent=time_spent,
        
        sprint=sprint,

        attachments=[attachment_to_base(attachment) for attachment in issue.attachments]
    )

    deduplicate_attachments(converted_issue)

    return converted_issue
        
def comment_to_base(comment: YoutrackIssueComment):
    
    
    return Comment(author=User(id=-1,
                               name=comment.author.fullName,
                               username=comment.author.login
                               ),
                   text=comment.text if comment.text else "",
                   created_at=float(comment.created) if comment.created else 0.0,
                   attachments=[attachment_to_base(attachment) for attachment in comment.attachments]
                   )
def label_to_base(label: YouTrackIssueTags):
    return Label(name=label.name,
                 description="",
                 color_hex=label.color.background if label.color.background else None
                 )
    
def attachment_to_base(attachment: YouTrackIssueAttachment):
    return Attachment(filename=attachment.name,
                      url=attachment.url)
    
def deduplicate_attachments(issue: Issue):
    for comment in issue.comments:
        for attachment in comment.attachments:
            # compare with issue attachments
            for issue_attachment in issue.attachments:
                if attachment.filename == issue_attachment.filename:
                    issue.attachments.remove(issue_attachment)