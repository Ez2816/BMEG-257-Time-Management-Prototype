"""
Test suite for the Time Management Prototype.

Covers:
    - parse_tasks()      – file parsing function
    - categorize_tasks() – categorizing function
    - identify_priority() / prioritize_tasks() – priority identification
"""

import io
import textwrap
import unittest
from datetime import date, timedelta

from time_management import (
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    categorize_tasks,
    identify_priority,
    parse_tasks,
    prioritize_tasks,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _csv_source(text):
    """Return a StringIO built from a dedented multi-line string."""
    return io.StringIO(textwrap.dedent(text).strip())


def _make_task(name="Task", deadline=None, category="work", importance=5):
    return {
        "name": name,
        "deadline": deadline or date(2030, 1, 1),
        "category": category,
        "importance": importance,
    }


# ---------------------------------------------------------------------------
# parse_tasks
# ---------------------------------------------------------------------------

class TestParseTasksValid(unittest.TestCase):
    """parse_tasks returns correct task dicts for valid CSV input."""

    def test_single_row(self):
        src = _csv_source("""
            name,deadline,category,importance
            Write report,2030-06-15,work,8
        """)
        tasks = parse_tasks(src)
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task["name"], "Write report")
        self.assertEqual(task["deadline"], date(2030, 6, 15))
        self.assertEqual(task["category"], "work")
        self.assertEqual(task["importance"], 8)

    def test_multiple_rows(self):
        src = _csv_source("""
            name,deadline,category,importance
            Gym,2030-01-10,health,3
            Budget,2030-01-20,finance,7
            Study,2030-01-25,school,6
        """)
        tasks = parse_tasks(src)
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]["name"], "Gym")
        self.assertEqual(tasks[1]["category"], "finance")
        self.assertEqual(tasks[2]["importance"], 6)

    def test_all_valid_categories(self):
        from time_management import VALID_CATEGORIES
        rows = "\n".join(
            f"Task {cat},2030-05-01,{cat},5" for cat in sorted(VALID_CATEGORIES)
        )
        src = _csv_source("name,deadline,category,importance\n" + rows)
        tasks = parse_tasks(src)
        parsed_categories = {t["category"] for t in tasks}
        self.assertEqual(parsed_categories, VALID_CATEGORIES)

    def test_column_order_independent(self):
        src = _csv_source("""
            importance,category,name,deadline
            4,personal,Dentist,2030-03-01
        """)
        tasks = parse_tasks(src)
        self.assertEqual(tasks[0]["name"], "Dentist")
        self.assertEqual(tasks[0]["importance"], 4)

    def test_boundary_importance_values(self):
        src = _csv_source("""
            name,deadline,category,importance
            Low,2030-01-01,other,1
            High,2030-01-01,other,10
        """)
        tasks = parse_tasks(src)
        self.assertEqual(tasks[0]["importance"], 1)
        self.assertEqual(tasks[1]["importance"], 10)

    def test_empty_csv_returns_empty_list(self):
        src = _csv_source("name,deadline,category,importance\n")
        tasks = parse_tasks(src)
        self.assertEqual(tasks, [])


class TestParseTasksInvalid(unittest.TestCase):
    """parse_tasks raises ValueError for invalid input."""

    def test_missing_column_raises(self):
        src = _csv_source("""
            name,deadline,category
            Task,2030-01-01,work
        """)
        with self.assertRaises(ValueError):
            parse_tasks(src)

    def test_invalid_date_format_raises(self):
        src = _csv_source("""
            name,deadline,category,importance
            Task,01/01/2030,work,5
        """)
        with self.assertRaises(ValueError):
            parse_tasks(src)

    def test_invalid_category_raises(self):
        src = _csv_source("""
            name,deadline,category,importance
            Task,2030-01-01,hobbies,5
        """)
        with self.assertRaises(ValueError):
            parse_tasks(src)

    def test_non_integer_importance_raises(self):
        src = _csv_source("""
            name,deadline,category,importance
            Task,2030-01-01,work,five
        """)
        with self.assertRaises(ValueError):
            parse_tasks(src)

    def test_importance_out_of_range_raises(self):
        for bad_val in ("0", "11"):
            with self.subTest(importance=bad_val):
                src = _csv_source(
                    f"name,deadline,category,importance\nTask,2030-01-01,work,{bad_val}"
                )
                with self.assertRaises(ValueError):
                    parse_tasks(src)

    def test_empty_name_raises(self):
        src = _csv_source("""
            name,deadline,category,importance
            ,2030-01-01,work,5
        """)
        with self.assertRaises(ValueError):
            parse_tasks(src)


# ---------------------------------------------------------------------------
# categorize_tasks
# ---------------------------------------------------------------------------

