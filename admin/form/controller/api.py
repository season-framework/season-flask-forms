import season
import datetime

class Controller(season.interfaces.form.controller.admin_api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def info(self, framework):
        app_id = framework.request.segment.get(0, True)
        version = framework.request.segment.get(1, "master")
        info = self.model.form.get(id=app_id, version=version)
        info["history"] = self.model.form.rows(id=app_id, status='use', orderby="`version` DESC")
        if info is None:
            self.status(404)
        self.status(200, info)

    def search(self, framework):
        data = framework.request.query()
        data['or'] = dict()
        data['version'] = "master"
        data['status'] = "use"
        if 'text' in data:
            if len(data['text']) > 0:
                data['or']['title'] = data['text']
                data['or']['id'] = data['text']
                data['or']['category'] = data['text']
            del data['text']
        data['like'] = 'title,id,category'
        data['orderby'] = '`category` ASC, `title` ASC'
        rows = self.model.form.search(**data)
        self.status(200, rows)

    def update(self, framework):
        info = framework.request.query()
        if 'id' not in info or info['id'] == 'new':
            self.status(400, "Bad Request")
        info["version"] = "master"
        stat, _ = self.model.form.upsert(info)
        if stat: self.status(200, info['id'])
        self.status(500, info['id'])

    def publish(self, framework):
        _info = framework.request.query()
        if 'id' not in _info or _info['id'] == 'new':
            self.status(400, "Bad Request")
        info = self.model.form.get(id=_info['id'], version="master")
        info['version'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        info['publish'] = "publish"
        try:
            info['memo'] = _info['memo']
        except:
            pass
        stat, _ = self.model.form.upsert(info)

        info['version'] = "master"
        _ = self.model.form.upsert(info)

        if stat: self.status(200, info['id'])
        self.status(500, info['id'])

    def delete(self, framework):
        id = framework.request.query('id', True)
        data = dict()
        data['status'] = 'delete'
        self.model.form.update(data, id=id)
        self.status(200, True)

    def flush(self, framework):
        id = framework.request.query('id', True)
        info = self.model.form.get(id=id)
        ns = info['namespace']
        self.model.docs.delete(id=f"dev-{ns}")
        self.model.process.delete(doc_id=f"dev-{ns}")
        self.status(200, True)