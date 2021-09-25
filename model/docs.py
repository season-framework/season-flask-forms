import season
import datetime
import json
import lesscpy
from six import StringIO
import pypugjs

dummy = '{"code":200,"data":{"id":"dummy","form_id":"dummy","form_version":"master","user_id":"john","title":"2021-09-15","approval_line":[["john"],["stella","jessy"],["jane"],["proin"]],"status":"process","timestamp":"2021-09-15 22:06:40","user":{"id":"john","name":"John Doe"},"action":"view","draft":{"doc_id":"dummy","user_id":"john","seq":0,"subseq":0,"status":"draft","data":{"date":"2021-09-15","list":[{"user":"stella"},{"user":"jessy"}],"price":22222},"response":"","timestamp":"2021-09-15 22:06:39"},"approval_line_info":[[{"doc_id":"dummy","user_id":"john","seq":0,"subseq":0,"status":"draft","data":{"date":"2021-09-15","list":[{"user":"stella"},{"user":"jessy"}],"price":22222},"response":"","timestamp":"2021-09-15 22:06:39","user":{"id":"john","name":"John Doe"}}],[{"doc_id":"dummy","user_id":"stella","seq":10,"subseq":0,"status":"ready","data":{"date":"2021-09-15","list":[{"user":"stella"},{"user":"jessy"}],"price":22222},"response":"","timestamp":"2021-09-15 22:06:40","user":{"id":"stella","name":"Stella Kim"}},{"doc_id":"dummy","user_id":"jessy","seq":10,"subseq":1,"status":"ready","data":{"date":"2021-09-15","list":[{"user":"stella"},{"user":"jessy"}],"price":22222},"response":"","timestamp":"2021-09-15 22:06:40","user":{"id":"jessy","name":"Jessy"}}],[{"doc_id":"dummy","user_id":"jane","seq":20,"subseq":0,"status":"pending","data":{"date":"2021-09-15","list":[{"user":"stella"},{"user":"jessy"}],"price":22222},"response":"","timestamp":"2021-09-15 22:06:40","user":{"id":"jane","name":"Jane"}}],[{"doc_id":"dummy","user_id":"proin","seq":30,"subseq":0,"status":"pending","data":{"date":"2021-09-15","list":[{"user":"stella"},{"user":"jessy"}],"price":22222},"response":"","timestamp":"2021-09-15 22:06:40","user":{"id":"proin","name":"Yeonghun Chae"}}]],"build":{"users":[{"id":"proin","name":"Yeonghun Chae"},{"id":"stella","name":"Stella Kim"},{"id":"jessy","name":"Jessy"},{"id":"jane","name":"Jane"},{"id":"john","name":"John Doe"}]}}}'
dummy = json.loads(dummy)["data"]

