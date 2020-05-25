import pytest
import re

from composer.backend.filesystem.primitives.entries import (
    add_to_section,
    read_section,
    partition_entries,
    get_entries,
    read_entry,
)
from composer.backend.filesystem.primitives.files import (
    make_file,
    partition_at,
    append_files,
)
from composer.backend.filesystem.primitives.parsing import (
    is_done_task,
    is_undone_task,
    is_completed,
    is_unfinished,
)

from ....fixtures import logfile, empty_logfile, tasklist_file  # noqa


class TestReadEntry(object):
    def test_generic_entry(self, logfile):
        entry, _ = read_entry(logfile)
        assert entry == "AGENDA:\n"

    def test_text_entry(self, logfile):
        for _ in range(3):
            logfile.readline()
        file = make_file(logfile.read())
        entry, _ = read_entry(file)
        assert entry == "Just some additional clarifications\n"

    def test_blank_line(self, logfile):
        for _ in range(4):
            logfile.readline()
        file = make_file(logfile.read())
        entry, _ = read_entry(file)
        assert entry == "\n"

    def test_task(self, logfile):
        for _ in range(2):
            logfile.readline()
        file = make_file(logfile.read())
        entry, _ = read_entry(file)
        assert entry == "[\\] a WIP task\n"

    def test_task_with_subtasks(self, logfile):
        for _ in range(6):
            logfile.readline()
        file = make_file(logfile.read())
        entry, _ = read_entry(file)
        expected = (
            "[ ] a task with subtasks\n"
            "\t[ ] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
        )
        assert entry == expected

    def test_empty_file(self, empty_logfile):
        entry, _ = read_entry(empty_logfile)
        assert entry is None

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
            "[x] a done task\n"
            "\t[x] with\n"
            "\t[x] subtasks\n"
            "[ ] another task\n"
            "[x] also a done task\n"
            "[-] an invalid task\n"
            "\n"
            "NOTES:\n"
        )

        _, complement = read_entry(logfile)
        assert complement.read() == expected

    def test_complement_when_not_found(self, empty_logfile):
        _, complement = read_entry(empty_logfile)
        assert complement.read() == empty_logfile.read()


class TestPartitionAt(object):
    def test_first_part(self, logfile):
        pattern = re.compile(r"^Just")
        first, _ = partition_at(logfile, pattern)
        expected = "AGENDA:\n" "[ ] a task\n" "[\\] a WIP task\n"
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
            "[x] a done task\n"
            "\t[x] with\n"
            "\t[x] subtasks\n"
            "[ ] another task\n"
            "[x] also a done task\n"
            "[-] an invalid task\n"
            "\n"
            "NOTES:\n"
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
            "[x] a done task\n"
            "\t[x] with\n"
            "\t[x] subtasks\n"
            "[ ] another task\n"
            "[x] also a done task\n"
            "[-] an invalid task\n"
            "\n"
            "NOTES:\n"
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


class TestAppendFiles(object):
    def test_happy(self):
        first = make_file("Hi ")
        second = make_file("there")
        result = append_files(first, second)
        expected = "Hi there"
        assert result.read() == expected
        assert first.read() == "Hi "
        assert second.read() == "there"

    def test_first_empty(self):
        first = make_file("")
        second = make_file("there")
        result = append_files(first, second)
        expected = "there"
        assert result.read() == expected
        assert first.read() == ""
        assert second.read() == "there"

    def test_second_empty(self):
        first = make_file("Hi ")
        second = make_file("")
        result = append_files(first, second)
        expected = "Hi "
        assert result.read() == expected
        assert first.read() == "Hi "
        assert second.read() == ""

    def test_both_empty(self):
        first = make_file("")
        second = make_file("")
        result = append_files(first, second)
        expected = ""
        assert result.read() == expected
        assert first.read() == ""
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
            "Just some additional clarifications\n"
            "\n"
            "[\\] a WIP task\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "SOMEDAY:\n"
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
            "Just some additional clarifications\n"
            "\n"
            "[\\] a WIP task\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "THIS WEEK:\n"
            "[ ] a task with subtasks\n"
            "\t[\\] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "THIS MONTH:\n"
            "[ ] one more thing to do!\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "SOMEDAY:\n"
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
            "Just some additional clarifications\n"
            "\n"
            "[\\] a WIP task\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "THIS WEEK:\n"
            "[ ] one more thing to do!\n"
            "[ ] a task with subtasks\n"
            "\t[\\] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "SOMEDAY:\n"
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
            "Just some additional clarifications\n"
            "\n"
            "[\\] a WIP task\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "THIS WEEK:\n"
            "[ ] a task with subtasks\n"
            "\t[\\] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "[ ] one more thing to do!\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "SOMEDAY:\n"
            "[ ] another task\n"
        )
        assert updated.read() == expected

    def test_add_to_bottom_of_file(self, tasklist_file):
        new_tasks = "[ ] one more thing to do!\n"
        updated = add_to_section(
            tasklist_file, 'SOMEDAY', new_tasks, above=False
        )
        expected = (
            "TOMORROW:\n"
            "[ ] a task\n"
            "Just some additional clarifications\n"
            "\n"
            "[\\] a WIP task\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "THIS WEEK:\n"
            "[ ] a task with subtasks\n"
            "\t[\\] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "SOMEDAY:\n"
            "[ ] another task\n"
            "[ ] one more thing to do!\n"
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
            "Just some additional clarifications\n"
            "\n"
            "[\\] a WIP task\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "THIS WEEK:\n"
            "[ ] one more thing to do!\n"
            "[ ] a task with subtasks\n"
            "\t[\\] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "SOMEDAY:\n"
            "[ ] another task\n"
        )
        assert updated.read() == expected


