import season
import datetime

TEXT_API = """def build(framework, doc):
  return None

# 기본결재라인 지정
def approval_line(framework, doc):  
  return []

def process(framework, doc, resp):
  pass
  
def onsubmit(framework, doc, resp):
  pass

def onapprove(framework, doc, resp):
  pass

def onreject(framework, doc, resp):
  pass

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

  // 초기 변수 설정
  $scope.init = function() {
    $timeout();
  }

  // 결재시 데이터 저장을 위한 데이터 변환 포맷
  $scope.transform = function() {
    var data = angular.copy($scope.data);
    // TODO: data 변수들을 문자열로 변환해야함
    // data.date = moment(data.date).format("YYYY-MM-DD");
    return data;
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
        if 'topmenus' in self.config: self.topnav(self.config.topmenus)
        cate = framework.request.segment.get(0, None)
        self.js('js/list.js')
        search = framework.request.query()
        search['category'] = cate

        category = []
        try:
            category = self.config.category
        except:
            pass
        if cate is None:
            return framework.response.redirect('list/' + category[0])
        menus = []
        for c in category:
            menus.append({ 'title': c, 'url': f'/form/admin/list/{c}' , 'pattern': r'^/form/admin/list/' + c })
        self.nav(menus)

        self.exportjs(search=search)
        return framework.response.render('list.pug', category=cate)

    def editor(self, framework):
        self.js('js/editor.js')
        self.css('css/editor.css')
        app_id = framework.request.segment.get(0, True)
        info = self.model.form.get(id=app_id, version="master")

        category = []
        try:
            category = self.config.category
        except:
            pass

        cate = framework.request.query("category", category[0])

        if info is None:
            info = dict()
            info["title"] = "새로운 문서"
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
            info["publish"] = ""
            info["api"] = TEXT_API
            info["html"] = "<div></div>"
            info["html_view"] = "<div></div>"
            info["js"] = TEXT_JS
            info["css"] = ""
            info["status"] = "use"
            info["category"] = cate

            info["created"] = datetime.datetime.now()
            self.model.form.insert(info)
            framework.response.redirect("editor/" + newid)
        
        self.exportjs(app_id=app_id, category=category)
        framework.response.render('editor.pug', category=category)
