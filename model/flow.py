import season
import json

# Model for document flow management
class Model:
    def __init__(self, framework):
        self.framework = framework
        self.config = framework.config.load("form")
        self.model = season.stdClass()
        self.model.form = framework.model("form", module="form")
        self.model.docs = framework.model("docs", module="form")
        self.model.process = framework.model("process", module="form")
        self.model.template = framework.model("template", module="form")

    def init(self, doc_id, resp, user_id=None):
        self = Model(self.framework)
        doc = self.doc = self.model.docs.data(doc_id, user_id=user_id)
        if doc is None: 
            raise Exception("Document Not Found")
        form = self.form = self.model.form.get(id=doc["form_id"], version=doc["form_version"])
        if form is None:
            raise Exception("Document Not Found")
        self.formapi = self.model.form.api(doc["form_id"], doc["form_version"])
        self.doc_id = doc_id
        self.resp = resp
        self.closed = False
        return self

    def __formapi(self, name):
        doc = self.model.docs.data(self.doc_id)
        framework = self.framework
        if name in self.formapi:
            self.formapi[name](framework, doc, self.resp)

    def __update_document(self, **data):
        doc_id = self.doc_id

        # delete update not allowed key
        notallowed = ["form_id", "form_version", "user_id", "id"]
        for key in notallowed:
            if key in data:
                del data[key]

        try: 
            if "approval_line" in data:
                if type(data["approval_line"]) != str:
                    data["approval_line"] = json.dumps(data["approval_line"], default=season.json_default)
        except: 
            data["approval_line"] = "[]"

        self.model.docs.update(data, id=doc_id)

    def __create_process(self, **data):
        data["doc_id"] = self.doc_id
        if "user_id" not in data: return False
        if "seq" not in data: return False
        if "subseq" not in data: return False
        if "status" not in data: return False
        if "response" not in data: data["response"] = ""
        try:
            if type(data["data"]) != str: 
                data["data"] = json.dumps(data["data"], season.json_default)
        except:
            pass
        self.model.process.insert(data)

    def __update_process(self, user_id, seq, subseq, **data):
        doc_id = self.doc_id
        if "doc_id" in data: del data["doc_id"]
        if "user_id" in data: del data["user_id"]
        if "seq" in data: del data["seq"]
        if "subseq" in data: del data["subseq"]
        if "timestamp" in data: del data["timestamp"]
        self.model.process.update(data, doc_id=doc_id, user_id=user_id, seq=seq, subseq=subseq)

    def add_process(self, uids):
        self.add_process_next(uids)

    def add_process_next(self, uids):
        if type(uids) == str:
            uids = [uids]
        if type(uids) != list:
            raise Exception("flow.add_process_next(list): not supported format")
        framework = self.framework
        user_id = self.config.uid(framework)
        doc_id = self.doc_id
        process = self.model.process.get(doc_id=doc_id, status='ready', user_id=user_id)
        if process is None:
            raise Exception("now allowed access")

        draft = self.model.process.get(doc_id=doc_id, status="draft")
        seq = int(process['seq']) + 1
        for subseq in range(len(uids)):
            uid = uids[subseq]
            self.__create_process(user_id=uid, seq=seq, subseq=subseq, status="pending", data=draft["data"], response="")

    def draft(self, **data):
        if len(data.items()) == 0:
            return self.model.process.get(doc_id=self.doc_id, status="draft")

        if "status" in data: del data["status"]
        if "doc_id" in data: del data["doc_id"]
        if "user_id" in data: del data["user_id"]
        if "seq" in data: del data["seq"]
        if "subseq" in data: del data["subseq"]
        if "timestamp" in data: del data["timestamp"]

        self.__update_document(**data)

        draft = self.model.process.get(doc_id=self.doc_id, status="draft")
        if draft is None:
            draft = dict()
            draft['doc_id'] = self.doc_id
            draft['user_id'] = self.doc['user_id']
            draft['seq'] = 0
            draft['subseq'] = 0
            draft['status'] = 'draft'
            draft['data'] = '{}'
            draft['response'] = ''
            self.model.process.insert(draft)
        self.model.process.update(data, doc_id=self.doc_id, user_id=self.doc['user_id'], seq=0, subseq=0)

    def close(self, status="finish"):
        doc_id = self.doc_id
        notresponsed = self.model.process.count(doc_id=doc_id, status=['pending', 'ready'])
        if notresponsed > 0:
            return False

        if status not in ["finish", "reject", "cancel"]:
            status = "finish"

        if status == 'finish':
            self.__formapi('onfinish')

        self.__update_document(status=status)
        self.closed = True
        return True

    def open(self):
        if self.closed: return False

        self.__formapi('onsubmit')
        self.__update_document(status="process")

        # initialize approval line
        doc_id = self.doc_id
        draft = self.model.process.get(doc_id=self.doc_id, status="draft")
        approval_line = self.model.docs.approval_line(doc_id)

        for seq in range(len(approval_line)):
            if seq == 0: continue # if draft, pass
            status = "ready"
            if seq > 1: status = "pending"
            for subseq in range(len(approval_line[seq])):
                uid = approval_line[seq][subseq]
                self.__create_process(user_id=uid, seq=seq * 10, subseq=subseq, status=status, data=draft["data"], response="")
        self.close()
        return True

    def next(self):
        if self.closed: return False
        if self.close(): return False 

        doc_id = self.doc_id
        readycount = self.model.process.count(doc_id=doc_id, status='ready')
        if readycount > 0:
            return False
        
        pendings = self.model.process.rows(doc_id=doc_id, status='pending', orderby="`seq` ASC, `subseq` ASC")
        if len(pendings) == 0:
            return False
        
        # next level ready
        preseq = None
        for pending in pendings:
            seq = int(pending['seq'])
            if preseq is None: preseq = seq
            if preseq != seq: break
            user_id = pending['user_id']
            seq = pending['seq']
            subseq = pending['subseq']
            self.__update_process(user_id, seq, subseq, status="ready")
            preseq = seq

        return True

    def response(self, response=None):
        if self.closed: return False
        if self.close(): return False 

        framework = self.framework
        user_id = self.config.uid(framework)
        doc_id = self.doc_id
        process = self.model.process.get(doc_id=doc_id, status='ready', user_id=user_id)
        if process is None:
            return False
        seq = process['seq']
        subseq = process['subseq']
        if response is not None:
            self.__update_process(user_id, seq, subseq, response=response)
        return True

    def approve(self):
        if self.closed: return False
        if self.close(): return False 

        framework = self.framework
        user_id = self.config.uid(framework)
        doc_id = self.doc_id

        process = self.model.process.get(doc_id=doc_id, status='ready', user_id=user_id)

        if process is None:
            return False
        self.__formapi('onapprove')
        seq = process['seq']
        subseq = process['subseq']
        self.__update_process(user_id, seq, subseq, status="finish")
        self.close()
        return True

    def reject(self):
        if self.closed: return False
        if self.close(): return False 

        framework = self.framework
        user_id = self.config.uid(framework)
        doc_id = self.doc_id
        process = self.model.process.get(doc_id=doc_id, status='ready', user_id=user_id)
        if process is None:
            return False
        self.__formapi('onreject')
        seq = process['seq']
        subseq = process['subseq']
        self.__update_process(user_id, seq, subseq, status="reject")
        self.close()
        return True
    
    def cancel(self):
        if self.closed: return False
        if self.close(): return False 

        doc_id = self.doc_id
        data = dict()
        data["status"] = "cancel"
        self.model.process.update(data, doc_id=doc_id, status="pending")
        self.model.process.update(data, doc_id=doc_id, status="ready")
