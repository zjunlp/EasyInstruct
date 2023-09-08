class BaseCleaner:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def clean(self):
        raise NotImplementedError