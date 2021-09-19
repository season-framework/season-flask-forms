import season
import lesscpy
from six import StringIO
import pypugjs

class Model(season.core.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)
        config = framework.config.load("form")
        self.namespace = config.get("database", "form")
        self.tablename = config.get("table_form", "form")

    def api(self, id, version="master"):
        info = self.get(id=id, version=version)
        process_api = info['api']
        fn = {'__file__': 'season.form.Spawner', '__name__': 'season.form.Spawner', 'framework': self.framework}
        exec(compile(process_api, 'season.form.Spawner', 'exec'), fn)
        return fn
