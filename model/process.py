import season

class Model(season.core.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)
        config = framework.config.load("form")
        self.namespace = config.get("database", "form")
        self.tablename = config.get("table_process", "form_process")