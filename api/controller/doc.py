import season
import time 

class Controller(season.interfaces.form.controller.api):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.framework = framework

    def __default__(self, framework):
        framework.response.abort(404)

    def data(self, framework):
        doc_id = framework.request.segment.get(0, True)
        doc = self.model.docs.data(doc_id)        
        if doc is None: self.status(404)
        
        self.status(200, doc)

    def delete(self, framework):
        doc_id = framework.request.segment.get(0, True)
        doc = self.model.docs.data(doc_id)
        if doc is None: self.status(404)
        if doc['status'] != 'draft': self.status(401)
        self.model.docs.delete(id=doc_id)
        self.model.process.delete(doc_id=doc_id)
        self.status(200, True)

    def upload(self, framework):
        if framework.request.method() != 'POST': 
            return self.status(400, 'bad request')
        doc_id = framework.request.segment.get(0, True)
        doc = self.model.docs.data(doc_id)
        if doc is None: self.status(404)
        
        files = framework.request.files()
        fs = framework.model('file', module="form")
        
        timestamp = round(time.time() * 1000)
        res = []
        for file in files:
            try:
                if len(file.filename) == 0: continue
                filename = file.filename
                fs.write_file(f"{doc_id}/{timestamp}/{filename}", file)
                res.append({'filename': filename, 'uri': f'/form/api/doc/download/{doc_id}/{timestamp}/{filename}'})
            except Exception as e:
                pass

        return self.status(200, res)

    def download(self, framework):
        doc_id = framework.request.segment.get(0, True)
        doc = self.model.docs.data(doc_id)
        if doc is None: self.status(404)

        timestamp = framework.request.segment.get(1, True)
        filename = framework.request.segment.get(2, True)

        filepath = f"{doc_id}/{timestamp}/{filename}"
        fs = framework.model('file', module="form")
        abspath = fs.abspath(filepath)
        if fs.isfile(filepath) == False:
            return self.status(404, 'Not Found')

        abspath = fs.abspath(filepath)
        framework.response.download(abspath, as_attachment=False)