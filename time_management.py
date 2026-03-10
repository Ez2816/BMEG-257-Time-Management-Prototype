"""
Time Management Prototype
Provides utilities for parsing task files, categorizing tasks,
and identifying task priorities.
"""

import csv
import io
from datetime import date, datetime


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_CATEGORIES = {"work", "personal", "school", "health", "finance", "other"}

PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"


# ---------------------------------------------------------------------------
# File Parsing
# ---------------------------------------------------------------------------

def parse_tasks(source):
    """Parse tasks from a CSV source.

    The CSV must contain the following columns (order-independent):
        name        – task name (str, required)
        deadline    – due date in YYYY-MM-DD format (str, required)
        category    – one of the VALID_CATEGORIES values (str, required)
        importance  – integer 1-10, where 10 is most important (int, required)

    Args:
        source: A file path (str) or a file-like object containing CSV data.

    Returns:
        A list of task dicts.  Each dict contains:
            {
                "name":       str,
                "deadline":   datetime.date,
                "category":   str,
                "importance": int,
            }

    Raises:
        ValueError: If a required column is missing or a field contains an
                    invalid value.
    """
    required_columns = {"name", "deadline", "category", "importance"}

    if isinstance(source, str):
        with open(source, newline="", encoding="utf-8") as fh:
            return _read_csv(fh, required_columns)
    else:
        return _read_csv(source, required_columns)


def _read_csv(fh, required_columns):
    reader = csv.DictReader(fh)

    if reader.fieldnames is None:
        return []

    lowered_fields = {f.strip().lower() for f in reader.fieldnames}
    missing = required_columns - lowered_fields
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    tasks = []
    for i, row in enumerate(reader, start=2):
        row_lower = {k.strip().lower(): v.strip() for k, v in row.items()}

        name = row_lower.get("name", "")
        if not name:
            raise ValueError(f"Row {i}: 'name' must not be empty.")

        raw_deadline = row_lower.get("deadline", "")
        try:
            deadline = datetime.strptime(raw_deadline, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(
                f"Row {i}: 'deadline' must be in YYYY-MM-DD format, got '{raw_deadline}'."
            )

        category = row_lower.get("category", "").lower()
        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"Row {i}: 'category' must be one of {VALID_CATEGORIES}, got '{category}'."
            )

        raw_importance = row_lower.get("importance", "")
        try:
            importance = int(raw_importance)
        except ValueError:
            raise ValueError(
                f"Row {i}: 'importance' must be an integer, got '{raw_importance}'."
            )
        if not 1 <= importance <= 10:
            raise ValueError(
                f"Row {i}: 'importance' must be between 1 and 10, got {importance}."
            )

        tasks.append(
            {
                "name": name,
                "deadline": deadline,
                "category": category,
                "importance": importance,
            }
        )

    return tasks


# ---------------------------------------------------------------------------
# Categorizing
# ---------------------------------------------------------------------------

def categorize_tasks(tasks):
    """Group tasks by their category.

    Args:
        tasks: A list of task dicts as returned by :func:`parse_tasks`.

    Returns:
        A dict mapping each category string to a list of task dicts that
        belong to that category.  Only categories that have at least one
        task are present in the result.

    Example::

        {
            "work":     [{"name": "Report", ...}],
            "personal": [{"name": "Gym", ...}],
        }
    """
    grouped = {}
    for task in tasks:
        cat = task["category"]
        grouped.setdefault(cat, []).append(task)
    return grouped


# ---------------------------------------------------------------------------
# Priority Identification
# ---------------------------------------------------------------------------

def identify_priority(task, reference_date=None):
    """Determine the priority level of a single task.

    Priority is calculated from two factors:

    * **Urgency** – how many days remain until the deadline:
        - 0-3 days  → urgency score 3
        - 4-7 days  → urgency score 2
        - 8+ days   → urgency score 1

    * **Importance** – the task's importance rating (1-10):
        - 7-10 → importance score 3
        - 4-6  → importance score 2
        - 1-3  → importance score 1

    The combined score (urgency + importance) maps to a priority level:
        - 5-6 → ``"high"``
        - 3-4 → ``"medium"``
        - 2   → ``"low"``

    Args:
        task: A task dict as returned by :func:`parse_tasks`.
        reference_date: The date to measure urgency from.  Defaults to
                        ``datetime.date.today()`` when *None*.

    Returns:
        One of ``"high"``, ``"medium"``, or ``"low"``.
    """
    if reference_date is None:
        reference_date = date.today()

    days_remaining = (task["deadline"] - reference_date).days

    if days_remaining <= 3:
        urgency_score = 3
    elif days_remaining <= 7:
        urgency_score = 2
    else:
        urgency_score = 1

    importance = task["importance"]
    if importance >= 7:
        importance_score = 3
    elif importance >= 4:
        importance_score = 2
    else:
        importance_score = 1

    combined = urgency_score + importance_score

    if combined >= 5:
        return PRIORITY_HIGH
    elif combined >= 3:
        return PRIORITY_MEDIUM
    else:
        return PRIORITY_LOW


def prioritize_tasks(tasks, reference_date=None):
    """Assign a priority level to every task in *tasks*.

    Args:
        tasks: A list of task dicts as returned by :func:`parse_tasks`.
        reference_date: Passed through to :func:`identify_priority`.

    Returns:
        A list of task dicts (copies) each augmented with a ``"priority"``
        key whose value is one of ``"high"``, ``"medium"``, or ``"low"``.
        The list is sorted from highest to lowest priority.
    """
    priority_order = {PRIORITY_HIGH: 0, PRIORITY_MEDIUM: 1, PRIORITY_LOW: 2}

    result = []
    for task in tasks:
        augmented = dict(task)
        augmented["priority"] = identify_priority(task, reference_date)
        result.append(augmented)

    result.sort(key=lambda t: priority_order[t["priority"]])
    return result
