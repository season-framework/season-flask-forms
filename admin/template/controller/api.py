import season
import datetime

class Controller(season.interfaces.form.controller.admin_api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def info(self, framework):
        app_id = framework.request.segment.get(0, True)
        info = self.model.template.get(id=app_id)
        if info is None: self.status(404)
        self.status(200, info)

    def search(self, framework):
        data = framework.request.query()
        data['or'] = dict()
        if 'text' in data:
            if len(data['text']) > 0:
                data['or']['displayname'] = data['text']
                data['or']['id'] = data['text']
            del data['text']
        data['like'] = 'displayname,id'
        data['orderby'] = '`displayname` ASC'
        rows = self.model.template.search(**data)
        self.status(200, rows)

    def update(self, framework):
        info = framework.request.query()
        if 'id' not in info or info['id'] == 'new':
            self.status(400, "Bad Request")
        stat, _ = self.model.template.upsert(info)
        if stat: self.status(200, info['id'])
        self.status(500, info['id'])

    def delete(self, framework):
        id = framework.request.query('id', True)
        self.model.template.delete(id=id)
        self.status(200, True)