import abc
import re

from ..utils import is_task

ABC = abc.ABCMeta("ABC", (object,), {})  # compatible with Python 2 *and* 3


def _tidy_item(item):
    # TODO: need a test for a case where there are extra newlines in
    # template components, to prove that this helps by eliminating them
    extra_newlines = re.compile('\n{2}$')
    if item == '\n':
        item = ''
    elif extra_newlines.search(item):
        item = item.rstrip('\n')
        item += '\n'
    return item


class Template(ABC):

    planner = None
    title = None
    entry = None
    agenda = None
    periodicname = None
    tasklistfile = None
    periodicfile = None
    checkpointsfile = None

    def __init__(self, planner, next_day):
        self.planner = planner  # need this for mutating it at the end
        self.load_context(planner, next_day)

    @abc.abstractmethod
    def load_context(self, planner, next_day):
        self.tasklistfile = planner.tasklistfile
        self.next_day = next_day

    @abc.abstractmethod
    def build(self):
        template = ""
        if self.title:
            self.title = _tidy_item(self.title)
            template = self.title
            template += "\n"
        if self.entry:
            self.entry = _tidy_item(self.entry)
            template += self.entry
            template += "\n"
        template += "CHECKPOINTS:\n"
        for line in self.checkpointsfile:
            if is_task(line):
                template += line
        template += "\n"
        template += "AGENDA:\n"
        if self.agenda:
            self.agenda = _tidy_item(self.agenda)
            template += self.agenda
        template += "\n"
        template += self.periodicname
        for line in self.periodicfile:
            if is_task(line):
                template += line
        template += "\n"
        template += "NOTES:\n\n\n"
        template += "TIME SPENT ON PLANNER: "
        return template

    @abc.abstractmethod
    def update(self):
        raise NotImplementedError

    @abc.abstractmethod
    def write_existing(self):
        raise NotImplementedError

    @abc.abstractmethod
    def write_new(self):
        raise NotImplementedError
