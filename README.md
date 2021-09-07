# SEASON eForm Platform

- SEASON WIZ depends on `season-flask`

## Installation

```bash
sf module import form --uri https://github.com/season-framework/season-flask-form
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
  `content` text,
  `html` longtext,
  `html_view` longtext,
  `js` longtext,
  `css` longtext,
  `api` longtext,
  `created` datetime NOT NULL,
  `updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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
  `status` varchar(12) NOT NULL,
  `data` longtext NOT NULL,
  `response` longtext,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`doc_id`,`user_id`),
  KEY `doc_id` (`doc_id`),
  KEY `user_id` (`user_id`),
  KEY `status` (`status`),
  KEY `timestamp` (`timestamp`)
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
config = stdClass()

config.database = 'portal'
config.table_form = 'form'
config.table_docs = 'form_docs'
config.table_process = 'form_process'

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