class TestCategorizeTasks(unittest.TestCase):
    """categorize_tasks groups tasks by their category."""

    def test_single_category(self):
        tasks = [_make_task("A", category="work"), _make_task("B", category="work")]
        result = categorize_tasks(tasks)
        self.assertIn("work", result)
        self.assertEqual(len(result["work"]), 2)

    def test_multiple_categories(self):
        tasks = [
            _make_task("A", category="work"),
            _make_task("B", category="personal"),
            _make_task("C", category="work"),
        ]
        result = categorize_tasks(tasks)
        self.assertEqual(len(result["work"]), 2)
        self.assertEqual(len(result["personal"]), 1)

    def test_empty_input_returns_empty_dict(self):
        self.assertEqual(categorize_tasks([]), {})

    def test_task_objects_are_preserved(self):
        task = _make_task("Study", category="school", importance=9)
        result = categorize_tasks([task])
        self.assertIs(result["school"][0], task)

    def test_only_present_categories_are_keys(self):
        tasks = [_make_task(category="health")]
        result = categorize_tasks(tasks)
        self.assertEqual(list(result.keys()), ["health"])


# ---------------------------------------------------------------------------
# identify_priority / prioritize_tasks
# ---------------------------------------------------------------------------

class TestIdentifyPriority(unittest.TestCase):
    """identify_priority returns the correct priority level."""

    REF = date(2030, 1, 1)

    def _task(self, days_ahead, importance):
        deadline = self.REF + timedelta(days=days_ahead)
        return _make_task(deadline=deadline, importance=importance)

    # High priority cases (combined score 5 or 6)
    def test_high_urgency_high_importance(self):
        task = self._task(days_ahead=1, importance=8)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_HIGH)

    def test_high_urgency_medium_importance(self):
        task = self._task(days_ahead=2, importance=5)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_HIGH)

    def test_medium_urgency_high_importance(self):
        task = self._task(days_ahead=5, importance=9)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_HIGH)

    # Medium priority cases (combined score 3 or 4)
    def test_low_urgency_high_importance(self):
        task = self._task(days_ahead=10, importance=10)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_MEDIUM)

    def test_medium_urgency_medium_importance(self):
        task = self._task(days_ahead=5, importance=5)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_MEDIUM)

    def test_high_urgency_low_importance(self):
        task = self._task(days_ahead=2, importance=2)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_MEDIUM)

    # Low priority cases (combined score 2)
    def test_low_urgency_low_importance(self):
        task = self._task(days_ahead=15, importance=2)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_LOW)

    def test_medium_urgency_low_importance(self):
        # urgency=2 (4-7 days) + importance_score=1 (1-3) → combined=3 → medium
        task = self._task(days_ahead=6, importance=1)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_MEDIUM)

    # Deadline boundary conditions
    def test_deadline_today_is_urgent(self):
        task = self._task(days_ahead=0, importance=5)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_HIGH)

    def test_deadline_exactly_3_days_is_urgent(self):
        task = self._task(days_ahead=3, importance=5)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_HIGH)

    def test_deadline_exactly_4_days_is_medium_urgency(self):
        task = self._task(days_ahead=4, importance=5)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_MEDIUM)

    def test_deadline_exactly_7_days_is_medium_urgency(self):
        # urgency=2 (4-7 days) + importance_score=1 (1-3) → combined=3 → medium
        task = self._task(days_ahead=7, importance=2)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_MEDIUM)

    def test_deadline_8_days_is_low_urgency(self):
        task = self._task(days_ahead=8, importance=2)
        self.assertEqual(identify_priority(task, self.REF), PRIORITY_LOW)


class TestPrioritizeTasks(unittest.TestCase):
    """prioritize_tasks annotates and sorts tasks by priority."""

    REF = date(2030, 1, 1)

    def test_priority_key_added(self):
        tasks = [_make_task(deadline=self.REF + timedelta(days=1), importance=8)]
        result = prioritize_tasks(tasks, self.REF)
        self.assertIn("priority", result[0])

    def test_sorted_high_before_medium_before_low(self):
        tasks = [
            _make_task("Low",    deadline=self.REF + timedelta(days=15), importance=2),
            _make_task("High",   deadline=self.REF + timedelta(days=1),  importance=9),
            _make_task("Medium", deadline=self.REF + timedelta(days=10), importance=8),
        ]
        result = prioritize_tasks(tasks, self.REF)
        self.assertEqual(result[0]["priority"], PRIORITY_HIGH)
        self.assertEqual(result[1]["priority"], PRIORITY_MEDIUM)
        self.assertEqual(result[2]["priority"], PRIORITY_LOW)

    def test_original_task_dicts_not_mutated(self):
        task = _make_task(deadline=self.REF + timedelta(days=1), importance=8)
        original_keys = set(task.keys())
        prioritize_tasks([task], self.REF)
        self.assertEqual(set(task.keys()), original_keys)

    def test_empty_list_returns_empty_list(self):
        self.assertEqual(prioritize_tasks([], self.REF), [])

    def test_all_high_priority_tasks_returned(self):
        tasks = [
            _make_task("A", deadline=self.REF + timedelta(days=1), importance=8),
            _make_task("B", deadline=self.REF + timedelta(days=2), importance=9),
        ]
        result = prioritize_tasks(tasks, self.REF)
        self.assertTrue(all(t["priority"] == PRIORITY_HIGH for t in result))


if __name__ == "__main__":
    unittest.main()
