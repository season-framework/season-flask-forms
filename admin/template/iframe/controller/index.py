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
        template_id = framework.request.segment.get(0, True)
        template_status = framework.request.segment.get(1, "draft")
        template = self.model.template.get(id=template_id)
        if template is None: framework.response.abort(404)
        
        kwargs = dict()
        kwargs['doc_id'] = "dummy"
        kwargs['form_id'] = "dummy"
        kwargs['form_version'] = "master"
        kwargs['form_title'] = "Sample Document"
        kwargs['view'] = "<div style='width: 100%; height: 400px; background: #eee; text-align: center; padding-top: 190px;'>Form Content</div>"
        kwargs['js'] = ""
        kwargs['css'] = ""
        kwargs['allow_cancel'] = False

        # build view
        view = self.model.template.render(template_id, template_status, **kwargs)
        framework.response.render(config.theme.view, module=config.theme.module, view=view)