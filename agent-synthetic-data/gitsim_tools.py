import uuid
from langchain_core.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import json


def generate_new_id(entity_type: str) -> str:
    """Generate a unique ID for an entity using UUID."""
    unique_id = str(uuid.uuid4())
    return f"{entity_type}-{unique_id}"

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
    commit_id: str = Field(default_factory=lambda: generate_new_id(
        "commit"), description="The unique ID of the commit")
    username: str = Field(..., description="The user who made the commit")
    message: str = Field(..., description="The commit message")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"), description="The timestamp of the commit")
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
    pr_id: str = Field(default_factory=lambda: generate_new_id(
        "pr"), description="The unique ID of the pull request")
    title: str = Field(..., description="The title of the pull request")
    description: str = Field(...,
                             description="The description of the pull request")
    status: str = Field(default="open", description="Current status of the PR")
    commits: List[Commit] = Field(
        default_factory=list, description="List of commits in the PR")
    comments: List[Comment] = Field(
        default_factory=list, description="List of comments on the PR")

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
            "status": self.status,
            "commits": [commit.get_details() for commit in self.commits],
            "comments": [comment.get_details() for comment in self.comments],
        }

# Issue Class


class Issue(BaseModel):
    issue_id: str = Field(default_factory=lambda: generate_new_id(
        "issue"), description="Unique identifier for the issue")
    title: str = Field(..., description="Title of the issue")
    description: Optional[str] = Field(
        default="", description="Detailed description of the issue")
    status: str = Field(
        default="open", description="Current status of the issue")
    comments: List[Comment] = Field(
        default_factory=list, description="Comments on the issue")
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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

# SimulationState Class


class SimulationState(BaseModel):
    issues: Dict[str, Issue] = Field(default_factory=dict)
    pull_requests: Dict[str, PR] = Field(default_factory=dict)
    commits: List[Commit] = Field(default_factory=list)
    maintainers: List[str] = Field(default_factory=list)

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# Helper functions


def load_state_from_json() -> SimulationState:
    try:
        with open('sim_state.json', 'r') as f:
            json_data = f.read()
        state = SimulationState.parse_raw(json_data)
    except FileNotFoundError:
        state = SimulationState()
    return state


def save_state_to_json(state: SimulationState) -> None:
    with open('sim_state.json', 'w') as f:
        f.write(state.json())


def sim_state_str() -> str:
    state = load_state_from_json()
    return state.json()


def print_sim_state() -> None:
    state = load_state_from_json()
    print(state.json())

####################
# issue tools

# open_issue


@tool
def open_issue(title: str, description: str = "") -> str:
    """
    Opens a new issue in the repository with the given title and description.
    """
    state = load_state_from_json()
    new_issue = Issue(title=title, description=description)
    state.issues[new_issue.issue_id] = new_issue
    save_state_to_json(state)
    return f"Issue #{new_issue.issue_id} created successfully."

# comment_issue


@tool
def comment_issue(issue_id: str, username: str, comment: str) -> str:
    """
    Add a comment to the issue with the given ID.
    """
    state = load_state_from_json()
    issue = state.issues.get(issue_id)
    if not issue:
        return "Issue not found."
    new_comment = Comment(username=username, content=comment)
    issue.add_comment(new_comment)
    state.issues[issue_id] = issue
    save_state_to_json(state)
    return f"Comment added to Issue #{issue_id}."

# close_issue


@tool
def close_issue(issue_id: str, username: str) -> str:
    """
    Close an issue if the user is a maintainer.
    """
    state = load_state_from_json()
    if username not in state.maintainers:
        return "Only maintainers can close issues."
    issue = state.issues.get(issue_id)
    if not issue:
        return "Issue not found."
    issue.close()
    state.issues[issue_id] = issue
    save_state_to_json(state)
    return f"Issue #{issue_id} closed successfully."

# read_issue


@tool
def read_issue(issue_id: str) -> dict:
    """
    Return details of a specific issue.
    """
    state = load_state_from_json()
    issue = state.issues.get(issue_id)
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
    state = load_state_from_json()
    new_pr = PR(title=title, description=description)
    state.pull_requests[new_pr.pr_id] = new_pr
    save_state_to_json(state)
    return f"PR #{new_pr.pr_id} created successfully."

# comment_pr


@tool
def comment_pr(pr_id: str, username: str, comment: str) -> str:
    """
    Add a comment to the pull request.
    """
    state = load_state_from_json()
    pr = state.pull_requests.get(pr_id)
    if not pr:
        return "Pull request not found."
    new_comment = Comment(username=username, content=comment)
    pr.add_comment(new_comment)
    state.pull_requests[pr_id] = pr
    save_state_to_json(state)
    return f"Comment added to PR #{pr_id}."

# close_pr


@tool
def close_pr(pr_id: str, username: str) -> str:
    """
    Close a pull request if the user is a maintainer.
    """
    state = load_state_from_json()
    if username not in state.maintainers:
        return "Only maintainers can close pull requests."
    pr = state.pull_requests.get(pr_id)
    if not pr:
        return "Pull request not found."
    pr.status = "closed"
    state.pull_requests[pr_id] = pr
    save_state_to_json(state)
    return f"PR #{pr_id} closed successfully."

# read_pr


@tool
def read_pr(pr_id: str) -> dict:
    """
    Return details of a specific pull request.
    """
    state = load_state_from_json()
    pr = state.pull_requests.get(pr_id)
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
    state = load_state_from_json()
    if username not in state.maintainers:
        return "Only maintainers can make commits."
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_commit = Commit(username=username, message=message,
                        timestamp=timestamp)
    state.commits.append(new_commit)
    save_state_to_json(state)
    return f"Commit #{new_commit.commit_id} created successfully."

# read_commit


@tool
def read_commit(commit_id: str) -> dict:
    """
    Return details of a specific commit.
    """
    state = load_state_from_json()
    commit = next((c for c in state.commits if c.commit_id == commit_id), None)
    if not commit:
        return "Commit not found."
    return commit.get_details()

####################
# permissions

# set_permissions


@tool
def set_permissions(username: str, role: str) -> str:
    """
    Set the permissions for a user (e.g., make them a maintainer).
    """
    state = load_state_from_json()
    if role == "maintainer":
        if username not in state.maintainers:
            state.maintainers.append(username)
            save_state_to_json(state)
            return f"User {username} set as maintainer."
        else:
            return f"User {username} is already a maintainer."
    return f"Invalid role: {role}"

####################
# get information

# read_repo


@tool
def read_repo() -> dict:
    """
    Read the repository information (e.g., all issues, PRs, commits).
    """
    state = load_state_from_json()
    return {
        "issues": [issue.get_details() for issue in state.issues.values()],
        "pull_requests": [pr.get_details() for pr in state.pull_requests.values()],
        "commits": [commit.get_details() for commit in state.commits],
        "maintainers": state.maintainers
    }


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
