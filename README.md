# SEASON eForm Platform

- SEASON WIZ depends on `season-flask`

## Installation

```bash
sf module import form --uri https://github.com/season-framework/season-flask-forms
```

## Configuration

### MySQL Table Scheme

- `form` table

```sql
CREATE TABLE `form` (
  `id` varchar(32) NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `version` varchar(20) NOT NULL,
  `publish` varchar(20) DEFAULT NULL,
  `namespace` varchar(32) DEFAULT NULL,
  `title` varchar(128) NOT NULL DEFAULT '',
  `category` varchar(20) DEFAULT NULL,
  `content` text DEFAULT NULL,
  `html` longtext DEFAULT NULL,
  `html_view` longtext DEFAULT NULL,
  `js` longtext DEFAULT NULL,
  `css` longtext DEFAULT NULL,
  `api` longtext DEFAULT NULL,
  `created` datetime NOT NULL,
  `updated` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `theme` varchar(32) NOT NULL DEFAULT '',
  `viewuri` text DEFAULT NULL,
  PRIMARY KEY (`id`,`version`),
  KEY `title` (`title`),
  KEY `category` (`category`),
  KEY `version` (`version`),
  KEY `namespace` (`namespace`,`version`),
  KEY `publish` (`publish`),
  KEY `status` (`status`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;
```

- `document` table

```sql
CREATE TABLE `form_docs` (
  `id` varchar(48) NOT NULL DEFAULT '',
  `form_id` varchar(32) NOT NULL DEFAULT '',
  `form_version` varchar(20) NOT NULL DEFAULT '',
  `user_id` varchar(20) NOT NULL DEFAULT '',
  `title` varchar(128) DEFAULT NULL,
  `approval_line` text NOT NULL COMMENT '[]',
  `status` varchar(20) NOT NULL DEFAULT '' COMMENT 'draft,process,finish,reject',
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `form_id` (`form_id`),
  KEY `user_id` (`user_id`),
  KEY `timestamp` (`timestamp`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;
```

- `process` table

```sql
CREATE TABLE `form_process` (
  `doc_id` varchar(48) NOT NULL DEFAULT '',
  `user_id` varchar(20) NOT NULL,
  `seq` int(11) NOT NULL DEFAULT 0,
  `subseq` int(11) NOT NULL,
  `status` varchar(12) NOT NULL,
  `data` longtext NOT NULL,
  `response` longtext DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`doc_id`,`user_id`,`seq`,`subseq`),
  KEY `doc_id` (`doc_id`),
  KEY `user_id` (`user_id`),
  KEY `status` (`status`),
  KEY `timestamp` (`timestamp`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;
```

- `templates` table

```sql
CREATE TABLE `form_templates` (
  `id` varchar(16) NOT NULL DEFAULT '',
  `displayname` varchar(64) NOT NULL,
  `draft` longtext NOT NULL,
  `draft_js` longtext NOT NULL,
  `draft_css` longtext NOT NULL,
  `process` longtext NOT NULL,
  `process_js` longtext NOT NULL,
  `process_css` longtext NOT NULL,
  `view` longtext NOT NULL,
  `view_js` longtext NOT NULL,
  `view_css` longtext NOT NULL,
  `api` longtext NOT NULL,
  `viewuri` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;
```

### websrc/app/config/config.py

- add variable start/end string config: `{$` / `$}`

```python
import season
config = season.stdClass()

# ...

config.jinja_variable_start_string = "{$"
config.jinja_variable_end_string = "$}"
```

### websrc/app/config/form.py

```python
from season import stdClass
import datetime
config = stdClass()

config.database = 'portal'
config.table_form = 'form'
config.table_docs = 'form_docs'
config.table_process = 'form_process'
config.table_template = 'form_templates'

config.category = ["인사", "총무", "재무", "업무"]
config.topmenus = [{ 'title': 'HOME', 'url': '/' }, { 'title': 'WIZ', 'url': '/wiz' }]

# General Access Level
def acl(framework):
    return True
config.acl = acl

# Admin (edit forms) Access Level
def admin_acl(framework):
    if 'role' not in framework.session:
        return False
    if framework.session['role'] not in ['admin']:
        return False
    return True
config.admin_acl = admin_acl

# Access Level for each document
def document_acl(framework, doc):
    if admin_acl(framework):
        return True
    return False
config.document_acl = document_acl

# define user info
def userinfo(framework, user_id):
    return framework.model("mysql/users").get(id=user_id)
config.userinfo = userinfo

# define user id
def uid(framework):
    return framework.session['id']
config.uid = uid

# pug build option
config.pug = stdClass()
config.pug.variable_start_string = "{$"
config.pug.variable_end_string = "$}"

# default theme file
config.theme = stdClass()
config.theme.module = "theme"
config.theme.view = "layout-form.pug"

# document id generator
def id_builder(framework, form):
    return datetime.datetime.now().strftime("%Y") + "-" + form['category'] + "-" + framework.lib.util.randomstring(12)
config.id_builder = id_builder
```

### Theme File

- create theme eg. `theme/view/layout-form.pug`
    - must include `{$ view $}` for render point

```pug
doctype 5
include theme/component

html(ng-app="app")
    head
        +header
        
    body.antialiased
        script(src='/resources/theme/libs/tabler/dist/libs/bootstrap/dist/js/bootstrap.bundle.min.js')
        script(src='/resources/theme/libs/tabler/dist/libs/peity/jquery.peity.min.js')
        script(src='/resources/theme/libs/tabler/dist/js/tabler.min.js')

        .page(ng-controller="content" ng-cloak)
            .preview
                {$ view $}

            style.
                html,
                body {
                    overflow: auto;
                    background: white;
                }

                body {
                    padding: 32px;
                }

                .page {
                    background: transparent;
                }

        +builder
```


## Usage

### websrc/app/filter/indexfilter.py

- add code to indexfilter

```python
framework.eform = framework.model("form", module="form")
framework.response.data.set(eform=framework.eform)
```

### in Templates

- load view using `document_id`
    - eform.render("document_id")

```pug
.container.mt-4
    {$ eform.render(doc_id) $}
```
