import season

class Controller(season.interfaces.form.controller.admin_api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def search(self, framework):
        data = framework.request.query()
        data['or'] = dict()
        data['version'] = "master"
        if 'text' in data:
            if len(data['text']) > 0:
                data['or']['title'] = data['text']
                data['or']['id'] = data['text']
                data['or']['category'] = data['text']
            del data['text']
        data['like'] = 'title,id,category'
        data['fields'] = 'id'
        data['orderby'] = "`title` ASC, `version` DESC"
        rows = self.model.form.search(**data)

        form_id = []
        for row in rows["list"]:
            form_id.append(row['id'])

        data = framework.request.query()
        data['or'] = dict()
        if 'text' in data:
            if len(data['text']) > 0:
                data['or']['id'] = data['text']
                data['or']['user_id'] = data['text']
                data['or']['status'] = data['text']
            del data['text']
        if len(form_id) > 0: data['or']['form_id'] = form_id
        data['like'] = 'id,user_id,status'
        data['orderby'] = "`timestamp` DESC"

        rows = self.model.docs.search(**data)
        rows["total"] = self.model.docs.count(**data)

        for i in range(len(rows["list"])):
            doc = rows["list"][i]
            rows["list"][i]["form"] = self.model.form.get(id=doc["form_id"], version=doc["form_version"])

            try:
                rows["list"][i]['user'] = self.config.userinfo(framework, rows["list"][i]['user_id'])
            except Exception as e:
                pass

        self.status(200, rows)

    def delete(self, framework):
        id = framework.request.query('id', True)
        version = framework.request.query('version', True)
        data = dict()
        data['status'] = 'delete'
        self.model.form.update(data, id=id, version=version)
        self.status(200, True)