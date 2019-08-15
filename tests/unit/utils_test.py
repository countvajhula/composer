from composer.backend.filesystem.utils import (
    read_item,
    is_blank_line,
    is_wip_task,
    is_scheduled_task,
    is_section,
)

from .fixtures import logfile, empty_logfile  # noqa


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
