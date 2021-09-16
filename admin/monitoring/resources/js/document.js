var content_controller = function ($sce, $scope, $timeout) {
    var API = {
        SEARCH: '/form/admin/monitoring/api/document/search'
    };

    $scope.loading = true;

    $scope.math = Math;
    $scope.list = [];
    $scope.facet = {};

    $scope.search = search;
    if (!$scope.search.page) $scope.search.page = 1;
    if (!$scope.search.text) $scope.search.text = "";

    $scope.event = {};
    $scope.event.docviewer = function (item) {
        $scope.loading = true;
        $timeout(function () {
            var url = '/form/admin/form/iframe/' + item.form.id + '/' + item.id;
            $('#modal-document iframe').attr('src', url);
            $('#modal-document iframe').on('load', function () {
                $scope.loading = false;
                $timeout();
                $('#modal-document').modal('show');
            });
        })

    }

    $scope.event.delete = function (item) {
        var pd = angular.copy(item);
        $.post(API.DELETE, pd, function (res) {
            if (res.code == 200) {
                location.reload();
            }
            $timeout();
        })
    }

    $scope.event.pagination = function () {
        var lastpage = $scope.facet.lastpage * 1;
        var startpage = Math.floor(($scope.search.page - 1) / 10) * 10 + 1;

        $scope.facet.pages = [];
        for (var i = 0; i < 10; i++) {
            if (startpage + i > lastpage) break;
            $scope.facet.pages.push(startpage + i);
        }

        $timeout();
    }

    $scope.event.load = function () {
        var pd = angular.copy($scope.search);
        $.post(API.SEARCH, pd, function (res) {
            if (res.code == 200) {
                $scope.facet.lastpage = res.data.lastpage;
                $scope.facet.total = res.data.total;
                $scope.list = res.data.list;
                $scope.event.pagination();
                $scope.loading = false;
            }
            $timeout();
        })
    }

    $scope.event.search = function () {
        $scope.search.page = 1;
        var q = Object.entries(angular.copy($scope.search)).map(e => e.join('=')).join('&');
        location.href = "?" + q;
    }

    $scope.event.page = function (page) {
        if (page < 1) {
            toastr.error('첫 페이지 입니다');
            return;
        }
        if (page > $scope.facet.lastpage) {
            toastr.error('마지막 페이지 입니다');
            return;
        }

        if ($scope.search.page == page) {
            return;
        }

        $scope.search.page = page;
        var q = Object.entries(angular.copy($scope.search)).map(e => e.join('=')).join('&');
        location.href = "?" + q;
    }

    $scope.event.load();
};