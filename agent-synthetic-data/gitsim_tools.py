import uuid
from langchain_core.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional
import datetime

# Comment Class


class Comment(BaseModel):
    username: str = Field(description="The user who made the comment")
    content: str = Field(description="The text of the comment")

    def __init__(self, username: str, content: str):
        self.username = username  # The user who made the comment
        self.content = content    # The text of the comment

    def __repr__(self):
        return f"Comment(by: {self.username}, content: '{self.content[:30]}...')"

    def get_details(self):
        return {
            "username": self.username,
            "content": self.content
        }


# Commit Class
class Commit(BaseModel):
    commit_id: str = Field(description="The unique ID of the commit")
    username: str = Field(description="The user who made the commit")
    message: str = Field(description="The commit message")
    timestamp: str = Field(description="The timestamp of the commit")

    def __init__(self, username: str, message: str, timestamp: Optional[str] = None):
        self.commit_id = generate_new_id("commit")  # Generate unique commit ID
        self.username = username  # The user who made the commit
        self.message = message    # The commit message
        self.timestamp = timestamp or datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")  # Default to current timestamp
        self.code = None          # Code (if relevant) can be added later

    def get_details(self):
        return {
            "commit_id": self.commit_id,
            "username": self.username,
            "message": self.message,
            "timestamp": self.timestamp,
        }

# PR Class


class PR(BaseModel):
    pr_id: str = Field(description="The unique ID of the pull request")
    title: str = Field(description="The title of the pull request")
    description: str = Field(description="The description of the pull request")
    commits: list = Field(description="List of commits in the PR")
    comments: list = Field(description="List of comments on the PR")

    def __init__(self, title: str, description: str):
        self.pr_id = generate_new_id("pr")  # Unique PR ID
        self.title = title  # Title of the PR
        self.description = description  # Description of the PR
        self.commits = []  # List of Commit objects
        self.comments = []  # List of Comment objects

    def add_commit(self, commit: Commit):
        self.commits.append(commit)  # Attach a commit to this PR

    def add_comment(self, comment: Comment):
        self.comments.append(comment)  # Add a comment to the PR

    def get_details(self):
        return {
            "pr_id": self.pr_id,
            "title": self.title,
            "description": self.description,
            "commits": [commit.get_details() for commit in self.commits],
            "comments": [comment.get_details() for comment in self.comments],
        }


class Issue(BaseModel):
    issue_id: str = Field(description="The unique ID of the issue")
    title: str = Field(description="The title of the issue")
    description: str = Field(description="The description of the issue")
    status: str = Field(description="The status of the issue")
    comments: list = Field(description="List of comments on the issue")

    def __init__(self, title: str, description: str = ""):
        self.issue_id = generate_new_id("issue")  # Generate unique issue ID
        self.title = title
        self.description = description
        self.status = "open"  # Default status is 'open'
        self.comments = []  # List to hold comments on the issue

    def add_comment(self, comment: Comment):
        self.comments.append(comment)

    def close(self):
        self.status = "closed"

    def get_details(self):
        return {
            "issue_id": self.issue_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
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
