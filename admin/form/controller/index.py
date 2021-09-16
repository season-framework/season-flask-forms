import season
import datetime

TEXT_API = """## acl
def acl(framework, doc):
    return False
    
# build default data
def build(framework, doc):
    return None

# set base approval line
def approval_line(framework, doc):  
    return []

# after submit event
def onsubmit(framework, doc, resp):
    pass

# on every approval event
def onapprove(framework, doc, resp):
    pass

# on reject event
def onreject(framework, doc, resp):
    pass

# on finish event
def onfinish(framework, doc, resp):
    pass
"""

TEXT_JS = """var form_controller = function ($sce, $scope, $timeout) {
    sform.init(function (doc) {
        $scope.data = sform.data();
        $scope.doc = doc;
        $scope.build = doc.build;
        sform.set_scope($scope);
        $scope.init();
    });

    // data transform for save
    $scope.transform = function() {
        var data = angular.copy($scope.data);
        // TODO: transform obj to string format
        // data.date = moment(data.date).format("YYYY-MM-DD");
        return data;
    }

    // create title function. if not set, default ""
    $scope.title = function () {
        var title = "";
        return title;
    }

    // initialize data
    $scope.init = function() {
        $timeout();
    }
}
"""

class Controller(season.interfaces.form.controller.admin):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('css/main.less')
        
    def __default__(self, framework):
        response = framework.response
        return response.redirect('list')

    def list(self, framework):
        cate = framework.request.segment.get(0, None)
        self.js('js/list.js')
        search = framework.request.query()
        search['category'] = cate

        category = []
        try:
            category = self.config.category
        except:
            pass
        
        menus = [{'title' : 'Total', 'url': '/form/admin/form/list'}]
        for c in category:
            menus.append({ 'title': c, 'url': f'/form/admin/form/list/{c}' , 'pattern': r'^/form/admin/form/list/' + c })
        self.subnav(menus)

        self.exportjs(search=search)
        return framework.response.render('list.pug', category=cate)

    def editor(self, framework):
        self.js('js/editor.js')
        self.css('css/editor.css')
        app_id = framework.request.segment.get(0, True)
        version = framework.request.query("version", "master")
        info = self.model.form.get(id=app_id, version=version)

        category = []
        try:
            category = self.config.category
        except:
            pass

        cate = framework.request.query("category", category[0])

        if info is None:
            info = dict()
            info["title"] = "New Forms"
            info["user_id"] = self.config.uid(framework)
            newid = framework.lib.util.randomstring(32)
            res = self.model.form.get(id=newid)
            while res is not None:
                newid = framework.lib.util.randomstring(32)
                res = self.model.form.get(id=newid)
            info["id"] = newid
            info["namespace"] = newid
            info["status"] = "ready"
            info["version"] = "master"
            info["publish"] = "draft"
            info["api"] = TEXT_API
            info["html"] = ".container"
            info["html_view"] = ".container"
            info["js"] = TEXT_JS
            info["css"] = ""
            info["status"] = "use"
            info["category"] = cate
            info["theme"] = "default"

            info["created"] = datetime.datetime.now()
            self.model.form.insert(info)
            framework.response.redirect("editor/" + newid)
        
        templates = self.model.template.rows()

        self.exportjs(app_id=app_id, category=category, version=info["version"])
        framework.response.render('editor.pug', category=category, templates=templates)
