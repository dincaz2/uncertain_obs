from software.sfl_diagnoser.Diagnoser.Singelton import Singleton


class Experiment_Data:
    # __metaclass__ = SingletonMetaClass

    class __Experiment_Data:
        def __init__(self):
            self.TERMINAL_PROB = 0.7
            self.PRIORS = []
            self.BUGS = []
            self.POOL = {}
            self.ESTIMATED_POOL = {}
            self.COMPONENTS_NAMES = {}
            self.clear()

        def clear(self):
            self.PRIORS = []
            self.BUGS = []
            self.POOL = {}
            self.COMPONENTS_NAMES = {}

        def set_values(self, priors_arg, bugs_arg, pool_arg, components_arg, extimated_pool_arg=None):
            self.clear()
            self.PRIORS = priors_arg
            self.BUGS = bugs_arg
            self.POOL = pool_arg
            self.COMPONENTS_NAMES = components_arg
            self.ESTIMATED_POOL = extimated_pool_arg

        def get_named_bugs(self):
            return map(lambda id: Experiment_Data().COMPONENTS_NAMES[id], Experiment_Data().BUGS)

    # transform class into a singleton
    instance = None

    def __init__(self):
        if not Experiment_Data.instance:
            Experiment_Data.instance = Experiment_Data.__Experiment_Data()

    def __getattr__(self, name):
        return getattr(self.instance, name)
