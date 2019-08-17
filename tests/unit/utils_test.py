import pytest
import re

from composer.backend.filesystem.utils import (
    add_to_section,
    read_item,
    read_section,
    read_until,
    get_task_items,
    is_blank_line,
    is_completed_task,
    is_undone_task,
    is_wip_task,
    is_scheduled_task,
    is_section,
)

from .fixtures import logfile, empty_logfile, tasklist_file  # noqa


class TestReadItem(object):

    def test_read_generic_item(self, logfile):
        item, _, _ = read_item(logfile)
        assert item == "[ ] a task\n"

    def test_read_blank_line(self, logfile):
        item, _, _ = read_item(logfile, of_type=is_blank_line)
        assert item == "\n"

    def test_read_text_item(self, logfile):
        logfile.readline()
        logfile.readline()
        item, _, _ = read_item(logfile, starting_position=logfile.tell())
        assert item == "Just some additional clarifications\n"

    def test_read_task(self, logfile):
        item, _, _ = read_item(logfile, of_type=is_wip_task)
        assert item == "[\\] a WIP task\n"

    def test_read_task_with_subtasks(self, logfile):
        for i in range(5):
            logfile.readline()
        item, _, _ = read_item(logfile, starting_position=logfile.tell())
        expected = ("[ ] a task with subtasks\n"
                    "\t[ ] first thing\n"
                    "\tclarification of first thing\n"
                    "\t[ ] second thing\n")
        assert item == expected

    def test_read_from_position(self, logfile):
        item, _, _ = read_item(logfile, starting_position=11)
        assert item == "[\\] a WIP task\n"

    def test_read_empty_file(self, empty_logfile):
        item, _, _ = read_item(empty_logfile)
        assert item is None

    def test_read_type_not_found(self, logfile):
        item, _, _ = read_item(logfile, of_type=is_section)
        assert item is None

    def test_complement_when_found(self, logfile):
        expected = ("[ ] a task\n"
                    "[\\] a WIP task\n"
                    "Just some additional clarifications\n"
                    "\n"
                    "[ ] a task with subtasks\n"
                    "\t[ ] first thing\n"
                    "\tclarification of first thing\n"
                    "\t[ ] second thing\n"
                    "[ ] another task\n")

        _, _, complement = read_item(logfile, of_type=is_scheduled_task)
        assert complement.read() == expected

    def test_complement_when_not_found(self, logfile):
        _, _, complement = read_item(logfile, of_type=is_section)
        assert complement.read() == logfile.read()

    def test_index_when_found(self, logfile):
        _, index, _ = read_item(logfile, of_type=is_wip_task)
        # should be the position right AFTER the item
        # in the original file
        assert index == 26

    def test_index_when_not_found(self, logfile):
        _, index, _ = read_item(logfile, of_type=is_section)
        assert index == -1


class TestReadUntil(object):

    def test_read_until_pattern(self, logfile):
        pattern = re.compile(r"^Just")
        contents, _, _ = read_until(logfile, pattern)
        expected = ("[ ] a task\n"
                    "[\\] a WIP task\n")
        assert contents == expected

    def test_read_until_inclusive(self, logfile):
        pattern = re.compile(r"^Just")
        contents, _, _ = read_until(logfile, pattern, inclusive=True)
        expected = ("[ ] a task\n"
                    "[\\] a WIP task\n"
                    "Just some additional clarifications\n")
        assert contents == expected

    def test_read_until_from_starting_position(self, logfile):
        pattern = re.compile(r"^\[ \]")
        contents, _, _ = read_until(logfile, pattern, starting_position=11)
        expected = ("[\\] a WIP task\n"
                    "Just some additional clarifications\n"
                    "\n"
                    "[o] a scheduled task [$TOMORROW$]\n")
        assert contents == expected

    def test_read_until_index(self, logfile):
        pattern = re.compile(r"^Just")
        _, index, _ = read_until(logfile, pattern)
        assert index == 26

    def test_read_until_complement(self, logfile):
        pattern = re.compile(r"^Just")
        _, _, complement = read_until(logfile, pattern)
        expected = ("Just some additional clarifications\n"
                    "\n"
                    "[o] a scheduled task [$TOMORROW$]\n"
                    "[ ] a task with subtasks\n"
                    "\t[ ] first thing\n"
                    "\tclarification of first thing\n"
                    "\t[ ] second thing\n"
                    "[ ] another task\n")
        assert complement.read() == expected

    def test_read_until_complement_inclusive(self, logfile):
        pattern = re.compile(r"^Just")
        _, _, complement = read_until(logfile, pattern, inclusive=True)
        expected = ("\n"
                    "[o] a scheduled task [$TOMORROW$]\n"
                    "[ ] a task with subtasks\n"
                    "\t[ ] first thing\n"
                    "\tclarification of first thing\n"
                    "\t[ ] second thing\n"
                    "[ ] another task\n")
        assert complement.read() == expected

    def test_pattern_not_found(self, logfile):
        pattern = re.compile(r"^NOT THERE")
        with pytest.raises(ValueError):
            _, _, _ = read_until(logfile, pattern)


