import uuid
from langchain_core.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional
import datetime

# Comment Class

class Comment(BaseModel):
    username: str = Field(..., description="The user who made the comment")
    content: str = Field(..., description="The text of the comment")

    class Config:
        orm_mode = True
        extra = 'ignore'

    def __repr__(self) -> str:
        return f"Comment(by: {self.username}, content: '{self.content[:30]}...')"

    def get_details(self) -> dict:
        return {
            "username": self.username,
            "content": self.content
        }

# Commit Class
class Commit(BaseModel):
    commit_id: str = Field(default_factory=lambda: generate_new_id("commit"), description="The unique ID of the commit")
    username: str = Field(..., description="The user who made the commit")
    message: str = Field(..., description="The commit message")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description="The timestamp of the commit")
    code: Optional[str] = None

    class Config:
        orm_mode = True
        extra = 'ignore'

    def get_details(self) -> dict:
        return {
            "commit_id": self.commit_id,
            "username": self.username,
            "message": self.message,
            "timestamp": self.timestamp,
        }

# PR Class

class PR(BaseModel):
    pr_id: str = Field(default_factory=lambda: generate_new_id("pr"), description="The unique ID of the pull request")
    title: str = Field(..., description="The title of the pull request")
    description: str = Field(..., description="The description of the pull request")
    commits: List[Commit] = Field(default_factory=list, description="List of commits in the PR")
    comments: List[Comment] = Field(default_factory=list, description="List of comments on the PR")

    class Config:
        orm_mode = True
        extra = 'ignore'

    def add_commit(self, commit: Commit) -> None:
        """Attach a commit to this PR"""
        self.commits.append(commit)

    def add_comment(self, comment: Comment) -> None:
        """Add a comment to the PR"""
        self.comments.append(comment)

    def get_details(self) -> dict:
        """Get detailed information about the PR"""
        return {
            "pr_id": self.pr_id,
            "title": self.title,
            "description": self.description,
            "commits": [commit.get_details() for commit in self.commits],
            "comments": [comment.get_details() for comment in self.comments],
        }

# Issue Class

class Issue(BaseModel):
    issue_id: str = Field(default_factory=lambda: generate_new_id("issue"), description="Unique identifier for the issue")
    title: str = Field(..., description="Title of the issue")
    description: Optional[str] = Field(default="", description="Detailed description of the issue")
    status: str = Field(default="open", description="Current status of the issue")
    comments: List[Comment] = Field(default_factory=list, description="Comments on the issue")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: Optional[str] = Field(default=None)

    class Config:
        orm_mode = True
        extra = 'ignore'

    def add_comment(self, comment: Comment) -> None:
        """
        Add a comment to the issue and update the timestamp.
        
        Args:
            comment (Comment): The comment to be added
        """
        self.comments.append(comment)
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def close(self) -> None:
        """
        Close the issue by setting its status to 'closed'.
        """
        self.status = "closed"
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # def reopen(self) -> None:
    #     """
    #     Reopen a closed issue by setting its status back to 'open'.
    #     """
    #     self.status = "open"
    #     self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_details(self) -> dict:
        """
        Get a dictionary representation of the issue details.
        
        Returns:
            dict: A dictionary containing the issue's details
        """
        return {
            "issue_id": self.issue_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "comments": [comment.get_details() for comment in self.comments],
        }


####################
# state
issues = {}
pull_requests = {}
commits = []
# List of maintainers (users who can close issues, PRs, and make commits)
maintainers = []


def print_sim_state():
    print("Issues:")
    for issue in issues.values():
        print(issue)
    print("Pull Requests:")
    for pr in pull_requests.values():
        print(pr)
    print("Commits:")
    for commit in commits:
        print(commit)
    print("Maintainers:")
    print(maintainers)


def sim_state_str():
    state_str = "Issues:\n"
    for issue in issues.values():
        state_str += str(issue) + "\n"
    state_str += "Pull Requests:\n"
    for pr in pull_requests.values():
        state_str += str(pr) + "\n"
    state_str += "Commits:\n"
    for commit in commits:
        state_str += str(commit) + "\n"
    state_str += "Maintainers:\n"
    state_str += str(maintainers) + "\n"
    return state_str


####################
# issue tools


