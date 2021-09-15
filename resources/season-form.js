var season_form = function (form_id, doc_id, version) {
    if (version) version = "master";
    else version = "latest";

    var obj = {};
    var baseurl = "/form/api";
    var API = {};
    API.DOC = {};
    API.DOC.DATA = baseurl + "/doc/data/" + doc_id;
    API.DOC.UPLOAD = baseurl + "/doc/upload/" + doc_id;
    API.DOC.DELETE = baseurl + "/doc/delete/" + doc_id;
    API.PROCESS = {};
    API.PROCESS.DRAFT = baseurl + "/process/draft/" + doc_id;
    API.PROCESS.SUBMIT = baseurl + "/process/submit/" + doc_id;
    API.PROCESS.APPROVE = baseurl + "/process/approve/" + doc_id;
    API.PROCESS.REJECT = baseurl + "/process/reject/" + doc_id;
    API.PROCESS.CANCEL = baseurl + "/process/cancel/" + doc_id;

    var fn = function (url, data, cb, opts) {
        var ajax = {
            url: url,
            type: 'POST',
            data: data
        };

        if (opts) {
            for (var key in opts) {
                ajax[key] = opts[key];
            }
        }

        $.ajax(ajax).always(function (a, b, c) {
            if (cb) cb(a, b, c);
        });
    }

    obj.cache = {};

    fn(API.DOC.DATA, {}, function (res) {
        obj.cache.doc = res.data;
    });

    obj.set_scope = function ($scope) {
        obj.$scope = $scope;
    }

    obj.data = function () {
        if (obj.$scope) {
            if (obj.$scope.transform) {
                return obj.$scope.transform();
            }
            return obj.$scope.data;
        }
        return obj.cache.doc.draft.data;
    }

    obj.title = function () {
        if (obj.$scope) {
            if (obj.$scope.title) {
                return obj.$scope.title();
            }
        }
        return "";
    }

    obj.delete = function (cb) {
        fn(API.DOC.DELETE, {}, cb);
    };

    obj.init = function (cb) {
        if (obj.cache.doc) {
            return cb(obj.cache.doc);
        }
        setTimeout(function () {
            obj.init(cb);
        }, 500);
    };

    obj.draft = function (title, data, cb) {
        data = JSON.stringify(data);
        fn(API.PROCESS.DRAFT, { title: title, data: data }, cb);
    };

    obj.submit = function (title, cb) {
        fn(API.PROCESS.SUBMIT, {title: title}, cb);
    };

    obj.approve = function (response, cb) {
        response = response;
        fn(API.PROCESS.APPROVE, { response: response }, cb);
    };

    obj.reject = function (response, cb) {
        response = response;
        fn(API.PROCESS.REJECT, { response: response }, cb);
    };

    obj.cancel = function (cb) {
        fn(API.PROCESS.CANCEL, {}, cb);
    };

    obj.upload = function (form_data, cb, onprocess) {
        $.ajax({
            url: API.DOC.UPLOAD,
            type: 'POST',
            xhr: function () {
                var myXhr = $.ajaxSettings.xhr();
                if (myXhr.upload) {
                    myXhr.upload.addEventListener('progress', function (event) {
                        var percent = 0;
                        var position = event.loaded || event.position;
                        var total = event.total;
                        if (event.lengthComputable) {
                            percent = Math.round(position / total * 10000) / 100;
                        }
                        if (onprocess) onprocess(percent);
                    }, false);
                }
                return myXhr;
            },
            data: form_data,
            cache: false,
            contentType: false,
            processData: false
        }).always(function (res) {
            cb(res);
        });
    }

    return obj;
};