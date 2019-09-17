import pytest
import re

from composer.backend.filesystem.utils import (
    add_to_section,
    make_file,
    read_item,
    read_section,
    partition_at,
    partition_items,
    get_task_items,
    is_completed_task,
    is_undone_task,
)

from .fixtures import logfile, empty_logfile, tasklist_file  # noqa


class TestReadItem(object):
    def test_generic_item(self, logfile):
        item, _ = read_item(logfile)
        assert item == "AGENDA:\n"

    def test_text_item(self, logfile):
        for _ in range(3):
            logfile.readline()
        file = make_file(logfile.read())
        item, _ = read_item(file)
        assert item == "Just some additional clarifications\n"

    def test_blank_line(self, logfile):
        for _ in range(4):
            logfile.readline()
        file = make_file(logfile.read())
        item, _ = read_item(file)
        assert item == "\n"

    def test_task(self, logfile):
        for _ in range(2):
            logfile.readline()
        file = make_file(logfile.read())
        item, _ = read_item(file)
        assert item == "[\\] a WIP task\n"

    def test_task_with_subtasks(self, logfile):
        for _ in range(6):
            logfile.readline()
        file = make_file(logfile.read())
        item, _ = read_item(file)
        expected = (
            "[ ] a task with subtasks\n"
            "\t[ ] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
        )
        assert item == expected

    def test_empty_file(self, empty_logfile):
        item, _ = read_item(empty_logfile)
        assert item is None

    def test_complement_when_found(self, logfile):
        expected = (
            "[ ] a task\n"
            "[\\] a WIP task\n"
            "Just some additional clarifications\n"
            "\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "[ ] a task with subtasks\n"
            "\t[ ] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "[ ] another task\n"
        )

        _, complement = read_item(logfile)
        assert complement.read() == expected

    def test_complement_when_not_found(self, empty_logfile):
        _, complement = read_item(empty_logfile)
        assert complement.read() == empty_logfile.read()


class TestPartitionAt(object):
    def test_first_part(self, logfile):
        pattern = re.compile(r"^Just")
        first, _ = partition_at(logfile, pattern)
        expected = (
            "AGENDA:\n"
            "[ ] a task\n"
            "[\\] a WIP task\n"
        )
        assert first.read() == expected

    def test_first_part_inclusive(self, logfile):
        pattern = re.compile(r"^Just")
        first, _ = partition_at(logfile, pattern, inclusive=True)
        expected = (
            "AGENDA:\n"
            "[ ] a task\n"
            "[\\] a WIP task\n"
            "Just some additional clarifications\n"
        )
        assert first.read() == expected

    def test_second_part(self, logfile):
        pattern = re.compile(r"^Just")
        _, second = partition_at(logfile, pattern)
        expected = (
            "Just some additional clarifications\n"
            "\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "[ ] a task with subtasks\n"
            "\t[ ] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "[ ] another task\n"
        )
        assert second.read() == expected

    def test_second_part_inclusive(self, logfile):
        pattern = re.compile(r"^Just")
        _, second = partition_at(logfile, pattern, inclusive=True)
        expected = (
            "\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "[ ] a task with subtasks\n"
            "\t[ ] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "[ ] another task\n"
        )
        assert second.read() == expected

    def test_pattern_not_found(self, logfile):
        pattern = re.compile(r"^NOT THERE")
        with pytest.raises(ValueError):
            _, _ = partition_at(logfile, pattern)

    def test_pattern_not_found_or_eof(self, logfile):
        pattern = re.compile(r"^NOT THERE")
        first, second = partition_at(logfile, pattern, or_eof=True)
        assert first.read() == logfile.getvalue()
        assert second.read() == ""


class TestReadSection(object):
    def test_read_section(self, tasklist_file):
        contents, _ = read_section(tasklist_file, 'THIS WEEK')
        expected = (
            "[ ] a task with subtasks\n"
            "\t[\\] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
        )
        assert contents.read() == expected

    def test_complement(self, tasklist_file):
        _, complement = read_section(tasklist_file, 'THIS WEEK')
        expected = (
            "TOMORROW:\n"
            "[ ] a task\n"
            "[\\] a WIP task\n"
            "Just some additional clarifications\n"
            "\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "UNSCHEDULED:\n"
            "[ ] another task\n"
        )
        assert complement.read() == expected

    def test_empty_section(self, tasklist_file):
        contents, _ = read_section(tasklist_file, 'THIS MONTH')
        expected = ""
        assert contents.read() == expected

    def test_empty_section_complement(self, tasklist_file):
        _, complement = read_section(tasklist_file, 'THIS MONTH')
        assert complement.read() == tasklist_file.read()

    def test_section_missing(self, tasklist_file):
        with pytest.raises(ValueError):
            read_section(tasklist_file, 'THIS DECADE')


