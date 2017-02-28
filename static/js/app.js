var app = angular.module('bugee', ['ngTagsInput']);
app.controller('formController', function($scope, $http, $sce) {

    $scope.searchResults = [];
    $scope.bugInfo = {};

    $scope.search = function() {
        $scope.searchFlag = false;
        searchHelper();

    };

    searchHelper = function() {
        if ($scope.searchText && ($scope.searchText).length > 3) {
            $scope.searchResults = [];
            var dataObj = {
                text: $scope.searchText,
                tags: $scope.tags
            };
            $http({
                method: 'POST',
                url: 'search',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: JSON.stringify(dataObj)
            }).then(function successCallback(response) {
                $scope.searchResults = [];
                hits = response.data.hits.hits
                for (var i = 0; i < hits.length; i++) {
                    $scope.searchResults.push({
                        "id": hits[i]["_id"],
                        "subject": $sce.trustAsHtml(hits[i]["highlight"]["SUBJECT"][0])
                    })
                }

            }, function errorCallback(response) {
                console.log(response.statusText);
            });
        }else{
             $scope.searchResults = [];
        }
    }
    $scope.searchAll = function() {
        $scope.searchFlag = true;
        searchAllHelper();

    };
    searchAllHelper = function() {
        $scope.searchResults = [];
        var dataObj = {
            text: $scope.searchText,
            tags: $scope.tags
        };
        $http({
            method: 'POST',
            url: 'searchAll',
            headers: {
                'Content-Type': 'application/json'
            },
            data: JSON.stringify(dataObj)
        }).then(function successCallback(response) {
            $scope.searchResults = [];
            hits = response.data.hits.hits
            for (var i = 0; i < hits.length; i++) {
                $scope.searchResults.push({
                    "id": hits[i]["_source"]["RPTNO"],
                    "subject": $sce.trustAsHtml(hits[i]["_source"]["SUBJECT"])
                })
            }

        }, function errorCallback(response) {
            console.log(response.statusText);
        });
    }
    $scope.getBugDetails = function(bugId) {

        $http({
            method: 'GET',
            url: 'bug/' + bugId

        }).then(function successCallback(response) {
            $scope.bugInfo = response.data

        }, function errorCallback(response) {
            console.log(response.statusText);
        });
    };
    $scope.tags = [

    ];
    $scope.searchText = "";

    $scope.tagAdded = function(tag) {
        if ($scope.searchFlag)
            searchAllHelper();
        else
            searchHelper();
    };
    $scope.tagRemoved = function(tag) {
        if ($scope.searchFlag)
            searchAllHelper();
        else
            searchHelper();
    };

    $scope.loadTags = function(query) {
        var result = [];

        return $http({
            method: 'GET',
            url: '/suggest',
            params: {
                "query": query
            }

        }).then(function successCallback(response) {
            var resp = response.data
            result = [];
            for (var i in resp) {
                result.push({
                    "text": resp[i]["_id"]
                })

            }

            return result;

        }, function errorCallback(response) {
            console.log(response.statusText);
            return result;
        });


    };



});