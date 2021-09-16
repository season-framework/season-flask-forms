import season

class Controller(season.interfaces.form.controller.admin):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('css/main.less')
        menus = []
        menus.append({ 'title': "Forms", 'url': f'/form/admin/monitoring/publish' , 'pattern': r'^/form/admin/monitoring/publish' })
        menus.append({ 'title': "Documents", 'url': f'/form/admin/monitoring/document' , 'pattern': r'^/form/admin/monitoring/document' })
        self.subnav(menus)
        
    def __default__(self, framework):
        response = framework.response
        return response.redirect('publish')

    def publish(self, framework):
        search = framework.request.query()
        self.exportjs(search=search)
        self.js('js/publish.js')
        return framework.response.render('publish.pug')

    def document(self, framework):
        search = framework.request.query()
        self.exportjs(search=search)
        self.js('js/document.js')
        return framework.response.render('document.pug')
