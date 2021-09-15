import season

class Controller(season.interfaces.form.controller.admin):

    def __startup__(self, framework):
        super().__startup__(framework)
        
    def __default__(self, framework):
        response = framework.response
        return response.redirect('form')