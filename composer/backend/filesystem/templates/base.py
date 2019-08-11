import abc

ABC = abc.ABCMeta('ABC', (object,), {})  # compatible with Python 2 *and* 3


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
            template = self.title
            template += "\n"
        if self.entry:
            template += self.entry
            template += "\n"
        template += "CHECKPOINTS:\n"
        for line in self.checkpointsfile:
            if line[:3] == '[ ]':
                template += line
        template += "\n"
        template += "AGENDA:\n"
        if self.agenda:
            template += self.agenda
            template += "\n"
        template += "\n"
        template += self.periodicname
        for line in self.periodicfile:
            if line[:3] == '[ ]':
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
