jQuery(function($) {
    "use strict";
    
    $('.popover-toggle').popover({
        container: 'body',
        html: true,
        placement: 'bottom',
        content: function () {
            return $(this).next('.popover-content').html();
        }
    });
    
    /*
     * We are gonna initialize all checkbox and radio inputs to 
     * iCheck plugin in.
     * You can find the documentation at http://fronteed.com/iCheck/
     */
    $("input[type='checkbox'], input[type='radio']").iCheck({
        checkboxClass: 'icheckbox_minimal',
        radioClass: 'iradio_minimal'
    });

    Edgesense.FullUrl = (function() {
      var regexp = /(.*)\/sites\/.*/g;
      var match = regexp.exec(window.location.href);
      var base = match[1];
      base += "/sites/default/files/edgesense";

      var full = function(path){
        return base+path;
      }
      return full;
    })();

    var cur_date = new Date();
    var cur_time = cur_date.getTime();
    
    // Load the main configuration
    var configuration = Edgesense.Configuration().file('configuration.json?'+cur_time).load();
    
    // The script produces an index json with the last date when it was run
    $.ajax({
      dataType: "json",
      async: false,
      url: Edgesense.FullUrl("/json/last.json?"+cur_time), 
      success: function( d ) {
          
          var dashboard = Edgesense.Dashboard().configuration(configuration);
          
          // Activate the analytics
          var analytics_tracking_id = configuration.get("analytics_tracking_id");
          if (analytics_tracking_id) {
              var analytics = Edgesense.
                               Analytics().
                               tracking_id(analytics_tracking_id).
                               start();
              dashboard.analytics(analytics);
          }

          var base_data_url = configuration.get("base_data_url");
          if (_.isEmpty(base_data_url)) {
              base_data_url = Edgesense.FullUrl('/json/data/');              
          }
    
          if (base_data_url.match(/\/$/)) {
              base_data_url = base_data_url.substring(0, base_data_url.length - 1);
          }
          dashboard
              .base(base_data_url+'/'+d.last)
              .show_datapackage(d.datapackage)
              .load('network.min.json?'+cur_time)
              .run();
          
          Edgesense.Help().analytics(dashboard.analytics()).load();
          
          Edgesense.Tutorial.dashboard(dashboard).setup();
          
          Edgesense.current = dashboard;
      }
    });
    
});
