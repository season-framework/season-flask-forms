import season
import json

class Controller(season.interfaces.form.controller.api):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.framework = framework

        # check access level
        doc_id = framework.request.segment.get(0, True)
        doc = self.model.docs.data(doc_id)
        if doc is None: self.status(404)

        formapi = self.model.form.api(doc["form_id"], doc["form_version"])
        self.doc = doc
        self.formapi = formapi

    def __default__(self, framework):
        framework.response.abort(404)

    def __error__(self, framework, e):
        self.status(500, framework.dic.form.API.ERROR)

    def delkey(self, obj, key):
        if key in obj:
            del obj[key]

    # save draft
    def draft(self, framework):
        data = dict()
        data["id"] = self.doc["id"]
        data["title"] = framework.request.query("title", "")
        try: data["approval_line"] = json.dumps(framework.request.query("title", []), default=season.json_default)
        except: data["approval_line"] = "[]"
        self.model.docs.upsert(data)
        
        data = dict()
        data["doc_id"] = self.doc["id"]
        data["user_id"] = self.config.uid(framework)
        data["seq"] = 0
        data["subseq"] = 0
        data["status"] = "draft"
        data["data"] = framework.request.query("data", "{}")
        data["response"] = ""
        if type(data["data"]) != str: data["data"] = json.dumps(data["data"], season.json_default)
        self.model.process.upsert(data)

        self.status(200, framework.dic.form.API.SAVED)

    # Submit
    def submit(self, framework):
        formapi = self.formapi
        doc = self.doc

        data = dict()
        data["title"] = framework.request.query("title", "")
        try: data["approval_line"] = json.dumps(framework.request.query("title", []), default=season.json_default)
        except: data["approval_line"] = "[]"
        self.model.docs.update(data, id=doc["id"])

        # onsubmit event
        approval_line = self.model.docs.approval_line(self.doc["id"])
        doc["approval_line"] = approval_line
        if 'onsubmit' in formapi:
            formapi["onsubmit"](framework, doc, self.status)
        
        # status change
        draft = doc["draft"]
        self.delkey(draft, "timestamp")
        try: draft['data'] = json.dumps(draft['data'], default=season.json_default)
        except Exception as e: draft['data'] = "{}"
        
        for seq in range(len(approval_line)):
            if seq == 0: continue
            draft['status'] = "ready"
            if seq > 1: draft['status'] = "pending"
            for subseq in range(len(approval_line[seq])):
                uid = approval_line[seq][subseq]
                draft['seq'] = seq * 10
                draft['subseq'] = subseq
                draft['user_id'] = uid
                self.model.process.upsert(draft)
        
        data = dict()
        if len(approval_line) == 1:
            data["status"] = "finish"
            if 'onfinish' in formapi:
                formapi["onfinish"](framework, doc, self.status)
        else:
            data["status"] = "process"

        self.model.docs.update(data, id=self.doc["id"])
        self.status(200, framework.dic.form.API.SUBMIT)

    # Approve
    def approve(self, framework):
        formapi = self.formapi
        doc = self.doc

        data = self.model.process.get(doc_id=doc['id'], status='ready', user_id=self.config.uid(framework))
        if data is None:
            self.status(401, "잘못된 접근입니다.")

        data["status"] = "finish"
        data["response"] = framework.request.query("response", "")
        del data['timestamp']
        self.model.process.upsert(data)

        readycount = len(self.model.process.rows(doc_id=doc['id'], status='ready'))
        if readycount > 0:
            if 'onapprove' in formapi:
                formapi["onapprove"](framework, doc, self.status)
            self.status(200, framework.dic.form.API.APPROVE)

        pendings = self.model.process.rows(doc_id=doc['id'], status='pending', orderby="`seq` ASC, `subseq` ASC")
        #  if pending not exists, end document
        if len(pendings) == 0:
            data = dict()
            data["status"] = "finish"
            self.model.docs.update(data, id=doc["id"])
            if 'onfinish' in formapi:
                formapi["onfinish"](framework, doc, self.status)
            self.status(200, framework.dic.form.API.APPROVE)

        preseq = None
        for pending in pendings:
            seq = int(pending['seq'])
            if preseq is None: preseq = seq
            if preseq != seq: break
            
            data = pending
            data["status"] = "ready"
            del data['timestamp']
            self.model.process.upsert(data)
            preseq = seq

        if 'onapprove' in formapi:
            formapi["onapprove"](framework, doc, self.status)

        self.status(200, framework.dic.form.API.APPROVE)

    # Reject
    def reject(self, framework):
        formapi = self.formapi
        doc = self.doc

        data = self.model.process.get(doc_id=doc['id'], status='ready', user_id=self.config.uid(framework))
        if data is None:
            self.status(401, "잘못된 접근입니다.")

        data["status"] = "reject"
        data["response"] = framework.request.query("response", "")
        del data['timestamp']
        self.model.process.upsert(data)

        data = dict()
        data["status"] = "reject"
        self.model.docs.update(data, id=doc["id"])

        data = dict()
        data["status"] = "cancel"
        self.model.process.update(data, doc_id=doc["id"], status="pending")
        self.model.process.update(data, doc_id=doc["id"], status="ready")

        if 'onreject' in formapi:
            formapi["onreject"](framework, doc, self.status)

        self.status(200, True)

    # Cancel
    def cancel(self, framework):
        formapi = self.formapi
        doc = self.doc

        if doc['user_id'] != self.config.uid(framework):
            self.status(401, True)

        data = dict()
        data["status"] = "cancel"
        self.model.docs.update(data, id=doc["id"])

        data = dict()
        data["status"] = "cancel"
        self.model.process.update(data, doc_id=doc["id"], status="pending")
        self.model.process.update(data, doc_id=doc["id"], status="ready")

        if 'oncancel' in formapi:
            formapi["oncancel"](framework, doc, self.status)
        self.status(200, True)