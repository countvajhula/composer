import pytest
import re

from composer.backend.filesystem.utils import (
    add_to_section,
    read_item,
    read_section,
    read_until,
    is_blank_line,
    is_wip_task,
    is_scheduled_task,
    is_section,
)

from .fixtures import logfile, empty_logfile, tasklist_file  # noqa


def test_read_generic_item(logfile):
    item, _, _ = read_item(logfile)
    assert item == "[ ] a task\n"


def test_read_blank_line(logfile):
    item, _, _ = read_item(logfile, of_type=is_blank_line)
    assert item == "\n"


def test_read_text_item(logfile):
    logfile.readline()
    logfile.readline()
    item, _, _ = read_item(logfile, starting_position=logfile.tell())
    assert item == "Just some additional clarifications\n"


def test_read_task(logfile):
    item, _, _ = read_item(logfile, of_type=is_wip_task)
    assert item == "[\\] a WIP task\n"


def test_read_task_with_subtasks(logfile):
    for i in range(5):
        logfile.readline()
    item, _, _ = read_item(logfile, starting_position=logfile.tell())
    expected = ("[ ] a task with subtasks\n"
                "\t[ ] first thing\n"
                "\tclarification of first thing\n"
                "\t[ ] second thing\n")
    assert item == expected


def test_read_from_position(logfile):
    item, _, _ = read_item(logfile, starting_position=11)
    assert item == "[\\] a WIP task\n"


def test_read_empty_file(empty_logfile):
    item, _, _ = read_item(empty_logfile)
    assert item is None


def test_read_type_not_found(logfile):
    item, _, _ = read_item(logfile, of_type=is_section)
    assert item is None


def test_complement_when_found(logfile):
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


def test_complement_when_not_found(logfile):
    _, _, complement = read_item(logfile, of_type=is_section)
    assert complement.read() == logfile.read()


def test_index_when_found(logfile):
    _, index, _ = read_item(logfile, of_type=is_wip_task)
    # should be the position right AFTER the item
    # in the original file
    assert index == 26


def test_index_when_not_found(logfile):
    _, index, _ = read_item(logfile, of_type=is_section)
    assert index == -1


# read_until

def test_read_until_pattern(logfile):
    pattern = re.compile(r"^Just")
    contents, _ = read_until(logfile, pattern)
    expected = ("[ ] a task\n"
                "[\\] a WIP task\n")
    assert contents == expected


def test_read_until_inclusive(logfile):
    pattern = re.compile(r"^Just")
    contents, _ = read_until(logfile, pattern, inclusive=True)
    expected = ("[ ] a task\n"
                "[\\] a WIP task\n"
                "Just some additional clarifications\n")
    assert contents == expected


def test_read_until_from_starting_position(logfile):
    pattern = re.compile(r"^\[ \]")
    contents, _ = read_until(logfile, pattern, starting_position=11)
    expected = ("[\\] a WIP task\n"
                "Just some additional clarifications\n"
                "\n"
                "[o] a scheduled task [$TOMORROW$]\n")
    assert contents == expected


def test_read_until_index(logfile):
    pattern = re.compile(r"^Just")
    _, index = read_until(logfile, pattern)
    assert index == 26


def test_pattern_not_found(logfile):
    pattern = re.compile(r"^NOT THERE")
    with pytest.raises(ValueError):
        _, _ = read_until(logfile, pattern)


# read_section

def test_read_section(tasklist_file):
    contents = read_section(tasklist_file, 'THIS WEEK')
    expected = ("[ ] a task with subtasks\n"
                "\t[ ] first thing\n"
                "\tclarification of first thing\n"
                "\t[ ] second thing\n")
    assert contents == expected


def test_read_section_empty(tasklist_file):
    contents = read_section(tasklist_file, 'THIS MONTH')
    expected = ""
    assert contents == expected


def test_read_section_missing(tasklist_file):
    with pytest.raises(ValueError):
        contents = read_section(tasklist_file, 'THIS DECADE')


# add_to_section

def test_add_to_section(tasklist_file):
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
                "\t[ ] first thing\n"
                "\tclarification of first thing\n"
                "\t[ ] second thing\n"
                "THIS MONTH:\n"
                "\n"
                "UNSCHEDULED:\n"
                "[ ] another task\n")
    assert updated.read() == expected

