class ModelWrapper(dict):

    def __init__(self, **kwargs):
        for arg, value in kwargs.items():
            self[arg] = value

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value