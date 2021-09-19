import season

class Controller(season.interfaces.form.controller.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def search(self, framework):
        data = framework.request.query()
        data['or'] = dict()
        data['version'] = "master"
        data['publish'] = "publish"
        if 'text' in data:
            if len(data['text']) > 0:
                data['or']['title'] = data['text']
                data['or']['id'] = data['text']
                data['or']['category'] = data['text']
            del data['text']
        data['like'] = 'title,id,category'
        data['orderby'] = '`created` DESC'
        rows = self.model.form.search(**data)
        self.status(200, rows)