class TestAddToSection(object):
    def test_add_to_empty_section(self, tasklist_file):
        new_tasks = "[ ] one more thing to do!\n"
        updated = add_to_section(tasklist_file, 'THIS MONTH', new_tasks)
        expected = (
            "TOMORROW:\n"
            "[ ] a task\n"
            "[\\] a WIP task\n"
            "Just some additional clarifications\n"
            "\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "THIS WEEK:\n"
            "[ ] a task with subtasks\n"
            "\t[\\] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "THIS MONTH:\n"
            "[ ] one more thing to do!\n"
            "UNSCHEDULED:\n"
            "[ ] another task\n"
        )
        assert updated.read() == expected

    def test_section_missing(self, tasklist_file):
        new_tasks = "[ ] one more thing to do!\n"
        with pytest.raises(ValueError):
            add_to_section(tasklist_file, 'THIS DECADE', new_tasks)

    def test_existing_contents_are_preserved_below(self, tasklist_file):
        new_tasks = "[ ] one more thing to do!\n"
        updated = add_to_section(tasklist_file, 'THIS WEEK', new_tasks)
        expected = (
            "TOMORROW:\n"
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
            "UNSCHEDULED:\n"
            "[ ] another task\n"
        )
        assert updated.read() == expected

    def test_existing_contents_are_preserved_above(self, tasklist_file):
        new_tasks = "[ ] one more thing to do!\n"
        updated = add_to_section(
            tasklist_file, 'THIS WEEK', new_tasks, above=False
        )
        expected = (
            "TOMORROW:\n"
            "[ ] a task\n"
            "[\\] a WIP task\n"
            "Just some additional clarifications\n"
            "\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "THIS WEEK:\n"
            "[ ] a task with subtasks\n"
            "\t[\\] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "[ ] one more thing to do!\n"
            "THIS MONTH:\n"
            "UNSCHEDULED:\n"
            "[ ] another task\n"
        )
        assert updated.read() == expected

    def test_file_containing_only_section(self):
        contents = "AGENDA:\n[ ] do this\n[\\] another thing\n"
        new_tasks = "[ ] one more thing to do!\n"
        file = make_file(contents)
        updated = add_to_section(
            file, 'AGENDA', new_tasks, above=False, ensure_separator=True
        )
        expected = contents + new_tasks
        assert updated.read() == expected

    def test_separator_added_if_needed(self, tasklist_file):
        new_tasks = "[ ] one more thing to do!\n"
        updated = add_to_section(
            tasklist_file, 'THIS WEEK', new_tasks, ensure_separator=True
        )
        expected = (
            "TOMORROW:\n"
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
            "\n"
            "THIS MONTH:\n"
            "UNSCHEDULED:\n"
            "[ ] another task\n"
        )
        assert updated.read() == expected


class TestGetTaskItems(object):
    def test_all_items(self, tasklist_file):
        items = get_task_items(tasklist_file)
        items_string = "".join(items)
        assert items_string == tasklist_file.read()

    def test_no_items(self, tasklist_file):
        items = get_task_items(tasklist_file, of_type=lambda x: False)
        items_string = "".join(items)
        assert items_string == ""

    def test_no_matching_items(self, tasklist_file):
        items = get_task_items(tasklist_file, of_type=is_completed_task)
        items_string = "".join(items)
        assert items_string == ""

    def test_all_matching_items(self, tasklist_file):
        items = get_task_items(
            tasklist_file, of_type=lambda x: not is_completed_task(x)
        )
        items_string = "".join(items)
        assert items_string == tasklist_file.read()

    def test_some_items(self, tasklist_file):
        items = get_task_items(tasklist_file, of_type=is_undone_task)
        items_string = "".join(items)
        expected = (
            "[ ] a task\n"
            "[ ] a task with subtasks\n"
            "\t[\\] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "[ ] another task\n"
        )
        assert items_string == expected

    def test_some_items_negation(self, tasklist_file):
        items = get_task_items(
            tasklist_file, of_type=lambda x: not is_undone_task(x)
        )
        items_string = "".join(items)
        expected = (
            "TOMORROW:\n"
            "[\\] a WIP task\n"
            "Just some additional clarifications\n"
            "\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "UNSCHEDULED:\n"
        )
        assert items_string == expected

    def test_items_and_negation_equals_original(self, tasklist_file):
        items = get_task_items(tasklist_file, of_type=is_undone_task)
        items_string = "".join(items)
        items_negation = get_task_items(
            tasklist_file, of_type=lambda x: not is_undone_task(x)
        )
        items_negation_string = "".join(items_negation)
        assert len(items_string + items_negation_string) == len(
            tasklist_file.read()
        )

    def test_empty_file(self, empty_logfile):
        items = get_task_items(empty_logfile)
        items_string = "".join(items)
        assert items_string == ""


class TestPartitionItems(object):
    def test_empty_list(self):
        items = []
        filtered, excluded = partition_items(items, lambda item: True)
        assert filtered == items
        assert excluded == items

    def test_all_pass(self):
        items = [1, 2, 3]
        filtered, excluded = partition_items(items, lambda item: True)
        assert filtered == items
        assert excluded == []

    def test_all_fail(self):
        items = [1, 2, 3]
        filtered, excluded = partition_items(items, lambda item: False)
        assert filtered == []
        assert excluded == items

    def test_some_pass(self):
        items = [1, 2, 3]
        filtered, excluded = partition_items(items, lambda item: item < 3)
        assert filtered == [1, 2]
        assert excluded == [3]

    def test_pass_and_fail_equal_original(self):
        items = [1, 2, 3]
        filtered, excluded = partition_items(items, lambda item: item > 2)
        assert set(filtered + excluded) == set(items)
