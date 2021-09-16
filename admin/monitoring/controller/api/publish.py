import season

class Controller(season.interfaces.form.controller.admin_api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def search(self, framework):
        data = framework.request.query()
        data['or'] = dict()
        data['version'] = {"op": "!=", "value": "master"}
        data['status'] = "use"
        if 'text' in data:
            if len(data['text']) > 0:
                data['or']['title'] = data['text']
                data['or']['id'] = data['text']
                data['or']['category'] = data['text']
            del data['text']
        data['like'] = 'title,id,category'
        data['orderby'] = "`title` ASC, `version` DESC"
        rows = self.model.form.search(**data)

        for i in range(len(rows["list"])):
            form = rows["list"][i]
            form_id = form["id"]
            form_version = form["version"]
            rows["list"][i]["usage_count"] = self.model.docs.count(form_id=form_id, form_version=form_version)

        self.status(200, rows)

    def delete(self, framework):
        id = framework.request.query('id', True)
        version = framework.request.query('version', True)
        data = dict()
        data['status'] = 'delete'
        self.model.form.update(data, id=id, version=version)
        self.status(200, True)