def generate_new_id(entity_type: str) -> str:
    """Generate a unique ID for an entity using UUID."""
    unique_id = str(uuid.uuid4())
    return f"{entity_type}-{unique_id}"

# open_issue


@tool
def open_issue(title: str, description: str = "") -> str:
    """
    Opens a new issue in the repository with the given title and description.
    """
    new_issue = Issue(title, description)
    issues[new_issue.issue_id] = new_issue
    return f"Issue #{new_issue.issue_id} created successfully."

# comment_issue


@tool
def comment_issue(issue_id: str, username: str, comment: str) -> str:
    """
    Add a comment to the issue with the given ID.
    """
    issue = issues.get(issue_id)
    if not issue:
        return "Issue not found."
    new_comment = Comment(username, comment)
    issue.add_comment(new_comment)
    return f"Comment added to Issue #{issue_id}."

# close_issue


@tool
def close_issue(issue_id: str, username: str) -> str:
    """
    Close an issue if the user is a maintainer.
    """
    if username not in maintainers:
        return "Only maintainers can close issues."
    issue = issues.get(issue_id)
    if not issue:
        return "Issue not found."
    issue.close()
    return f"Issue #{issue_id} closed successfully."

# read_issue


@tool
def read_issue(issue_id: str) -> dict:
    """
    Return details of a specific issue.
    """
    issue = issues.get(issue_id)
    if not issue:
        return "Issue not found."
    return issue.get_details()


####################
# pull request tools

# open_pr
@tool
def open_pr(title: str, description: str = "") -> str:
    """
    Open a new pull request.
    """
    new_pr = PR(title, description)
    pull_requests[new_pr.pr_id] = new_pr
    return f"PR #{new_pr.pr_id} created successfully."

# comment_pr


@tool
def comment_pr(pr_id: str, username: str, comment: str) -> str:
    """
    Add a comment to the pull request.
    """
    pr = pull_requests.get(pr_id)
    if not pr:
        return "Pull request not found."
    new_comment = Comment(username, comment)
    pr.add_comment(new_comment)
    return f"Comment added to PR #{pr_id}."

# close_pr


@tool
def close_pr(pr_id: str, username: str) -> str:
    """
    Close a pull request if the user is a maintainer.
    """
    if username not in maintainers:
        return "Only maintainers can close pull requests."
    pr = pull_requests.get(pr_id)
    if not pr:
        return "Pull request not found."
    pr.status = "closed"
    return f"PR #{pr_id} closed successfully."

# read_pr


@tool
def read_pr(pr_id: str) -> dict:
    """
    Return details of a specific pull request.
    """
    pr = pull_requests.get(pr_id)
    if not pr:
        return "Pull request not found."
    return pr.get_details()


####################
# commit tools

# commit
@tool
def commit(username: str, message: str, timestamp: Optional[str] = None) -> str:
    """
    Make a commit to the repository if the user is a maintainer.
    """
    if username not in maintainers:
        return "Only maintainers can make commits."
    new_commit = Commit(username, message, timestamp)
    commits.append(new_commit)
    return f"Commit #{new_commit.commit_id} created successfully."

# read_commit


@tool
def read_commit(commit_id: str) -> dict:
    """
    Return details of a specific commit.
    """
    commit = next((c for c in commits if c.commit_id == commit_id), None)
    if not commit:
        return "Commit not found."
    return commit.get_details()

####################
# permissions

# set_permissions
# have to be "maintainer", lets maintainers make other maintainers


@tool
def set_permissions(username: str, role: str) -> str:
    """
    Set the permissions for a user (e.g., make them a maintainer).
    """
    if role == "maintainer":
        maintainers.append(username)
        return f"User {username} set as maintainer."
    return f"Invalid role: {role}"

####################
# get information

# read_repo


@tool
def read_repo() -> dict:
    """
    Read the repository information (e.g., all issues, PRs, commits).
    """
    return {
        "issues": [issue.get_details() for issue in issues.values()],
        "pull_requests": [pr.get_details() for pr in pull_requests.values()],
        "commits": [commit.get_details() for commit in commits]
    }

# read_issues

# read_prs

# read_commits

# read_permissions


all_tools = [
    open_issue,
    comment_issue,
    close_issue,
    read_issue,
    open_pr,
    comment_pr,
    close_pr,
    read_pr,
    commit,
    read_commit,
    set_permissions,
    read_repo
]
