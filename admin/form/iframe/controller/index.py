import season
import datetime

class Controller(season.interfaces.form.controller.admin):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.framework = framework

    def json_default(self, value):
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return ""

    def __default__(self, framework):
        config = self.config
        form_id = framework.request.segment.get(0, True)
        form = self.model.form.get(id=form_id, version="master")
        if len(form) == 0: 
            framework.response.abort(404)
        
        doc_id = framework.request.segment.get(1, f"dev-{form_id}")
        doc = self.model.docs.get(id=doc_id)
        if doc is None and doc_id.split("-")[0] == "dev":
            self.model.docs.create(form_id, form_version="master")

        doc = self.model.docs.data(doc_id)
        if doc is None: 
            framework.response.abort(401)
        
        doc_id = doc["id"]
        view = self.model.docs.render(doc_id)

        framework.response.render(config.theme.view, module=config.theme.module, view=view)
