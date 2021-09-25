import season

class Controller(season.interfaces.form.controller.api):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.framework = framework

        # check access level
        self.doc_id = doc_id = framework.request.segment.get(0, True)
        self.doc = doc = self.model.docs.data(doc_id)
        if doc is None: self.status(404)

        self.flow = framework.model("flow", module="form").init(doc_id, self.status)        
        form = self.model.form.get(id=doc["form_id"], version=doc["form_version"])
        self.templateapi = self.model.template.api(form['theme'])

    def __default__(self, framework):
        fn = framework.request.segment.get(0, None)
        if fn is not None:
            self.__templateapi(fn)
        framework.response.abort(404)

    def __error__(self, framework, e):
        self.status(500, framework.dic.form.API.ERROR)

    def delkey(self, obj, key):
        if key in obj:
            del obj[key]

    def __templateapi(self, name):
        framework = self.framework
        if name in self.templateapi:
            framework.response.status = self.status
            self.templateapi[name](framework, self.flow)

    # save draft
    def draft(self, framework):
        self.__templateapi("draft")
        data = dict()
        data["title"] = framework.request.query("title", "")
        data["approval_line"] = framework.request.query("approval_line", "[]")
        data["data"] = framework.request.query("data", "{}")
        self.flow.draft(**data)
        self.status(200, framework.dic.form.API.SAVED)

    # Submit
    def submit(self, framework):
        self.__templateapi("submit")
        data = dict()
        data["title"] = framework.request.query("title", "")
        data["approval_line"] = framework.request.query("approval_line", [])
        self.flow.draft(**data)
        
        # submit
        self.flow.open()
        self.status(200, framework.dic.form.API.SUBMIT)

    # Approve
    def approve(self, framework):
        self.__templateapi("approve")
        print("default process")
        response = framework.request.query("response", "")
        self.flow.response(response)
        self.flow.approve()
        self.flow.next()
        self.status(200, framework.dic.form.API.APPROVE)

    # Reject
    def reject(self, framework):
        self.__templateapi("reject")
        response = framework.request.query("response", "")
        self.flow.response(response)
        self.flow.reject()
        self.flow.cancel()
        self.flow.close("reject")
        self.status(200, True)

    # Cancel
    def cancel(self, framework):
        self.__templateapi("cancel")
        doc = self.doc
        if doc['user_id'] != self.config.uid(framework):
            self.status(401, True)
        self.flow.cancel()
        self.flow.close("cancel")
        self.status(200, True)