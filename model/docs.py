import season
import datetime
import json
import lesscpy
from six import StringIO
import pypugjs

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

    def render(self, doc_id):
        framework = self.framework
        config = framework.config.load("form")

        o = "{"
        e = "}"

        model = season.stdClass()
        model.form = framework.model('form', module="form")

        doc = self.get(id=doc_id)
        if doc is None:
            return ""
        
        form_id = doc['form_id']
        form_version = doc['form_version']
        doc_status = doc['status']
        
        form = model.form.get(id=form_id, version=form_version)

        if form is None: 
            return ""

        form_title = form["title"]

        # 권한 확인
        docdata = self.data(doc_id)
        if docdata is None:
            return ""

        html = form["html_view"]
        if doc_status == 'draft': html = form["html"]
        try:
            pug = pypugjs.Parser(html)
            pug = pug.parse()
            pug = pypugjs.ext.jinja.Compiler(pug).compile()
            html = framework.response.template_from_string(pug)
        except:
            pass

        button = ""
        header = f"""
            <div class="container">
                <div class="info-form row first-child">
                    <div class="col-md-2"> 
                        <h4>문서번호</h4>
                    </div>
                    <div class="col-md-6"> 
                        <div class="p-1">{o}{o}doc.id{e}{e}</div>
                    </div>
                    <div class="col-md-2"> 
                        <h4>결재상태</h4>
                    </div>
                    <div class="col-md-2"> 
                        <div class="p-1">{o}{o}statusmap[doc.status]{e}{e}</div>
                    </div>
                </div>
                <div class="info-form row">
                    <div class="col-md-2"> 
                    <h4>신청자</h4>
                    </div>
                    <div class="col-md-10"> 
                    <div class="p-1">{o}{o}doc.user.name_ko{e}{e}</div>
                    </div>
                </div>
                <div class="info-form row">
                    <div class="col-md-2"> 
                    <h4>신청일자</h4>
                    </div>
                    <div class="col-md-10"> 
                    <div class="p-1">{o}{o}doc.timestamp{e}{e}</div>
                    </div>
                </div>
                <div class="info-form row">
                    <div class="col-md-2"> 
                        <h4>문서제목</h4>
                    </div>
                    <div class="col-md-10"> 
                        <div class="p-1">{o}{o}doc.title{e}{e}</div>
                    </div>
                </div>
            </div> 
        """

        procstatus = ""
        response_message = ""

        if doc_status == 'draft':
            button = f"""
                <button class="btn btn-light pr-4 pl-4 ml-2" ng-click="event.delete()"><i class="mr-2 fas fa-times"></i>삭제</button>
                <button class="btn btn-light pr-4 pl-4 ml-2" ng-click="event.save()"><i class="mr-2 fas fa-save"></i>임시저장</button>
                <button class="btn btn-dark pr-4 pl-4 ml-2" ng-click="event.submit()"><i class="mr-2 fas fa-paper-plane"></i>제출</button>
            """
            
            header = f"""
                <div class="container">
                    <div class="info-form row first-child">
                        <div class="col-md-2"> 
                            <h4>문서번호</h4>
                        </div>
                        <div class="col-md-6"> 
                            <div class="p-1">{o}{o}doc.id{e}{e}</div>
                        </div>
                        <div class="col-md-2"> 
                            <h4>결재상태</h4>
                        </div>
                        <div class="col-md-2"> 
                            <div class="p-1">{o}{o}statusmap[doc.status]{e}{e}</div>
                        </div>
                    </div>
                    <div class="info-form row">
                        <div class="col-md-2"> 
                        <h4>신청자</h4>
                        </div>
                        <div class="col-md-10"> 
                        <div class="p-1">{o}{o}doc.user.name_ko{e}{e}</div>
                        </div>
                    </div>
                    <div class="info-form row">
                        <div class="col-md-2"> 
                        <h4>신청일자</h4>
                        </div>
                        <div class="col-md-10"> 
                        <div class="p-1">{o}{o}doc.timestamp{e}{e}</div>
                        </div>
                    </div>
                    <div class="info-form row">
                        <div class="col-md-2"> 
                            <h4>문서제목</h4>
                        </div>
                        <div class="col-md-10"> 
                            <input class="form-control" type="text" ng-model="doc.title" placeholder="문서제목"/>
                        </div>
                    </div>
                </div> 
            """

        if docdata["action"] == "process":
            response_message = f"""
                <div class="container">
                    <div class="info-form row first-child bg-dark-lt">
                        <div class="col-md-2">
                        <h4>응답메시지</h4>
                        </div>
                        <div class="col-md-10"> 
                        <textarea class="form-control" rows="5" ng-model="doc.response"></textarea>
                        </div>
                    </div>
                </div>
            """

            button = f"""
                <button class="btn btn-light pr-4 pl-4 ml-2" ng-click="event.reject()"><i class="mr-2 fas fa-times"></i>반려</button>
                <button class="btn btn-dark pr-4 pl-4 ml-2" ng-click="event.approve()"><i class="mr-2 fas fa-check-circle"></i>승인</button>
            """

        if doc_status != 'draft':
            procstatus = f"""
                <div class="container">
                    <div class="info-form row first-child">
                        <div class="col-md-2">
                        <h4>결재현황</h4>
                        </div>
                        <div class="col-md-10">
                        <div class="row row-deck row-cards" ng-if="doc.approval_line_info.length == 0">
                            <div class="col-md-3">
                            <div class="card mb-4">
                                <div class="card-header">
                                <div class="card-title">결재없음</div>
                                </div>
                                <div class="card-body text-left" style="height: 120px; overflow: auto;">
                                <div class="text-left">결재가 필요 없는 문서입니다</div>
                                </div>
                                <div class="card-footer">
                                <button class="btn btn-green btn-block">결재없음</button>
                                </div>
                            </div>
                            </div>
                        </div>
                        <div class="row mt-4" ng-if="doc.approval_line_info.length &gt; 0">
                            <div class="col-md-3">
                                <div class="card mb-4">
                                    <div class="card-header">
                                        <div class="card-title">{o}{o}doc.user.name_ko{e}{e}</div>
                                    </div>
                                    <div class="card-body text-left" style="height: 120px; overflow: auto;">
                                        문서 제출
                                    </div>
                                    <div class="card-footer">
                                        <button class="btn btn-secondary btn-block">제출</button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3" ng-repeat="line in doc.approval_line_info">
                                <div class="card mb-4" ng-repeat="approval in line">
                                    <div class="ribbon ribbon-top ribbon-bookmark bg-green" ng-if="approval.status.status == 'ready' && approval.user.id != doc.user_id"></div>
                                    <div class="card-header">
                                        <div class="card-title">{o}{o}approval.user.name_ko{e}{e}</div>
                                    </div>
                                    <div class="card-body text-left" style="height: 120px; overflow: auto;">
                                        <div class="text-left" ng-if="approval.user.id != doc.user_id && ['reject', 'finish'].includes(approval.status.status)">{o}{o}approval.status.response{e}{e}</div>
                                        <div class="text-left" ng-if="approval.user.id != doc.user_id && approval.status.status == 'ready'">결재 대기중 입니다</div>
                                        <div class="text-left" ng-if="approval.user.id != doc.user_id && approval.status.status == 'cancel'">결재가 취소되었습니다</div>
                                        <div class="text-left" ng-if="approval.user.id == doc.user_id">자동승인됨</div>
                                    </div>
                                    <div class="card-footer" ng-if="approval.user.id == doc.user_id">
                                    <button class="btn btn-green btn-block">자동승인</button>
                                    </div>
                                    <div class="card-footer" ng-if="approval.user.id != doc.user_id">
                                        <button class="btn btn-secondary btn-block" ng-if="approval.status.status == 'ready'">결재대기</button>
                                        <button class="btn btn-green btn-block" ng-if="approval.status.status == 'finish'">승인</button>
                                        <button class="btn btn-red btn-block" ng-if="approval.status.status == 'reject'">반려</button>
                                        <button class="btn btn-secondary btn-block" ng-if="approval.status.status == 'cancel'">취소</button>
                                        <button class="btn btn-secondary btn-block" ng-if="!approval.status">대기</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        </div>
                    </div>
                </div>
            """

        if button == "" and docdata['user_id'] == config.uid(framework) and docdata['status'] == 'process':
            button = f"""
                <button class="btn btn-light pr-4 pl-4 ml-2" ng-click="event.cancel()"><i class="mr-2 fas fa-undo"></i>회수</button>
            """
        
        html = f"""
            <div class="container" id='form-controller' ng-controller='form-container-controller'>
                <div class="page-header">
                    <div class="row align-items-center">
                        <div class="col-auto">
                            <div class="page-pretitle">전자결재</div>
                            <h2 class="page-title">{form_title}</h2>
                        </div>
                        <div class="col-auto ml-auto d-print-none">
                            {button}
                        </div>
                    </div>
                </div>
            
                {header}

                <div id='form-{form_id}' ng-controller='form-{form_id}'>
                    {html}
                </div>

                {procstatus}

                {response_message}
                
                <div class="container mt-4 text-center">{button}</div>

            </div>
        """

        js = form["js"]
        
        css = form["css"]
        css = f"#form-{form_id} {o} {css} {e}"
        css = lesscpy.compile(StringIO(css), minify=True)
        css = str(css)
        
        view = f"""
        {html}
        <script src='/resources/form/season-form.js'></script>
        <script>
            var sform = season_form('{form_id}', '{doc_id}', '{form_version}'); 
            
            try {o}
                app.controller('form-container-controller', form_container_controller);
            {e} catch (e) {o}
                app.controller('form-container-controller', function() {o}{e});
            {e}

            function __init_{form_id}() {o}
                {js}; 
                try {o} 
                    app.controller('form-{form_id}', form_controller); 
                {e}  catch (e) {o} 
                    app.controller('form-{form_id}', function() {o} {e} ); 
                {e} 
            {e}; 
            __init_{form_id}();
        </script>
        <style>{css}</style>
        """
        
        return view
        
    def approval_line(self, doc_id):
        framework = self.framework
        config = framework.config.load("form")

        doc = self.get(id=doc_id)
        if doc is None:
            return []

        model_form = framework.model("form", module="form")
        formapi = model_form.api(doc["form_id"], doc["form_version"])
        approval_line = json.loads(doc["approval_line"])

        usercheck = dict()
        usercheck[config.uid(framework)] = True
        
        doc = self.data(doc_id)
        aline = formapi['approval_line'](framework, doc)
        for i in range(len(aline)):
            _line = []
            for j in range(len(aline[i])):
                if aline[i][j] is not None:
                    if aline[i][j] in usercheck:
                        continue
                    usercheck[aline[i][j]] = True
                    _line.append(aline[i][j])
            if len(_line) > 0:
                approval_line.append(_line)
            
        return approval_line

    def create(self, form_id, form_version=None, user_id=None):
        framework = self.framework   
        config = framework.config.load("form")

        model_form = framework.model("form", module="form")

        if user_id is None: 
            user_id = config.uid(framework)

        # 신규 문서 작성시 기초자료
        form = None
        form = model_form.get(id=form_id, version=form_version)
        if form is None:
            form = model_form.rows(id=form_id, orderby="`version` DESC")
            if len(form) > 1: 
                form = form[1]
        
        def id_builder():
            newid = datetime.datetime.now().strftime("%Y") + "-" + form['category'] + "-" + framework.lib.util.randomstring(12)
            res = self.get(id=newid)
            while res is not None:
                newid = datetime.datetime.now().strftime("%Y") + "-" + form['category'] + "-" + framework.lib.util.randomstring(12)
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
        approval_line = "[]"
        doc['approval_line'] = approval_line
        
        self.upsert(doc)
        doc = self.get(id=doc_id)
        return doc

    def data(self, doc_id, user_id=None):
        framework = self.framework
        config = framework.config.load("form")
        
        model_form = framework.model("form", module="form")
        model_process = framework.model("process", module="form")

        document_acl = config.get('document_acl', None)
        userinfo = config.get('userinfo', None)
        if user_id is None: 
            user_id = config.uid(framework)

        # 문서 정보 불러오기
        doc = self.get(id=doc_id)
        if doc is None:
            return None

        form_id = doc['form_id']
        version = doc['form_version']

        if userinfo is not None: 
            doc['user'] = userinfo(framework, doc['user_id'])
        else: 
            doc['user'] = {"id": doc['user_id']}
    
        # 결재라인 자료형 변환
        doc["approval_line_info"] = json.loads(doc["approval_line"])
        doc["approval_line"] = json.loads(doc["approval_line"])
        
        doc['action'] = model_process.get(doc_id=doc_id, user_id=user_id, status="ready")
        if doc['action'] is not None: doc['action'] = "process"
        else: doc['action'] = "view"

        # 작성안 불러오기
        draft = model_process.get(doc_id=doc_id, status="draft")

        # 초안이 없는 경우 작성자인 경우 초안 자동 생성
        if doc['user_id'] == user_id and draft is None:
            draft = dict()
            draft["doc_id"] = doc_id
            draft["user_id"] = user_id
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

        # 결재 상황 불러오기
        for i in range(len(doc["approval_line_info"])):
            for j in range(len(doc["approval_line_info"][i])):
                uid = doc["approval_line_info"][i][j]
                obj = dict()
                obj['user'] = framework.model("mysql/users").get(id=uid)
                if userinfo is not None: obj['user'] = userinfo(framework, uid)
                else: obj['user'] = {"id": uid}
                status = model_process.get(doc_id=doc_id, user_id=uid)
                if status is not None:
                    try:
                        status['data'] = json.loads(status['data'])
                    except:
                        status['data'] = {}
                else:
                    status = False
                obj['status'] = status
                doc["approval_line_info"][i][j] = obj

        formapi = model_form.api(form_id, version)
        doc["build"] = formapi['build'](framework, doc)

        # 문서 권한 확인
        if document_acl is not None:
            if document_acl(framework, doc):
                return doc
        
        authorized = model_process.get(doc_id=doc_id, user_id=user_id)
        if doc['user_id'] != user_id and authorized is None:
            return None

        return doc