import uuid
from langchain_core.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import json
import os


def generate_new_id(entity_type: str) -> str:
    """Generate a unique ID for an entity using UUID."""
    unique_id = str(uuid.uuid4())
    return f"{entity_type}-{unique_id}"

# Comment Class


class Comment(BaseModel):
    username: str = Field(..., description="The user who made the comment")
    content: str = Field(..., description="The text of the comment")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"), description="The timestamp of the comment")

    class Config:
        orm_mode = True
        extra = 'ignore'

    def __repr__(self) -> str:
        return f"Comment(by: {self.username}, content: '{self.content[:30]}...')"

    def get_details(self) -> dict:
        return {
            "username": self.username,
            "content": self.content,
            "timestamp": self.timestamp
        }

# Commit Class


class Commit(BaseModel):
    commit_id: str = Field(default_factory=lambda: generate_new_id(
        "commit"), description="The unique ID of the commit")
    username: str = Field(..., description="The user who made the commit")
    message: str = Field(..., description="The commit message")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"), description="The timestamp of the commit")
    code: str = Field(..., description="The code to be committed")
    file_name: str = Field(...,
                           description="The name of the file to be modified or created")

    class Config:
        orm_mode = True
        extra = 'ignore'

    def get_details(self) -> dict:
        return {
            "commit_id": self.commit_id,
            "username": self.username,
            "message": self.message,
            "timestamp": self.timestamp,
            "file_name": self.file_name
        }


# PR Class


class PR(BaseModel):
    pr_id: str = Field(default_factory=lambda: generate_new_id(
        "pr"), description="The unique ID of the pull request")
    title: str = Field(..., description="The title of the pull request")
    description: str = Field(...,
                             description="The description of the pull request")
    opened_by: str = Field(..., description="The user who opened the PR")
    status: str = Field(
        default="open", description="Current status of the PR (open, approved, closed)")
    commits: List[Commit] = Field(
        default_factory=list, description="List of commits in the PR")
    comments: List[Comment] = Field(
        default_factory=list, description="List of comments on the PR")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"), description="The timestamp when the PR was opened")

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
            "opened_by": self.opened_by,
            "status": self.status,
            "timestamp": self.timestamp,
            "commits": [commit.get_details() for commit in self.commits],
            "comments": [comment.get_details() for comment in self.comments],
        }

# SimulationState Class


class SimulationState(BaseModel):
    pull_requests: Dict[str, PR] = Field(default_factory=dict)
    maintainers: List[str] = Field(default_factory=list)
    files: Dict[str, str] = Field(default_factory=dict)  # filename: code

    # constructor, go through /fake_library and add all files to the state
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            for root, dirs, files in os.walk("fake_library"):
                for file in files:
                    with open(os.path.join(root, file), 'r') as f:
                        self.files[file] = f.read()
        except FileNotFoundError:
            pass

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# Helper functions


def load_state_from_json() -> SimulationState:
    try:
        with open('logs/sim_state.json', 'r') as f:
            json_data = f.read()
        state = SimulationState.parse_raw(json_data)
    except FileNotFoundError:
        state = SimulationState()
    return state


def save_state_to_json(state: SimulationState) -> None:
    # create logs directory if it doesn't exist
    try:
        os.makedirs("logs")
    except FileExistsError:
        pass
    with open('logs/sim_state.json', 'w') as f:
        f.write(state.json())
    with open('logs/sim_state_pretty.json', 'w') as f:
        f.write(json.dumps(json.loads(state.json()), indent=4))


def sim_state_str() -> str:
    state = load_state_from_json()
    return state.json()


def print_sim_state() -> None:
    state = load_state_from_json()
    print(state.json())

####################
# pull request tools

# open_pr


@tool
def open_pr(title: str, description: str, username: str) -> str:
    """
    Open a new pull request. This is also the system for opening issues.
    """
    state = load_state_from_json()
    new_pr = PR(title=title, description=description, opened_by=username)
    state.pull_requests[new_pr.pr_id] = new_pr
    save_state_to_json(state)
    return f"PR #{new_pr.pr_id} created successfully by {username}."

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

# commit_to_pr


@tool
def commit_to_pr(pr_id: str, username: str, message: str, file_name: str, code: str) -> str:
    """
    Add a commit to a pull request.
    """
    state = load_state_from_json()
    pr = state.pull_requests.get(pr_id)
    if not pr:
        return "Pull request not found."
    if pr.status != "open":
        return "Cannot commit to a closed or approved PR."
    new_commit = Commit(username=username, message=message,
                        file_name=file_name, code=code)
    pr.add_commit(new_commit)
    state.pull_requests[pr_id] = pr
    save_state_to_json(state)
    return f"Commit added to PR #{pr_id}."

# approve_pr


@tool
def approve_pr(pr_id: str, username: str) -> str:
    """
    Approve a pull request. Only maintainers can approve PRs. Upon approval, commits are applied.
    """
    state = load_state_from_json()
    if username not in state.maintainers:
        return "Only maintainers can approve pull requests."
    pr = state.pull_requests.get(pr_id)
    if not pr:
        return "Pull request not found."
    if pr.status != "open":
        return "PR is already closed or approved."
    # Apply commits
    for commit in pr.commits:
        state.files[commit.file_name] = commit.code
    pr.status = "approved"
    state.pull_requests[pr_id] = pr
    save_state_to_json(state)
    return f"PR #{pr_id} approved and commits applied."

# close_pr


@tool
def close_pr(pr_id: str, username: str) -> str:
    """
    Close a pull request without approving it. Only maintainers can close PRs.
    """
    state = load_state_from_json()
    if username not in state.maintainers:
        return "Only maintainers can close pull requests."
    pr = state.pull_requests.get(pr_id)
    if not pr:
        return "Pull request not found."
    if pr.status != "open":
        return "PR is already closed or approved."
    pr.status = "closed"
    state.pull_requests[pr_id] = pr
    save_state_to_json(state)
    return f"PR #{pr_id} closed without approving."

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

# list_files


@tool
def list_files() -> List[str]:
    """
    List all files in the fake library.
    """
    state = load_state_from_json()
    return list(state.files.keys())

# read_file


@tool
def read_file(file_name: str) -> str:
    """
    Read the contents of a file in the fake library.
    """
    state = load_state_from_json()
    code = state.files.get(file_name)
    if code is None:
        return f"File '{file_name}' does not exist."
    return code

# read_repo


@tool
def read_repo() -> dict:
    """
    Read the repository information (e.g., all PRs, files, maintainers).
    """
    state = load_state_from_json()
    return {
        "pull_requests": [pr.get_details() for pr in state.pull_requests.values()],
        "files": state.files,
        "maintainers": state.maintainers
    }

####################
# helper functions


def has_maintainer(username: str) -> bool:
    state = load_state_from_json()
    return username in state.maintainers


all_tools = [
    open_pr,
    comment_pr,
    commit_to_pr,
    approve_pr,
    close_pr,
    read_pr,
    set_permissions,
    list_files,
    read_file,
    read_repo
]
