jQuery(function($) {
    "use strict";
    
    Edgesense.Analytics = function(){

        var tracking_id = undefined;

        function a(){
        };

        a.tracking_id = function(id){
            if (!arguments.length) return tracking_id;

            tracking_id = id;

            return a;
        };

        a.start = function(){
            if (!tracking_id) {
                return a;                
            }
            
            (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
            (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
            m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
            })(window,document,'script','//www.google-analytics.com/analytics.js','_ga_tracker');

            _ga_tracker('create', tracking_id, { 'cookieDomain': 'none' });
            _ga_tracker('send', 'pageview');

            return a;
        };
        
        a.track = function(category, action, label, value ){
            _ga_tracker('send', 'event', category, action, label, value);
        };

        return a;
    };
    
});
