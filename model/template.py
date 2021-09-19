import season
import lesscpy
from six import StringIO
import pypugjs

class Model(season.core.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)
        config = framework.config.load("form")
        self.namespace = config.get("database", "form")
        self.tablename = config.get("table_template", "form_templates")

    def compile_pug(self, html):
        framework = self.framework
        config = framework.config.load("form")
        try:
            pugconfig = {}
            if config.pug is not None: pugconfig = config.pug
            pug = pypugjs.Parser(html)
            pug = pug.parse()
            html = pypugjs.ext.jinja.Compiler(pug, **pugconfig).compile()
        except Exception as e:
            pass
        return html

    def render(self, id, status, **kwargs):
        form_id = kwargs['form_id']
        doc_id = kwargs['doc_id']
        form_version = kwargs['form_version']
        js = kwargs['js']
        css = kwargs['css']

        del kwargs['css']
        del kwargs['js']

        o = "{"
        e = "}"
        template = self.get(id=id)
        if template is None:
            template = self.get(id="default")            
        if template is None:
            template = self.rows(limit=1)
            if len(template) == 0:
                return ""
            template = template[0]

        template_pug = template[status]
        template_js = template[status + "_js"]
        template_css = template[status + "_css"]
        template_pug = self.compile_pug(template_pug)
        template_pug = self.framework.response.template_from_string(template_pug, **kwargs)
        template_css = lesscpy.compile(StringIO(template_css), minify=True)
        template_css = str(template_css)

        view = f"""<script src='/resources/form/season-form.js'></script>
        <script>var sform = season_form('{form_id}', '{doc_id}', '{form_version}');</script>

        {template_pug}
        
        <script>
            {template_js}
        </script>

        <script>
            function __init_{form_id}() {o}
                {js};
                try {o} 
                    app.controller('form-{form_id}', form_controller); 
                {e}  catch (e) {o} 
                    app.controller('form-{form_id}', function() {o} {e} ); 
                {e} 
            {e}; 
            __init_{form_id}();
        </script>
        
        <style>{template_css}</style>
        <style>{css}</style>
        """
        
        return view

    def api(self, id):
        template = self.get(id=id)
        if template is None:
            template = self.get(id="default")            
        if template is None:
            template = self.rows(limit=1)
            if len(template) == 0:
                return ""
            template = template[0]

        if template is None:
            return season.stdClass()
            
        process_api = template['api']
        fn = {'__file__': 'season.form.Spawner', '__name__': 'season.form.Spawner', 'framework': self.framework}
        exec(compile(process_api, 'season.form.Spawner', 'exec'), fn)
        return fn
