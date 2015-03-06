'use strict';
/* App Module */
angular.module('foosball', ['foosballServices', 'ngRoute']).
    config(['$interpolateProvider', '$routeProvider',
     function ($interpolateProvider, $routeProvider) {
       $interpolateProvider.startSymbol('[[');
       $interpolateProvider.endSymbol(']]');
       $routeProvider.
        when('/',
            {templateUrl: 'static/ang_templs/welcome.html',
             controller: 'WelcomeCtrl'}).
        when('/login',
            {templateUrl: 'static/ang_templs/login.html',
             controller: 'LoginCtrl'}).
        when('/newplayer',
            {templateUrl: 'static/ang_templs/nuplayer.html',
             controller: 'LoginCtrl'}).
        when('/game/:gameid',
            {templateUrl: 'static/ang_templs/ingame.html',
             controller: 'GameCtrl'}).
        when('/recgame',
            {templateUrl: 'static/ang_templs/recordgame.html',
             controller: 'RecGameCtrl'}).
        otherwise({redirectTo: '/'});
}]);
