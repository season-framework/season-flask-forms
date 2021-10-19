var content_controller = function ($scope, $timeout, $sce) {
    _builder($scope, $timeout);
    $scope.trustAsHtml = $sce.trustAsHtml;
    $scope.math = Math;
    $scope.category = category;

    var API_URL = "/form/admin/form";
    var API = {
        INFO: API_URL + '/api/info/' + app_id + "/" + version,
        DELETE: API_URL + '/api/delete',
        FLUSH: API_URL + '/api/flush',
        UPDATE: API_URL + '/api/update/' + app_id,
        PUBLISH: API_URL + '/api/publish/' + app_id,
        UPLOAD: API_URL + '/api/upload',
        LIST: API_URL,
        IFRAME: function (app_id) {
            if ($scope.info.viewuri) {
                return $scope.info.viewuri;
            }
            return API_URL + "/iframe/" + app_id + '?mode=' + $scope.preview_mode + '&time=' + new Date().getTime();
        }
    };

    $scope.preview_mode = "edit";

    try {
        $scope.options = JSON.parse(localStorage["form.option"])
    } catch (e) {
        $scope.options = {};
        $scope.options.layout = 2;
        $scope.options.tab = {};
        $scope.options.tab['tab1_val'] = 'html';
        $scope.options.tab['tab2_val'] = 'preview';
        $scope.options.tab['tab5_val'] = 'debug';
        $scope.options.infotab = 1;
        $scope.options.sidemenu = true;
    }

    $scope.$watch("options", function () {
        var opt = angular.copy($scope.options);
        localStorage["form.option"] = JSON.stringify(opt);
    }, true);

    $scope.event = {};

    $scope.event.change_preview = function () {
        if ($scope.preview_mode == "view") {
            $scope.preview_mode = 'edit';
        } else {
            $scope.preview_mode = 'view';
        }
        $scope.event.iframe();
    }

    $scope.event.flush = function () {
        $.get(API.FLUSH, { id: app_id }, function (res) {
            $scope.event.iframe();
        });
    }

    $scope.event.delete = function () {
        $.get(API.DELETE, { id: app_id }, function (res) {
            location.href = API.LIST;
        });
    }

    $scope.event.modal = {};
    $scope.event.modal.delete = function () {
        $('#modal-delete').modal('show');
    }

    $scope.event.iframe = function (findurl) {
        var url = API.IFRAME(app_id, app_id);
        if (findurl) {
            return url;
        }
        $timeout(function () {
            $('iframe.preview').attr('src', url);
        });
    };

    $scope.event.publish = function (cb) {
        var data = angular.copy($scope.info);

        $.post(API.PUBLISH, data, function (res) {
            $scope.event.iframe();
            if (cb) return cb(res);
            if (res.code == 200) {
                location.href = "?version=master";
                return
            }
            toastr.error('Error');
        });
    }

    $scope.event.save = function (cb) {
        try { $scope.info.html = $scope.info.html.replace(/\t/gim, '    '); } catch (e) { }
        try { $scope.info.html_view = $scope.info.html_view.replace(/\t/gim, '    '); } catch (e) { }
        try { $scope.info.css = $scope.info.css.replace(/\t/gim, '    '); } catch (e) { }
        try { $scope.info.js = $scope.info.js.replace(/\t/gim, '    '); } catch (e) { }
        try { $scope.info.api = $scope.info.api.replace(/\t/gim, '    '); } catch (e) { }

        var data = angular.copy($scope.info);

        $.post(API.UPDATE, data, function (res) {
            if ($scope.info.version != "master") {
                location.href = "?version=master"
                return;
            }
            $scope.event.iframe();
            if (cb) return cb(res);
            if (res.code == 200) {
                return toastr.success('Saved');
            }
            toastr.error('Error');
        });
    }

    // import from file
    $scope.event.select_file = function () {
        $('#import-file').click();
    }

    $('#import-file').change(function () {
        var fr = new FileReader();
        fr.onload = function () {
            var data = fr.result;
            var json = JSON.parse(data);
            $scope.info.html = json.html;
            $scope.info.js = json.js;
            $scope.info.css = json.css;
            $scope.info.api = json.api;
            $scope.event.save();
        };
        fr.readAsText($('#import-file').prop('files')[0]);
    });

    // init page
    $.get(API.INFO, function (res) {
        $scope.info = res.data;
        $scope.event.iframe();
        $timeout();
    });

    // shortcut
    shortcutjs(window, {
        'Ctrl KeyS': function (ev) {
            ev.preventDefault();
            $scope.event.save();
        },
        'default': function (ev, name) {
        }
    });

    // drag event
    var dragbasewidth = 0;
    var dragbaseheight = 0;
    var vh50 = window.innerHeight / 2;
    $scope.status_drag = '';
    $scope.event.drag = {
        onstart: function (self) {
            $scope.status_drag = 'unselectable';
            $timeout();

            vh50 = window.innerHeight / 2;

            var target = $(self.element).attr('target');
            dragbasewidth = $('.' + target).width();

            var tds = $('.code-top td.bg-white');
            for (var i = 0; i < tds.length; i++) {
                var w = $(tds[i]).width();
                if (i == tds.length - 1) {
                    $(tds[i]).width('auto');
                } else {
                    $(tds[i]).width(w);
                }
            }

            var tds = $('.code-tabs-top td');
            for (var i = 0; i < tds.length; i++) {
                var w = $(tds[i]).width();
                if (i == tds.length - 1) {
                    $(tds[i]).width('auto');
                } else {
                    $(tds[i]).width(w);
                }
            }

            if ($scope.options.layout < 5) return;
            dragbaseheight = $('.tab-5').height();
        },
        onmove: function (self, pos) {
            var target = $(self.element).attr('target');

            if (target == 'tab-5') {
                var move_y = pos.y;
                var resize_h = dragbaseheight - move_y - 1;
                var base_h = vh50 - 65;
                var diff = base_h - resize_h;
                var hstr = 'calc(100vh - 130px - ' + resize_h + 'px)';
                $('.code-top td').height(hstr);
                hstr = 'calc(100vh - 132px - ' + resize_h + 'px)';
                $('.code-top td .code-input').height(hstr);
                $('.code-top td .code-input .CodeMirror').height(hstr);

                $('.code-bottom td').height(resize_h);
                $('.code-bottom td .code-input').height(resize_h);
                $('.code-bottom td .code-input .CodeMirror').height(resize_h);

                return;
            }

            var move_x = pos.x;

            if (dragbasewidth + move_x - 1 < 400) return;
            if (move_x > 0 && $('.code-top td.bg-white:last-child').width() < 400) {
                return;
            }

            $('.' + target).width(dragbasewidth + move_x - 1);
        },
        onend: function (self) {
            $scope.status_drag = '';
            $timeout();
        }
    };

    $timeout(function () {
        if ($scope.options.layout > 4) {
            var resize_h = 300;
            var hstr = 'calc(100vh - 130px - ' + resize_h + 'px)';
            $('.code-top td').height(hstr);
            hstr = 'calc(100vh - 132px - ' + resize_h + 'px)';
            $('.code-top td .code-input').height(hstr);
            $('.code-top td .code-input .CodeMirror').height(hstr);

            $('.code-bottom td').height(resize_h);
            $('.code-bottom td .code-input').height(resize_h);
            $('.code-bottom td .code-input .CodeMirror').height(resize_h);
        }
    })

    $scope.$watch('options.tab', function () {
        try {
            var hstr = $('.code-top td')[0].style.height;
            $timeout(function () {
                $('.h-half .code-top td .code-input').height(hstr);
                $('.h-half .code-top td .code-input .CodeMirror').height(hstr);
            });
        } catch (e) {
        }
    }, true);

    $scope.event.toggle = {};
    $scope.event.toggle.sidemenu = function () {
        $scope.options.sidemenu = !$scope.options.sidemenu;
        $timeout();
    }
};