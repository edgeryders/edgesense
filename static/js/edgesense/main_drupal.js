;(function(undefined) {
  'use strict';
  
  // defines the main object holding all the 
  // code / data for the dashboard
  if (window.Edgesense === void 0) {
      window.Edgesense = new Object();        
  }

  // asynchronous loading of the js files
  $script('//ajax.googleapis.com/ajax/libs/jquery/2.0.2/jquery.min.js', function() {
      $script(['js/jquery-ui-1.10.3.min.js', 
               'js/underscore-min.js', 
               'js/bootstrap.min.js', 
               'js/plugins/iCheck/icheck.min.js',
               'js/plugins/ionslider/ion.rangeSlider.min.js'
              ], 'base');
  });

  $script('js/d3.v3.min.js', function() {
      $script(['js/rickshaw.min.js', 
               'js/crossfilter.min.js'
              ], 'd3');
  });

  $script('js/sigma.min.js', function() {
      $script(['js/plugins/sigma/sigma.layout.forceAtlas2.min.js', 
               'js/edgesense/sigma.js'
              ], 'sigma');
  });

  $script.ready(['base', 'd3', 'sigma'], function () {
    
      $script(['js/edgesense/utils.js',
               'js/edgesense/help.js',
               'js/edgesense/analytics.js',
               'js/edgesense/tutorial.js',
               'js/edgesense/dashboard.js'
              ], function(){
                  $script('js/edgesense/run_drupal.js');
              });
  })
}).call(this);