class TestGetTaskEntries(object):
    def test_all_entries(self, tasklist_file):
        entries = get_entries(tasklist_file)
        entries_string = "".join(entries)
        assert entries_string == tasklist_file.read()

    def test_no_entries(self, tasklist_file):
        entries = get_entries(tasklist_file, of_type=lambda x: False)
        entries_string = "".join(entries)
        assert entries_string == ""

    def test_no_matching_entries(self, tasklist_file):
        entries = get_entries(tasklist_file, of_type=is_done_task)
        entries_string = "".join(entries)
        assert entries_string == ""

    def test_all_matching_entries(self, tasklist_file):
        entries = get_entries(
            tasklist_file, of_type=lambda x: not is_done_task(x)
        )
        entries_string = "".join(entries)
        assert entries_string == tasklist_file.read()

    def test_some_entries(self, tasklist_file):
        entries = get_entries(tasklist_file, of_type=is_undone_task)
        entries_string = "".join(entries)
        expected = (
            "[ ] a task\n"
            "[ ] a task with subtasks\n"
            "\t[\\] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "[ ] another task\n"
        )
        assert entries_string == expected

    def test_some_entries_negation(self, tasklist_file):
        entries = get_entries(
            tasklist_file, of_type=lambda x: not is_undone_task(x)
        )
        entries_string = "".join(entries)
        expected = (
            "TOMORROW:\n"
            "Just some additional clarifications\n"
            "\n"
            "[\\] a WIP task\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "SOMEDAY:\n"
        )
        assert entries_string == expected

    def test_entries_and_negation_equals_original(self, tasklist_file):
        entries = get_entries(tasklist_file, of_type=is_undone_task)
        entries_string = "".join(entries)
        entries_negation = get_entries(
            tasklist_file, of_type=lambda x: not is_undone_task(x)
        )
        entries_negation_string = "".join(entries_negation)
        assert len(entries_string + entries_negation_string) == len(
            tasklist_file.read()
        )

    def test_empty_file(self, empty_logfile):
        entries = get_entries(empty_logfile)
        entries_string = "".join(entries)
        assert entries_string == ""


class TestPartitionEntries(object):
    def test_empty_list(self):
        entries = []
        filtered, excluded = partition_entries(entries, lambda entry: True)
        assert filtered == entries
        assert excluded == entries

    def test_all_pass(self):
        entries = [1, 2, 3]
        filtered, excluded = partition_entries(entries, lambda entry: True)
        assert filtered == entries
        assert excluded == []

    def test_all_fail(self):
        entries = [1, 2, 3]
        filtered, excluded = partition_entries(entries, lambda entry: False)
        assert filtered == []
        assert excluded == entries

    def test_some_pass(self):
        entries = [1, 2, 3]
        filtered, excluded = partition_entries(
            entries, lambda entry: entry < 3
        )
        assert filtered == [1, 2]
        assert excluded == [3]

    def test_pass_and_fail_equal_original(self):
        entries = [1, 2, 3]
        filtered, excluded = partition_entries(
            entries, lambda entry: entry > 2
        )
        assert set(filtered + excluded) == set(entries)


class TestIsCompleted(object):
    def test_done(self):
        entry = "[x] do this"
        assert is_completed(entry)

    def test_done_with_subtasks(self):
        entry = "[x] do this\n" "\t[ ] a subtask\n" "\t[ ] another subtask"
        assert is_completed(entry)

    def test_invalid(self):
        entry = "[-] do this"
        assert is_completed(entry)

    def test_scheduled(self):
        entry = "[o] do this [$TOMORROW$]"
        assert is_completed(entry)

    def test_undone(self):
        entry = "[ ] do this"
        assert not is_completed(entry)

    def test_undone_with_subtasks(self):
        entry = "[ ] do this\n" "\t[x] a subtask\n" "\t[x] another subtask"
        assert not is_completed(entry)

    def test_wip(self):
        entry = "[\\] do this"
        assert not is_completed(entry)

    def test_text(self):
        entry = "do this"
        assert not is_completed(entry)

    def test_blank_line(self):
        entry = "\n"
        assert not is_completed(entry)

    def test_whitespace(self):
        entry = "  "
        assert not is_completed(entry)

    def test_empty(self):
        entry = ""
        assert not is_completed(entry)


class TestIsUnfinished(object):
    def test_done(self):
        entry = "[x] do this"
        assert not is_unfinished(entry)

    def test_done_with_subtasks(self):
        entry = "[x] do this\n" "\t[ ] a subtask\n" "\t[ ] another subtask"
        assert not is_unfinished(entry)

    def test_invalid(self):
        entry = "[-] do this"
        assert not is_unfinished(entry)

    def test_scheduled(self):
        entry = "[o] do this [$TOMORROW$]"
        assert not is_unfinished(entry)

    def test_undone(self):
        entry = "[ ] do this"
        assert is_unfinished(entry)

    def test_undone_with_subtasks(self):
        entry = "[ ] do this\n" "\t[x] a subtask\n" "\t[x] another subtask"
        assert is_unfinished(entry)

    def test_wip(self):
        entry = "[\\] do this"
        assert is_unfinished(entry)

    def test_text(self):
        entry = "do this"
        assert not is_unfinished(entry)

    def test_blank_line(self):
        entry = "\n"
        assert not is_unfinished(entry)

    def test_whitespace(self):
        entry = "  "
        assert not is_unfinished(entry)

    def test_empty(self):
        entry = ""
        assert not is_unfinished(entry)
