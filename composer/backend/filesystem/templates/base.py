import abc
import re

from ..primitives import is_task

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

    title = None
    entry = None
    agenda = None
    periodicname = None
    tasklistfile = None
    periodicfile = None
    checkpointsfile = None

    def __init__(self, planner, start_date):
        self.load_context(planner, start_date)

    @abc.abstractmethod
    def _file_handle(self):
        """ Return the relevant file for the template class. """
        raise NotImplementedError

    @abc.abstractmethod
    def load_context(self, planner, start_date):
        """ Store any relevant context that may be needed in populating a
        logfile from a template.

        :param :class:`~composer.backend.filesystem.base.FilesystemPlanner`
            planner: The planner instance in connection with which log files
            are to be populated.
        :param :class:`datetime.date` start_date: The start date of the
            new period
        """
        self.tasklistfile = planner.tasklist.file
        self.start_date = start_date
        self.bullet_character = planner.preferred_bullet_char

    @abc.abstractmethod
    def build(self, **kwargs):
        """ Create a new log file for the current date by specifying a template
        and populating it with configured contents (like periodic tasks) for
        the relevant period.

        :returns str: The log file created from the template
        """
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
        """ Update an existing log file for the current date in relation to a
        specified template.

        :returns str: The updated log file
        """
        raise NotImplementedError


class ZeroTemplate(Template):
    def _file_handle(self):
        return ""

    def build(self, **kwargs):
        return ""

    def update(self):
        return ""