class TestReadSection(object):

    def test_read_section(self, tasklist_file):
        contents = read_section(tasklist_file, 'THIS WEEK')
        expected = ("[ ] a task with subtasks\n"
                    "\t[\\] first thing\n"
                    "\tclarification of first thing\n"
                    "\t[ ] second thing\n")
        assert contents == expected

    def test_read_section_empty(self, tasklist_file):
        contents = read_section(tasklist_file, 'THIS MONTH')
        expected = ""
        assert contents == expected

    def test_read_section_missing(self, tasklist_file):
        with pytest.raises(ValueError):
            read_section(tasklist_file, 'THIS DECADE')


class TestAddToSection(object):

    def test_add_to_section(self, tasklist_file):
        new_tasks = "[ ] one more thing to do!\n"
        updated = add_to_section(tasklist_file, 'THIS WEEK', new_tasks)
        expected = ("TOMORROW:\n"
                    "[ ] a task\n"
                    "[\\] a WIP task\n"
                    "Just some additional clarifications\n"
                    "\n"
                    "[o] a scheduled task [$TOMORROW$]\n"
                    "THIS WEEK:\n"
                    "[ ] one more thing to do!\n"
                    "[ ] a task with subtasks\n"
                    "\t[\\] first thing\n"
                    "\tclarification of first thing\n"
                    "\t[ ] second thing\n"
                    "THIS MONTH:\n"
                    "\n"
                    "UNSCHEDULED:\n"
                    "[ ] another task\n")
        assert updated.read() == expected

    def test_add_to_section_missing(self, tasklist_file):
        new_tasks = "[ ] one more thing to do!\n"
        with pytest.raises(ValueError):
            add_to_section(tasklist_file, 'THIS DECADE', new_tasks)


class TestGetTaskItems(object):

    def test_get_all_items(self, tasklist_file):
        items, complement = get_task_items(tasklist_file)
        assert items == tasklist_file.read()
        assert complement.read() == ""

    def test_get_no_items(self, tasklist_file):
        items, complement = get_task_items(tasklist_file, of_type=is_completed_task)
        assert items == ""
        assert complement.read() == tasklist_file.read()

    def test_get_some_items(self, tasklist_file):
        items, complement = get_task_items(tasklist_file, of_type=is_undone_task)
        expected = ("[ ] a task\n"
                    "[ ] a task with subtasks\n"
                    "\t[\\] first thing\n"
                    "\tclarification of first thing\n"
                    "\t[ ] second thing\n"
                    "[ ] another task\n")
        expected_complement = ("TOMORROW:\n"
                            "[\\] a WIP task\n"
                            "Just some additional clarifications\n"
                            "\n"
                            "[o] a scheduled task [$TOMORROW$]\n"
                            "THIS WEEK:\n"
                            "THIS MONTH:\n"
                            "\n"
                            "UNSCHEDULED:\n")

        assert items == expected
        assert complement.read() == expected_complement

    def test_get_items_empty_file(self, empty_logfile):
        items, complement = get_task_items(empty_logfile)
        assert items == ""
        assert complement.read() == empty_logfile.read()