class Model(season.core.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)
        config = framework.config.load("form")
        self.namespace = config.get("database", "form")
        self.tablename = config.get("table_docs", "form_docs")

    def api(self, doc_id):
        framework = self.framework
        model = season.stdClass()
        model.form = framework.model('form', module="form")
        doc = self.get(id=doc_id)
        form_id = doc['form_id']
        form_version = doc['form_version']
        return model.form.api(form_id, form_version)

    def compile_pug(self, html):
        framework = self.framework
        config = framework.config.load("form")
        try:
            pugconfig = {}
            if config.pug is not None: pugconfig = config.pug
            pug = pypugjs.Parser(html)
            pug = pug.parse()
            html = pypugjs.ext.jinja.Compiler(pug, **pugconfig).compile()
        except Exception as e:
            pass
        return html

    def readfile(self, path):
        try:
            f = open(path, 'r')
            data = f.read()
            f.close()
            return data
        except:
            return ""

    def render(self, doc_id):
        framework = self.framework
        config = framework.config.load("form")

        o = "{"
        e = "}"

        model = season.stdClass()
        model.form = framework.model('form', module="form")
        model.template = framework.model('template', module="form")

        doc = self.get(id=doc_id)
        if doc is None:
            return ""
        
        form_id = doc['form_id']
        form_version = doc['form_version']
        doc_status = doc['status']
        
        form = model.form.get(id=form_id, version=form_version)
        
        # is valid form
        if form is None: 
            return ""
            
        # check access level
        docdata = self.data(doc_id)
        if docdata is None:
            return ""

        # find status
        if doc_status != 'draft': 
            if docdata["action"] == "process":
                doc_status = "process"
            else:
                doc_status = "view"
        
        # select view by level
        html = form["html_view"]
        if doc_status == 'draft':
            html = form["html"]
        html = self.compile_pug(html)
        html = framework.response.template_from_string(html)

        js = form["js"]
        css = form["css"]
        css = f"#form-{form_id} {o} {css} {e}"
        css = lesscpy.compile(StringIO(css), minify=True)
        css = str(css)
                
        # form variables
        kwargs = dict()
        kwargs['doc_id'] = doc_id
        kwargs['form_id'] = form_id
        kwargs['form_version'] = form_version
        kwargs['form_title'] = form["title"]
        kwargs['view'] = html
        kwargs['js'] = js
        kwargs['css'] = css
        kwargs['allow_cancel'] = False
        if docdata['user_id'] == config.uid(framework) and docdata['status'] == 'process':
            kwargs['allow_cancel'] = True

        # build view
        return model.template.render(form["theme"], doc_status, **kwargs)
        
    def approval_line(self, doc_id):
        doc = self.data(doc_id)
        return doc['approval_line']

    def create(self, form_id, form_version=None, user_id=None):
        framework = self.framework   
        config = framework.config.load("form")

        model_form = framework.model("form", module="form")

        if user_id is None: 
            user_id = config.uid(framework)

        # base info for new doc
        form = None
        form = model_form.get(id=form_id, version=form_version)
        if form is None:
            form = model_form.rows(id=form_id, orderby="`version` DESC")
            if len(form) > 1: 
                form = form[1]
        
        # new doc id creator
        def id_builder():
            def _genid(framework, form):
                return datetime.datetime.now().strftime("%Y") + "-" + form['category'] + "-" + framework.lib.util.randomstring(12)
            if config.id_builder is not None: genid = config.id_builder 
            else: genid = _genid
            newid = genid(framework, form)
            res = self.get(id=newid)
            while res is not None:
                newid = genid(framework, form)
                res = self.get(id=newid)
            return newid

        if form_version == 'master':
            doc_id = "dev-" + form['namespace']
        else:
            doc_id = id_builder()

        doc = dict()
        doc['id'] = doc_id
        doc['form_id'] = form_id
        doc['user_id'] = user_id
        doc['form_version'] = form["version"]
        doc['user_id'] = user_id
        doc['status'] = 'draft'
        doc['approval_line'] = "[]"
        
        self.upsert(doc)
        doc = self.get(id=doc_id)
        return doc

    def data(self, doc_id, user_id=None):
        framework = self.framework

        if doc_id == "dummy":
            return dummy

        config = framework.config.load("form")
        model_form = framework.model("form", module="form")
        model_process = framework.model("process", module="form")

        # load options
        document_acl = config.get('document_acl', None)
        userinfofn = config.get('userinfo', None)

        if user_id is None: 
            user_id = config.uid(framework)

        # load doc info
        doc = self.get(id=doc_id)
        if doc is None:
            return None

        form_id = doc['form_id']
        version = doc['form_version']
        formapi = model_form.api(form_id, version)

        # load doc user info 
        try:
            doc['user'] = userinfofn(framework, doc['user_id'])
        except:
            doc['user'] = {"id": doc['user_id'], "name": doc['user_id']}
            
        # load access level info
        doc['action'] = model_process.get(doc_id=doc_id, user_id=user_id, status="ready")
        if doc['action'] is not None: doc['action'] = "process"
        else: doc['action'] = "view"

        # load draft info
        draft = model_process.get(doc_id=doc_id, status="draft")

        # if draft not exist
        if doc['user_id'] == user_id and draft is None:
            draft = dict()
            draft["doc_id"] = doc_id
            draft["user_id"] = user_id
            draft["seq"] = 0
            draft["subseq"] = 0
            draft["status"] = "draft"
            draft["data"] = "{}"
            draft["response"] = ""
            model_process.upsert(draft)
            draft = model_process.get(doc_id=doc_id, status="draft")
        try:
            draft["data"] = json.loads(draft["data"])
        except:
            draft["data"] = {}
        doc["draft"] = draft

        # load process
        processes = model_process.rows(doc_id=doc_id, orderby="`seq` ASC, `subseq` ASC")
        pre_seq = None
        tmp = []
        lineobj = []
        for proc in processes:
            try:
                proc['data'] = json.loads(proc['data'])
            except:
                proc['data'] = {}
            try:
                proc['user'] = userinfofn(framework, proc['user_id'])
            except:
                proc['user'] = {"name": proc['user_id']}
            proc['user']['id'] = proc['user_id']
            if pre_seq != proc['seq']:
                if len(lineobj) > 0: tmp.append(lineobj)
                lineobj = []
            lineobj.append(proc)
            pre_seq = proc['seq']
        if len(lineobj) > 0: tmp.append(lineobj)
        doc["approval_line_info"] = tmp

        # load default approval lines
        approval_line = [[user_id]]

        def check_user(uid):
            try:
                exists = config.userinfo(framework, uid)
            except:
                exists = None
            if exists is not None: 
                return True
            return False

        # load additional approval line
        try:
            additional_approval_line = json.loads(doc["approval_line"])
        except:
            additional_approval_line = []

        for i in range(len(additional_approval_line)):
            _line = []
            for j in range(len(additional_approval_line[i])):
                if additional_approval_line[i][j] is not None:
                    uid = additional_approval_line[i][j]
                    if check_user(uid):
                        _line.append(uid)
            if len(_line) > 0:
                approval_line.append(_line)
        
        # required approval line
        required_approval_line = formapi['approval_line'](framework, doc)
        for i in range(len(required_approval_line)):
            _line = []
            for j in range(len(required_approval_line[i])):
                if required_approval_line[i][j] is not None:
                    uid = required_approval_line[i][j]
                    if check_user(uid):
                        _line.append(uid)
            if len(_line) > 0:
                approval_line.append(_line)

        if len(doc["approval_line_info"]) >= len(approval_line):
            approval_line = []
            for i in range(len(doc["approval_line_info"])):
                _line = []
                for j in range(len(doc["approval_line_info"][i])):
                    uid = doc["approval_line_info"][i][j]["user_id"]
                    _line.append(uid)
                if len(_line) > 0:
                    approval_line.append(_line)
                
        doc["approval_line"] = approval_line
        doc["build"] = formapi['build'](framework, doc)

        # check customized document access level
        if document_acl is not None:
            if document_acl(framework, doc):
                return doc
        
        # formapi acl
        if 'acl' in formapi:
            try:
                if formapi['acl'](framework, doc):
                    return doc
            except:
                pass

        # check authorized
        authorized = model_process.get(doc_id=doc_id, user_id=user_id)
        if doc['user_id'] != user_id and authorized is None:
            return None

        return doc