import season
import json

class Controller(season.interfaces.form.controller.api):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.framework = framework

        # acl
        doc_id = framework.request.segment.get(0, True)
        doc = self.model.docs.data(doc_id)
        if doc is None: self.status(404)

        formapi = self.model.form.api(doc["form_id"], doc["form_version"])
        self.doc = doc
        self.formapi = formapi

    def __default__(self, framework):
        framework.response.abort(404)

    def __error__(self, framework):
        self.status(500, "오류가 발생하였습니다.")

    def delkey(self, obj, key):
        if key in obj:
            del obj[key]

    # 임시저장
    def draft(self, framework):
        data = dict()
        data["id"] = self.doc["id"]
        data["title"] = framework.request.query("title", "")
        self.model.docs.upsert(data)

        data = dict()
        data["doc_id"] = self.doc["id"]
        data["user_id"] = self.config.uid(framework)
        data["status"] = "draft"
        data["data"] = framework.request.query("data", "{}")
        data["response"] = ""
        self.model.process.upsert(data)
        self.status(200, "저장되었습니다.")

    # 제출
    def submit(self, framework):
        formapi = self.formapi
        doc = self.doc

        data = dict()
        data["id"] = doc["id"]
        data["title"] = framework.request.query("title", "")
        self.model.docs.upsert(data)

        approval_line = self.model.docs.approval_line(self.doc["id"])
        self.doc["approval_line"] = approval_line
        formapi["onsubmit"](framework, doc, self.status)

        draft = self.doc["draft"]
        self.delkey(draft, "timestamp")
        draft['status'] = "ready"
        
        createcount = 0
        for item in approval_line:
            for uid in item:
                if uid == self.config.uid(framework): continue
                draft['data'] = json.dumps(draft['data'])
                draft['user_id'] = uid
                self.model.process.upsert(draft)
                createcount = createcount + 1
            if createcount > 0:
                break
        
        data = dict()
        data["id"] = self.doc["id"]
        data["approval_line"] = json.dumps(approval_line)
        if createcount == 0:
            data["status"] = "finish"
            formapi["onfinish"](framework, doc, self.status)
        else:
            data["status"] = "process"
        self.model.docs.upsert(data)
        
        self.status(200, "저장되었습니다.")

    # 승인
    def approve(self, framework):
        formapi = self.formapi
        doc = self.doc

        data = dict()
        data["doc_id"] = doc["id"]
        data["user_id"] = self.config.uid(framework)
        data["status"] = "finish"
        data["response"] = framework.request.query("response", "")
        self.model.process.upsert(data)

        aline = doc["approval_line_info"]
        for i in range(len(aline)):
            allcount = len(aline[i])
            approvecount = 0
            iscreated = False
            try:
                for j in range(len(aline[i])):
                    auser = aline[i][j]["user"]["id"]
                    if auser == self.config.uid(framework):
                        approvecount += 1
                        continue

                    if aline[i][j]["status"] == False:
                        iscreated = True
                        draft = self.doc["draft"]
                        draft['status'] = "ready"
                        draft['user_id'] = auser
                        draft['data'] = json.dumps(draft['data'])
                        self.model.process.upsert(draft)
                    else:
                        status = aline[i][j]["status"]["status"]
                        if status == "finish":
                            approvecount += 1
            except:
                pass

            if approvecount == allcount and i == len(aline) - 1:
                data = dict()
                data["id"] = doc["id"]
                data["status"] = "finish"
                formapi["onfinish"](framework, doc, self.status)
                self.model.docs.upsert(data)
                break

            if iscreated:
                break
            
            if approvecount != allcount:
                break

        formapi["onapprove"](framework, doc, self.status)
        self.status(200, "승인됨")

    # 반려
    def reject(self, framework):
        formapi = self.formapi
        doc = self.doc

        data = dict()
        data["doc_id"] = doc["id"]
        data["user_id"] = self.config.uid(framework)
        data["status"] = "reject"
        data["response"] = framework.request.query("response", "")
        self.model.process.upsert(data)

        data = dict()
        data["id"] = doc["id"]
        data["status"] = "reject"
        self.model.docs.upsert(data)

        aline = doc["approval_line_info"]
        iscancel = False
        for i in range(len(aline)):
            try:
                for j in range(len(aline[i])):
                    auser = aline[i][j]["user"]["id"]
                    if auser == self.config.uid(framework):
                        iscancel = True
                        continue
                
                if iscancel:
                    for j in range(len(aline[i])):
                        auser = aline[i][j]["user"]["id"]
                        if auser == self.config.uid(framework):
                            continue

                        draft = self.doc["draft"]
                        draft['status'] = "cancel"
                        draft['user_id'] = auser
                        draft['data'] = json.dumps(draft['data'])
                        self.model.process.upsert(draft)
            except:
                pass

        formapi["onreject"](framework, doc, self.status)
        self.status(200, True)

    # 회수
    def cancel(self, framework):
        doc = self.doc

        if doc['user_id'] != self.config.uid(framework):
            self.status(401, True)

        data = dict()
        data["id"] = doc["id"]
        data["status"] = "cancel"
        self.model.docs.upsert(data)

        draft = self.doc["draft"]
        draft['data'] = json.dumps(draft['data'])
        
        aline = doc["approval_line_info"]
        for i in range(len(aline)):
            try:
                for j in range(len(aline[i])):
                    auser = aline[i][j]["user"]["id"]
                    process = self.model.process.get(user_id=auser, doc_id=doc['id'])
                    if process is not None and process['status'] != 'ready':
                        continue
                    
                    draft['status'] = "cancel"
                    draft['user_id'] = auser
                    self.model.process.upsert(draft)
            except:
                pass

        self.status(200, True)