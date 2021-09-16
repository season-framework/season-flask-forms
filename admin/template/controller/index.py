import season
import datetime

class Controller(season.interfaces.form.controller.admin):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('css/main.less')
        
    def __default__(self, framework):
        response = framework.response
        return response.redirect('list')

    def list(self, framework):
        self.js('js/list.js')
        search = framework.request.query()
        self.exportjs(search=search)
        return framework.response.render('list.pug')

    def editor(self, framework):
        self.js('js/editor.js')
        self.css('css/editor.css')
        id = framework.request.segment.get(0, True)
        info = self.model.template.get(id=id)

        if info is None:
            info = dict()
            info["displayname"] = "새로운 템플릿"
            newid = framework.lib.util.randomstring(16)
            res = self.model.template.get(id=newid)
            while res is not None:
                newid = framework.lib.util.randomstring(16)
                res = self.model.template.get(id=newid)
            info["id"] = newid
            info["draft"] = ""
            info["process"] = ""
            info["view"] = ""
            info["js"] = ""
            self.model.form.insert(info)
            framework.response.redirect("editor/" + newid)
        
        self.exportjs(id=id)
        framework.response.render('editor.pug')
