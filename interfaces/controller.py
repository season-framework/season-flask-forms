import season
import datetime
import json
import os

class view:
    def __startup__(self, framework):
        self.__framework__ = framework
        self._css = []
        self._js = []
        self._exportjs = {}

        self.__framework__.response.data.set(css=self._css)
        self.__framework__.response.data.set(js=self._js)
        self.__framework__.response.data.set(exportjs=self._exportjs)
        self.__framework__.response.data.set(session=dict(framework.session))

        self.config = framework.config.load('form').data
        self.model = season.stdClass()
        self.model.form = framework.model("form", module="form")
        self.model.docs = framework.model("docs", module="form")
        self.model.process = framework.model("process", module="form")
        self.model.template = framework.model("template", module="form")

        self.config.acl(framework)
        if 'topmenus' in self.config: self.topnav(self.config.topmenus)
        
    def nav(self, menus):
        framework = self.__framework__

        for menu in menus:
            pt = None
            if 'pattern' in menu: pt = menu['pattern']
            elif 'url' in menu: pt = menu['url']

            if pt is not None:
                if framework.request.match(pt): menu['class'] = 'active'
                else: menu['class'] = ''

            if 'child' in menu:
                menu['show'] = 'show'
                for i in range(len(menu['child'])):
                    child = menu['child'][i]
                    cpt = None
                
                    if 'pattern' in child: cpt = child['pattern']
                    elif 'url' in child: cpt = child['url']

                    if cpt is not None:
                        if framework.request.match(cpt): 
                            menu['child'][i]['class'] = 'active'
                            menu['show'] = 'show'
                        else: 
                            menu['child'][i]['class'] = ''

        framework.response.data.set(menus=menus)
    
    def topnav(self, menus):
        framework = self.__framework__

        for menu in menus:
            pt = None
            if 'pattern' in menu: pt = menu['pattern']
            elif 'url' in menu: pt = menu['url']

            if pt is not None:
                if framework.request.match(pt): menu['class'] = 'bg-dark text-white'
                else: menu['class'] = ''

        framework.response.data.set(topmenus=menus)
    

    def subnav(self, menus):
        framework = self.__framework__

        for menu in menus:
            pt = None
            if 'pattern' in menu: 
                pt = menu['pattern']
                if pt is not None:
                    if framework.request.match(pt): menu['class'] = 'bg-dark text-white'
                    else: menu['class'] = ''
            elif 'url' in menu: 
                pt = menu['url']
                if framework.request.uri() == pt: menu['class'] = 'bg-dark text-white'
                else: menu['class'] = ''

        framework.response.data.set(submenus=menus)
    
    def status(self, status_code=200, data=dict()):
        if type(data) == season.dicClass: data = str(data)
        res = season.stdClass()
        res.code = status_code
        res.data = data
        res = json.dumps(res, default=self.json_default)
        return self.__framework__.response.send(res, content_type='application/json')

    def exportjs(self, **args):
        for key in args:
            v = args[key]
            self._exportjs[key] = json.dumps(v, default=self.json_default)
        
        self.__framework__.response.data.set(exportjs=self._exportjs)

    def css(self, url):
        framework = self.__framework__
        url = os.path.join(framework.modulename, url)
        self._css.append(url)
        self.__framework__.response.data.set(css=self._css)
    
    def js(self, url):
        framework = self.__framework__
        url = os.path.join(framework.modulename, url)
        self._js.append(url)
        self.__framework__.response.data.set(js=self._js)

    def parse_json(self, jsonstr, default=None):
        try:
            return json.loads(jsonstr)
        except:
            pass
        return default

    def json_default(self, value):
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value).replace('<', '&lt;').replace('>', '&gt;')

class api(view):
    def __startup__(self, framework):
        super().__startup__(framework)

    def __error__(self, framework, e):
        framework.response.json({"status": 500, "error": str(e)})

class admin(view):
    def __startup__(self, framework):
        super().__startup__(framework)
        if self.config.admin_acl(framework) == False:
            framework.response.abort(401)

        menus = []
        menus.append({ 'title': "Forms", 'url': f'/form/admin/form' , 'pattern': r'^/form/admin/form' })
        menus.append({ 'title': "Templates", 'url': f'/form/admin/template' , 'pattern': r'^/form/admin/template' })
        menus.append({ 'title': "Monitoring", 'url': f'/form/admin/monitoring' , 'pattern': r'^/form/admin/monitoring' })
        self.nav(menus)

class admin_api(admin):
    def __startup__(self, framework):
        super().__startup__(framework)

    def __error__(self, framework, e):
        framework.response.json({"status": 500, "error": str(e)})