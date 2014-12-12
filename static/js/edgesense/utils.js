jQuery(function($) {
    "use strict";
    
    Edgesense.FullUrl = (function() {
        var base = window.location.protocol + '//' + window.location.hostname;
        base += window.location.port ? (':' + window.location.port) : '';
        base += window.location.pathname;
        if (base.match(/\/$/)) {
            base = base.substring(0, base.length - 1);
        }
        
        var full = function(path){
            return base+path;
        }
        return full;
    })();
    
    Edgesense.Configuration = function(){

        var base_url = Edgesense.FullUrl('/json'),
            file = 'configuration.json',
            data = undefined,
            build = function(d){
                data = d;
            };

        function c(){
        };

        c.base = function(url){
            if (!arguments.length) return base_url;

            base_url = url;

            return c;
        };

        c.file = function(filename){
            if (!arguments.length) return file;

            file = filename;

            return c;
        };

        c.load = function(){
            
            $.ajax({
              dataType: "json",
              async: false,
              url: base_url+"/"+file, 
              success: build
            });

            return c;
        };
        
        c.data = function(d){
            if (!arguments.length) return data;

            data = d;

            return c;
        };
        
        c.get = function(key){
            return data[key];
        };

        return c;
    };
    
});
