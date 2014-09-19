jQuery(function($) {
    "use strict";
    
    Edgesense.Help = function(){

        var base_url = Edgesense.FullUrl('/json'),
            file = 'help.json',
            lang = 'en',
            data = undefined,
            helped = undefined,
            analytics = undefined,
            make_popover = function(element, key, placement){
              $(element).popover({
                  placement: placement||'auto',
                  content: data[lang][key],
                  trigger: 'manual'
              }).on('shown.bs.popover', function () {
                  if (analytics) {
                      analytics.track('help', 'toggle', key, 1);
                  }
              }).on('hidden.bs.popover', function () {
                  if (analytics) {
                      analytics.track('help', 'toggle', key, 0);
                  }
              })  
            },
            activate = function(element){
              var help_key = $(element).data('help');
              var help_placement = $(element).data('help-placement');
              if (help_key && data[lang][help_key]) {
                  var help_button = $('<i class="help-button fa fa-fw fa-question-circle"></i>');
                  $(element).append(help_button);
                  help_button.position({
                                  my: "right-3 top+4",
                                  at: "right top",
                                  of: $(element),
                                  within: $(element)
                              });
                  
                  make_popover(element,help_key, help_placement);
                  
                  help_button.on('click', function(){
                      $(element).popover('toggle');
                  });
              }  
            },
            build = function(d){
                data = d;
                helped = $('.helped');
                _.each(helped, activate);
            };

        function h(){
        };

        h.base = function(url){
            if (!arguments.length) return base_url;

            base_url = url;

            return h;
        };

        h.file = function(filename){
            if (!arguments.length) return file;

            file = filename;

            return h;
        };

        h.analytics = function(a){
            if (!arguments.length) return analytics;

            analytics = a;

            return h;
        };

        h.load = function(){
            
            $.ajax({
              dataType: "json",
              url: base_url+"/"+file, 
              success: build
            });

            return h;
        };
        
        h.data = function(){
            return data;
        };

        return h;
    };

});
