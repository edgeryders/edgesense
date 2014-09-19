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
    
    // Load the main configuration
    var configuration = Edgesense.Configuration().load();
    
    // The script produces an index json with the last date when it was run
    $.ajax({
      dataType: "json",
      async: false,
      url: Edgesense.FullUrl("/json/last.json"), 
      success: function( d ) {
          
          var dashboard = Edgesense.Dashboard().configuration(configuration);
          
          var base_data_url = configuration.get("base_data_url");
          if (_.isEmpty(base_data_url)) {
              base_data_url = Edgesense.FullUrl('/json/data/');              
          }
    
          if (base_data_url.match(/\/$/)) {
              base_data_url = base_data_url.substring(0, base_data_url.length - 1);
          }
          dashboard
              .base(base_data_url+'/'+d.last)
              .load('network.min.json')
              .run();
          
          Edgesense.Tutorial.dashboard(dashboard).setup();
          
          Edgesense.current = dashboard;
      }
    });
    
});
