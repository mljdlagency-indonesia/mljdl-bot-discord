"""
models/task.py -- Enums dan constants untuk task management
"""
from enum import Enum


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


STATUS_EMOJI = {
    TaskStatus.TODO: "⬜",
    TaskStatus.IN_PROGRESS: "🔄",
    TaskStatus.REVIEW: "👀",
    TaskStatus.DONE: "✅",
    TaskStatus.CANCELLED: "❌",
}

PRIORITY_EMOJI = {
    TaskPriority.LOW: "🔵",
    TaskPriority.MEDIUM: "🟡",
    TaskPriority.HIGH: "🟠",
    TaskPriority.URGENT: "🔴",
}
