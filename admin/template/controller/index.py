import season

PUG = """mixin button()
    // on draft
    button.btn.btn-light.pr-4.pl-4.ml-2(ng-click="event.delete()")
        i.mr-2.fas.fa-times
        | Delete
    button.btn.btn-light.pr-4.pl-4.ml-2(ng-click="event.save()")
        i.mr-2.fas.fa-save
        | Save Draft
    button.btn.btn-dark.pr-4.pl-4.ml-2(ng-click="event.submit()")
        i.mr-2.fas.fa-paper-plane
        | Submit

    // on process
    button.btn.btn-light.pr-4.pl-4.ml-2(ng-click="event.reject()")
        i.mr-2.fas.fa-times
        | Reject
    button.btn.btn-dark.pr-4.pl-4.ml-2(ng-click="event.approve()")
        i.mr-2.fas.fa-check-circle
        | Approve

    // on viewer
    - if allow_cancel
        button.btn.btn-light.pr-4.pl-4.ml-2(ng-click="event.cancel()")
            i.mr-2.fas.fa-undo
            | Cancel

.container(ng-controller="form-container-controller")
    .page-header
        .row.align-items-center
            .col-auto
                // set document title
                h2.page-title {$ form_title $}
            .col-auto.ml-auto.d-print-none
                +button
    
    .container
        .info-form.row.first-child
            .col-md-2
                h4 Document ID
            .col-md-6
                .p-1 {{doc.id}}
            .col-md-2
                h4 Status
            .col-md-2
                .p-1 {{doc.status}}
        .info-form.row
            .col-md-2
                h4 User
            .col-md-10
                .p-1 {{doc.user.name}}
        .info-form.row
            .col-md-2
                h4 Date
            .col-md-10
                .p-1 {{doc.timestamp}}
        .info-form.row
            .col-md-2
                h4 Document Title
            .col-md-10
                .p-1 {{doc.title}}

    // call form view
    div(id="#form-{$form_id$}" ng-controller='form-{$form_id$}')
        {$ view | safe $}

    .container.mt-4.text-center
        +button
        
"""

JS = """app.controller('form-container-controller', function ($sce, $scope, $timeout) {
    $scope.doc = null;
    sform.init(function (doc) {
        $scope.doc = doc;
        var tmp = [];
        for (var i = 0; i < $scope.doc.approval_line_info.length; i++) {
            var obj = [];
            for (var j = 0; j < $scope.doc.approval_line_info[i].length; j++) {
                obj.push($scope.doc.approval_line_info[i][j]);
            }

            if (obj.length > 0) {
                tmp.push(obj);
            }
        }
        
        $scope.doc.approval_line_info = tmp;
        $timeout();
    });

    $scope.event = {};

    $scope.event.save = function (cb) {
        var data = sform.data();
        $scope.doc.title = sform.title();
        sform.draft($scope.doc.title, data, function (res) {
            if (res.code == 200) {
                if (cb) return cb(res);
                return toastr.success(res.data);
            }
            return toastr.error(res.data);
        });
    };

    $scope.event.submit = function () {
        $scope.event.save(function () {
            sform.submit($scope.doc.title, function (res) {
                if (res.code == 200) {
                    return location.reload();
                }
                return toastr.error(res.data)
            });
        });
    };

    $scope.event.approve = function () {
        sform.approve($scope.doc.response, function (res) {
            if (res.code == 200) {
                return location.reload();
            }
            return toastr.error(res.data);
        });
    };

    $scope.event.reject = function () {
        sform.reject($scope.doc.response, function (res) {
            if (res.code == 200) {
                return location.reload();
            }
            return toastr.error(res.data);
        });
    };

    $scope.event.cancel = function () {
        sform.cancel(function (res) {
            console.log(res);
            if (res.code == 200) {
                return location.reload();
            }
            return toastr.error(res.data);
        });
    };

    $scope.event.delete = function () {
        sform.delete(function (res) {
            if (res.code == 200) {
                location.href = "/eform/mylist";
                return;
            }
            return toastr.error(res.data);
        });
    };
});
"""

API = """#  default api functions

# save draft api
def draft(framework, flow):
    pass

# submit api: when called user click submit button
def submit(framework, flow):
    pass

# approve api: when called approver click approve button
def approve(framework, flow):
    pass

# approve api: when called approver click reject button
def reject(framework, flow):
    pass

# approve api: when called user click cancel button
def cancel(framework, flow):
    pass

# not called default
def custom_api(framework, flow):
    # save draft document
    flow.draft(title="some title", data="{}", approval_line="[]")

    # document process start
    # - change document status to `process`
    # - create approval line data
    flow.open()

    # save response (allowed to approver)
    flow.response("response text")

    # update process status (`ready` -> `finish`)
    flow.approve()

    # change to next approver's status (`pending` -> `ready`)
    flow.next()

    # update process status to (`ready` -> `reject`)
    flow.reject()

    # clear process data (`ready` | `pending` -> `cancel`)
    flow.cancel()

    # document close,
    flow.close("finish | cancel | reject")

    # response to client
    framework.response.status(200, "message")
"""

CSS = """.form-control:disabled, .form-select:disabled {
    background: white !important;
    color: #354052 !important;
    border: 0;
}
"""

class Controller(season.interfaces.form.controller.admin):

    def __startup__(self, framework):
        super().__startup__(framework)
        self.css('css/main.less')
        
    def __default__(self, framework):
        response = framework.response
        return response.redirect('list')

    def list(self, framework):
        self.js('js/list.js')
        search = framework.request.query()
        self.exportjs(search=search)
        return framework.response.render('list.pug')

    def editor(self, framework):
        self.js('js/editor.js')
        self.css('css/editor.css')
        id = framework.request.segment.get(0, True)
        info = self.model.template.get(id=id)

        if info is None:
            info = dict()
            info["displayname"] = "New Template"
            newid = framework.lib.util.randomstring(16)
            res = self.model.template.get(id=newid)
            while res is not None:
                newid = framework.lib.util.randomstring(16)
                res = self.model.template.get(id=newid)
            info["id"] = newid
            info["draft"] = PUG
            info["draft_js"] = JS
            info["draft_css"] = CSS
            info["process"] = PUG
            info["process_js"] = JS
            info["process_css"] = CSS
            info["view"] = PUG
            info["view_js"] = JS
            info["view_css"] = CSS
            info["api"] = API
            info["viewuri"] = ""
            self.model.template.insert(info)
            framework.response.redirect("editor/" + newid)
        
        self.exportjs(id=id)
        framework.response.render('editor.pug')
