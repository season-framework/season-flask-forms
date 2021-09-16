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
  `process` longtext NOT NULL,
  `view` longtext NOT NULL,
  `js` longtext NOT NULL,
  `css` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;
```

- `default template` data

```sql
INSERT INTO `form_templates` (`id`, `displayname`, `draft`, `process`, `view`, `js`, `css`)
VALUES
	('default', 'default', 'mixin button()\n    button.btn.btn-light.pr-4.pl-4.ml-2(ng-click=\"event.delete()\")\n        i.mr-2.fas.fa-times\n        | 삭제\n    button.btn.btn-light.pr-4.pl-4.ml-2(ng-click=\"event.save()\")\n        i.mr-2.fas.fa-save\n        | 임시저장\n    button.btn.btn-dark.pr-4.pl-4.ml-2(ng-click=\"event.submit()\")\n        i.mr-2.fas.fa-paper-plane\n        | 제출\n\n\n.container(ng-controller=\"form-container-controller\")\n    .page-header\n        .row.align-items-center\n            .col-auto\n                .page-pretitle 전자결재\n                h2.page-title {$ form_title $}\n            .col-auto.ml-auto.d-print-none\n                +button\n    \n    .container\n        .info-form.row.first-child\n            .col-md-2\n                h4 문서번호\n            .col-md-6\n                .p-1 {{doc.id}}\n            .col-md-2\n                h4 결재상태\n            .col-md-2\n                .p-1 {{statusmap[doc.status]}}\n        .info-form.row\n            .col-md-2\n                h4 신청자\n            .col-md-10\n                .p-1 {{doc.user.name}}\n        .info-form.row\n            .col-md-2\n                h4 신청일자\n            .col-md-10\n                .p-1 {{doc.timestamp}}\n        .info-form.row\n            .col-md-2\n                h4 문서제목\n            .col-md-10\n                .p-1 {{doc.title}}\n\n    div(id=\"#form-{$form_id$}\" ng-controller=\'form-{$form_id$}\')\n        {$ view | safe $}\n\n    .container.mt-4.text-center\n        +button\n        ', 'mixin button()\n    button.btn.btn-light.pr-4.pl-4.ml-2(ng-click=\"event.reject()\")\n        i.mr-2.fas.fa-times\n        | 반려\n    button.btn.btn-dark.pr-4.pl-4.ml-2(ng-click=\"event.approve()\")\n        i.mr-2.fas.fa-check-circle\n        | 승인\n\nmixin card()\n    .card.mb-4(class=\"{{approval.status == \'ready\' && approval.user.id != doc.user_id ? \'bg-dark text-white\' : \'\'}}\")\n        .ribbon.ribbon-top.ribbon-bookmark.bg-dark-lt(ng-if=\"approval.status == \'ready\' && approval.user.id != doc.user_id\")\n        .card-header\n            .card-title(style=\"text-overflow: ellipsis; white-space: nowrap; overflow: hidden;\") {{approval.user.name}}\n        .card-body.text-left(style=\"height: 120px; overflow: auto;\")\n            .text-left(ng-if=\"approval.user.id != doc.user_id && [\'reject\', \'finish\'].includes(approval.status)\") {{approval.response}}\n            .text-left(ng-if=\"approval.user.id != doc.user_id && approval.status == \'ready\'\") 결재 대기중 입니다\n            .text-left(ng-if=\"approval.user.id != doc.user_id && approval.status == \'cancel\'\") 결재가 취소되었습니다\n            .text-left(ng-if=\"approval.user.id == doc.user_id\") 제출\n        .card-footer(ng-if=\"approval.user.id == doc.user_id\")\n            button.btn.btn-secondary.btn-sm.btn-block 제출\n        .card-footer(ng-if=\"approval.user.id != doc.user_id\")\n            button.btn.btn-secondary.btn-sm.btn-block(ng-if=\"approval.status == \'ready\'\") 결재대기\n            button.btn.btn-green.btn-sm.btn-block(ng-if=\"approval.status == \'finish\'\") 승인\n            button.btn.btn-red.btn-sm.btn-block(ng-if=\"approval.status == \'reject\'\") 반려\n            button.btn.btn-secondary.btn-sm.btn-block(ng-if=\"approval.status == \'cancel\'\") 취소\n            button.btn.btn-secondary.btn-sm.btn-block(ng-if=\"approval.status == \'pending\'\") 대기\n\nmixin approval()\n    .container\n        .info-form.row.first-child\n            .col-md-2\n                h4 결재현황\n            .col-md-10.pt-4\n                .row.row-deck.row-cards(ng-if=\"doc.approval_line_info.length == 0\")\n                    .col-md-3\n                        .card.mb-4\n                            .card-header\n                                .card-title 결재없음\n                            .card-body.text-left(style=\"height: 120px; overflow: auto;\")\n                                .text-left 결재가 필요 없는 문서입니다\n                            .card-footer\n                                button.btn.btn-green.btn-block 결재없음\n                \n                .approvals(ng-if=\"doc.approval_line_info.length > 0\")\n                    div(ng-repeat=\"line in doc.approval_line_info track by $index\" style=\"display: inline-block;\")\n                        .pr-3(ng-if=\"$index > 0\" style=\"display: inline-block; height: 100%;\")\n                            i.fas.fa-arrow-circle-right.text-dark(style=\"font-size: 24px;\")\n                        .pr-3(ng-repeat=\"approval in line\" style=\"width: 180px; display: inline-block;\")\n                            +card\n\n.container(ng-controller=\"form-container-controller\")\n    .page-header\n        .row.align-items-center\n            .col-auto\n                .page-pretitle 전자결재\n                h2.page-title {$ form_title $}\n            .col-auto.ml-auto.d-print-none\n                +button\n    \n    .container\n        .info-form.row.first-child\n            .col-md-2\n                h4 문서번호\n            .col-md-6\n                .p-1 {{doc.id}}\n            .col-md-2\n                h4 결재상태\n            .col-md-2\n                .p-1 {{statusmap[doc.status]}}\n        .info-form.row\n            .col-md-2\n                h4 신청자\n            .col-md-10\n                .p-1 {{doc.user.name}}\n        .info-form.row\n            .col-md-2\n                h4 신청일자\n            .col-md-10\n                .p-1 {{doc.timestamp}}\n        .info-form.row\n            .col-md-2\n                h4 문서제목\n            .col-md-10\n                .p-1 {{doc.title}}\n\n    div(id=\"#form-{$form_id$}\" ng-controller=\'form-{$form_id$}\')\n        {$ view | safe $}\n\n    +approval\n\n    .container\n        .info-form.row.first-child.bg-dark-lt\n            .col-md-2\n                h4 응답메시지\n            .col-md-10\n                textarea.form-control(rows=\"5\" ng-model=\"doc.response\")\n\n    .container.mt-4.text-center\n        +button\n        ', 'mixin button()\n    - if allow_cancel\n        button.btn.btn-light.pr-4.pl-4.ml-2(ng-click=\"event.cancel()\")\n            i.mr-2.fas.fa-undo\n            | 회수\n\nmixin card()\n    .card.mb-4(class=\"{{approval.status == \'ready\' && approval.user.id != doc.user_id ? \'bg-dark text-white\' : \'\'}}\")\n        .ribbon.ribbon-top.ribbon-bookmark.bg-dark-lt(ng-if=\"approval.status == \'ready\' && approval.user.id != doc.user_id\")\n        .card-header\n            .card-title(style=\"text-overflow: ellipsis; white-space: nowrap; overflow: hidden;\") {{approval.user.name}}\n        .card-body.text-left(style=\"height: 120px; overflow: auto;\")\n            .text-left(ng-if=\"approval.user.id != doc.user_id && [\'reject\', \'finish\'].includes(approval.status)\") {{approval.response}}\n            .text-left(ng-if=\"approval.user.id != doc.user_id && approval.status == \'ready\'\") 결재 대기중 입니다\n            .text-left(ng-if=\"approval.user.id != doc.user_id && approval.status == \'cancel\'\") 결재가 취소되었습니다\n            .text-left(ng-if=\"approval.user.id == doc.user_id\") 제출\n        .card-footer(ng-if=\"approval.user.id == doc.user_id\")\n            button.btn.btn-secondary.btn-sm.btn-block 제출\n        .card-footer(ng-if=\"approval.user.id != doc.user_id\")\n            button.btn.btn-secondary.btn-sm.btn-block(ng-if=\"approval.status == \'pending\'\") 대기\n            button.btn.btn-secondary.btn-sm.btn-block(ng-if=\"approval.status == \'ready\'\") 결재대기\n            button.btn.btn-green.btn-sm.btn-block(ng-if=\"approval.status == \'finish\'\") 승인\n            button.btn.btn-red.btn-sm.btn-block(ng-if=\"approval.status == \'reject\'\") 반려\n            button.btn.btn-secondary.btn-sm.btn-block(ng-if=\"approval.status == \'cancel\'\") 취소\n\nmixin approval()\n    .container\n        .info-form.row.first-child\n            .col-md-2\n                h4 결재현황\n            .col-md-10.pt-4\n                .row.row-deck.row-cards(ng-if=\"doc.approval_line_info.length == 0\")\n                    .col-md-3\n                        .card.mb-4\n                            .card-header\n                                .card-title 결재없음\n                            .card-body.text-left(style=\"height: 120px; overflow: auto;\")\n                                .text-left 결재가 필요 없는 문서입니다\n                            .card-footer\n                                button.btn.btn-green.btn-block 결재없음\n                \n                .approvals(ng-if=\"doc.approval_line_info.length > 0\")\n                    div(ng-repeat=\"line in doc.approval_line_info track by $index\" style=\"display: inline-block;\")\n                        .pr-3(ng-if=\"$index > 0\" style=\"display: inline-block; height: 100%;\")\n                            i.fas.fa-arrow-circle-right.text-dark(style=\"font-size: 24px;\")\n                        .pr-3(ng-repeat=\"approval in line\" style=\"width: 180px; display: inline-block;\")\n                            +card\n\n.container(ng-controller=\"form-container-controller\")\n    .page-header\n        .row.align-items-center\n            .col-auto\n                .page-pretitle 전자결재\n                h2.page-title {$ form_title $}\n            .col-auto.ml-auto.d-print-none\n                +button\n    \n    .container\n        .info-form.row.first-child\n            .col-md-2\n                h4 문서번호\n            .col-md-6\n                .p-1 {{doc.id}}\n            .col-md-2\n                h4 결재상태\n            .col-md-2\n                .p-1 {{statusmap[doc.status]}}\n        .info-form.row\n            .col-md-2\n                h4 신청자\n            .col-md-10\n                .p-1 {{doc.user.name}}\n        .info-form.row\n            .col-md-2\n                h4 신청일자\n            .col-md-10\n                .p-1 {{doc.timestamp}}\n        .info-form.row\n            .col-md-2\n                h4 문서제목\n            .col-md-10\n                .p-1 {{doc.title}}\n\n    div(id=\"#form-{$form_id$}\" ng-controller=\'form-{$form_id$}\')\n        {$ view | safe $}\n\n    +approval\n\n    .container.mt-4.text-center\n        +button\n        ', 'app.controller(\'form-container-controller\', function ($sce, $scope, $timeout) {\n    $scope.statusmap = { \'draft\': \'작성중\', \'process\': \'진행중\', \'finish\': \'완료\', \'reject\': \'반려\', \'cancel\': \'취소\', \'pending\': \'대기\', \'ready\': \'결재대기\' };\n    $scope.doc = null;\n    sform.init(function (doc) {\n        $scope.doc = doc;\n        var tmp = [];\n        for (var i = 0; i < $scope.doc.approval_line_info.length; i++) {\n            var obj = [];\n            for (var j = 0; j < $scope.doc.approval_line_info[i].length; j++) {\n                obj.push($scope.doc.approval_line_info[i][j]);\n            }\n\n            if (obj.length > 0) {\n                tmp.push(obj);\n            }\n        }\n        \n        $scope.doc.approval_line_info = tmp;\n        $timeout();\n    });\n\n    $scope.event = {};\n\n    $scope.event.save = function (cb) {\n        var data = sform.data();\n        $scope.doc.title = sform.title();\n        sform.draft($scope.doc.title, data, function (res) {\n            if (res.code == 200) {\n                if (cb) return cb(res);\n                return toastr.success(res.data);\n            }\n            return toastr.error(res.data);\n        });\n    };\n\n    $scope.event.submit = function () {\n        $scope.event.save(function () {\n            sform.submit($scope.doc.title, function (res) {\n                if (res.code == 200) {\n                    return location.reload();\n                }\n                return toastr.error(res.data)\n            });\n        });\n    };\n\n    $scope.event.approve = function () {\n        sform.approve($scope.doc.response, function (res) {\n            if (res.code == 200) {\n                return location.reload();\n            }\n            return toastr.error(res.data);\n        });\n    };\n\n    $scope.event.reject = function () {\n        sform.reject($scope.doc.response, function (res) {\n            if (res.code == 200) {\n                return location.reload();\n            }\n            return toastr.error(res.data);\n        });\n    };\n\n    $scope.event.cancel = function () {\n        sform.cancel(function (res) {\n            console.log(res);\n            if (res.code == 200) {\n                return location.reload();\n            }\n            return toastr.error(res.data);\n        });\n    };\n\n    $scope.event.delete = function () {\n        sform.delete(function (res) {\n            if (res.code == 200) {\n                location.href = \"/eform/mylist\";\n                return;\n            }\n            return toastr.error(res.data);\n        });\n    };\n});', '');

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
