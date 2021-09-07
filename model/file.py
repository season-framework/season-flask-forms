import season

class Model(season.core.interfaces.model.FileSystem):
    def __init__(self, framework):
        super().__init__(framework)
        self.namespace = 'form'
