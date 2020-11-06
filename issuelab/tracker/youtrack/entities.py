from pydantic import BaseModel
from typing import List, Union

"""
WARNING: YOU CAN LOOP YOURSELF HERE with {get_query_fields}
"""


class YouTrackSprint(BaseModel):
    """
    https://www.jetbrains.com/help/youtrack/standalone/api-entity-Sprint.html
    """
    # agile
    id: str
    name: str = None
    goal: str = None
    start: int = None
    finish: int = None
    archived: bool
    isDefault: bool
    # issues
    # unresolvedIssuesCount
    unresolvedIssuesCount: int
    
    @staticmethod
    def get_query_fields():
        return "id," \
            "name," \
            "goal," \
            "start," \
            "finish," \
            "archived," \
            "isDefault," \
            "unresolvedIssuesCount"
    
class YouTrackUser(BaseModel):
    """
    https://www.jetbrains.com/help/youtrack/standalone/api-entity-User.html
    """
    
    login: str = None
    fullName: str = None
    email: str = None
    jabberAccountName: str = None
    ringId: str = None
    guest: bool
    online: bool
    banned: bool
    avatarUrl: str
    
    @staticmethod
    def get_query_fields():
        return "login," \
            "fullName," \
            "email," \
            "jabberAccountName," \
            "ringId," \
            "guest," \
            "online," \
            "banned," \
            "avatarUrl"
    
class YouTrackIssueAttachment(BaseModel):
    """
    https://www.jetbrains.com/help/youtrack/standalone/api-entity-IssueAttachment.html
    """
    name: str = None
    author: YouTrackUser = None
    created: int
    updated: int
    size: int
    extension: str = None
    charset: str = None
    mimeType: str = None
    metaData: str = None
    draft: bool
    removed: bool
    # base64Content: str = None
    url: str = None
    # visibility
    # issue
    # comment
    thumbnailurl: str = None
    
    @staticmethod
    def get_query_fields():
        return "name," \
            f"author({YouTrackUser.get_query_fields()})," \
            "created," \
            "updated," \
            "size," \
            "extension," \
            "charset," \
            "mimeType," \
            "metaData," \
            "draft," \
            "removed," \
            "url"
    
class YoutrackIssueComment(BaseModel):
    """
    https://www.jetbrains.com/help/youtrack/standalone/api-entity-IssueComment.html
    """
    id: str
    text: str = None
    usesMarkdown: bool
    # textPreview: str
    created: int = None
    updated: int = None
    author: YouTrackUser = None
    # issue: YouTrackIssue = None
    attachments: List[YouTrackIssueAttachment]
    # visiblity
    deleted: bool
    
    @staticmethod
    def get_query_fields():
        return "id," \
            "text," \
            "usesMarkdown," \
            "created," \
            "updated," \
            f"author({YouTrackUser.get_query_fields()})," \
            f"attachments({YouTrackIssueAttachment.get_query_fields()})," \
            "deleted"
    
class YouTrackFieldStyle(BaseModel):
    """
    https://www.jetbrains.com/help/youtrack/standalone/api-entity-FieldStyle.html
    """
    background: str = None
    foreground: str = None
    
    @staticmethod
    def get_query_fields():
        return f"background,foreground"

class YouTrackIssueTags(BaseModel):
    """
    https://www.jetbrains.com/help/youtrack/standalone/api-entity-IssueTag.html
    """
    # issues
    color: YouTrackFieldStyle
    untagOnResolve: bool
    owner: YouTrackUser = None
    # visibleFor
    # updateableBy
    name: str = None
    
    @staticmethod
    def get_query_fields():
        return f"color({YouTrackFieldStyle.get_query_fields()})," \
            "untagOnResolve," \
            f"owner({YouTrackUser.get_query_fields()})," \
            "name"


class YouTrackIssueCustomFieldValues(BaseModel):
    id: str = None
    name: str = None
    login: str = None
    minutes: int = None
    
    @staticmethod
    def get_query_fields():
        return "id," \
            "name," \
            "login," \
            "minutes"

class YouTrackIssueCustomField(BaseModel):
    """
    https://www.jetbrains.com/help/youtrack/standalone/api-entity-IssueCustomField.html
    NOTE: Merged values, too many types to separate from
    NOTE: Only needed values
    """
    name: str
    value: Union[YouTrackIssueCustomFieldValues, List[YouTrackIssueCustomFieldValues]] = None
    
    @staticmethod
    def get_query_fields():
        return "name," \
            f"value({YouTrackIssueCustomFieldValues.get_query_fields()})"
    
    
class YouTrackIssue(BaseModel):
    """
    https://www.jetbrains.com/help/youtrack/standalone/api-entity-Issue.html
    """
    idReadable: str
    created: int = None
    updated: int = None
    resolved: int = None
    numberInProject: int
    # project
    summary: str = None
    description: str = None
    usesMarkdown: bool
    # wikifiedDescription
    reporter: YouTrackUser = None
    updater: YouTrackUser = None
    draftOwner: YouTrackUser = None
    isDraft: bool
    # visibility
    votes: int
    comments: List[YoutrackIssueComment]
    commentsCount: int
    tags: List[YouTrackIssueTags]
    # links
    # externalIssue
    customFields: List[YouTrackIssueCustomField] = []
    attachments: List[YouTrackIssueAttachment]
    # subtasks
    # parent
    
    @staticmethod
    def get_query_fields():
        return "idReadable," \
            "created," \
            "updated," \
            "resolved," \
            "numberInProject," \
            "summary," \
            "description," \
            "usesMarkdown," \
            f"reporter({YouTrackUser.get_query_fields()})," \
            f"updater({YouTrackUser.get_query_fields()})," \
            f"draftOwner({YouTrackUser.get_query_fields()})," \
            "isDraft," \
            "votes," \
            f"comments({YoutrackIssueComment.get_query_fields()})," \
            "commentsCount," \
            f"tags({YouTrackIssueTags.get_query_fields()})," \
            f"customFields({YouTrackIssueCustomField.get_query_fields()})," \
            f"attachments({YouTrackIssueAttachment.get_query_fields()})"