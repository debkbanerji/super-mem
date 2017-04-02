angular.module('superMemApp').config(['$locationProvider', '$routeProvider',
    function config($locationProvider, $routeProvider) {
        $locationProvider.hashPrefix('!');

        $routeProvider.when('/about', {
            template: '<about></about>'
        }).when('/view-memes', {
            template: '<view-memes></view-memes>'
        }).when('/upload-memes', {
            template: '<upload-memes></upload-memes>'
        }).when('/developer-mode', {
            template: '<developer-mode></developer-mode>'
        }).when('/login', {
            template: '<login></login>'
        }).otherwise('/view-memes');


        // use the HTML5 History API
        $locationProvider.html5Mode(true);
    }

]);