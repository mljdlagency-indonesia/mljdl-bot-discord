"""
services/github_service.py -- GitHub repo activity via PyGithub
"""
from datetime import datetime, timezone
from github import Github, Repository
from bot.config import config

_gh: Github | None = None
_repo: Repository.Repository | None = None


def _get_repo() -> Repository.Repository:
    global _gh, _repo
    if _repo is None:
        _gh = Github(config.GITHUB_TOKEN)
        _repo = _gh.get_repo(config.GITHUB_REPO)
    return _repo


def get_recent_commits(limit: int = 5) -> list[dict]:
    """Ambil N commit terbaru dari default branch."""
    repo = _get_repo()
    commits = repo.get_commits()
    result = []
    for commit in commits[:limit]:
        result.append({
            "sha": commit.sha[:7],
            "message": commit.commit.message.split("\n")[0],  # first line only
            "author": commit.commit.author.name,
            "url": commit.html_url,
            "date": commit.commit.author.date,
        })
    return result


def get_open_prs(limit: int = 5) -> list[dict]:
    """Ambil open pull requests."""
    repo = _get_repo()
    prs = repo.get_pulls(state="open", sort="updated")
    result = []
    for pr in list(prs)[:limit]:
        result.append({
            "number": pr.number,
            "title": pr.title,
            "author": pr.user.login,
            "url": pr.html_url,
            "created_at": pr.created_at,
            "reviewers": [r.login for r in pr.requested_reviewers],
        })
    return result


def get_recent_issues(limit: int = 5, state: str = "open") -> list[dict]:
    """Ambil issues terbaru."""
    repo = _get_repo()
    issues = repo.get_issues(state=state, sort="updated")
    result = []
    for issue in list(issues)[:limit]:
        if issue.pull_request:
            continue  # skip PR yang kedetect sebagai issue
        result.append({
            "number": issue.number,
            "title": issue.title,
            "author": issue.user.login,
            "url": issue.html_url,
            "labels": [l.name for l in issue.labels],
            "created_at": issue.created_at,
        })
    return result


def get_events_since(since: datetime) -> list[dict]:
    """
    Ambil semua events repo sejak `since`.
    Dipakai buat polling notifikasi otomatis.
    """
    repo = _get_repo()
    events = []
    for event in repo.get_events():
        if event.created_at.replace(tzinfo=timezone.utc) <= since.replace(tzinfo=timezone.utc):
            break
        events.append({
            "type": event.type,
            "actor": event.actor.login,
            "created_at": event.created_at,
            "payload": event.payload,
        })
    return events
