jQuery(function($) {
    "use strict";
    
    var VerticalMarker = Rickshaw.Class.create({

    	initialize: function(args) {

    		var graph = this.graph = args.graph;

    		var element = this.element = document.createElement('div');
    		element.className = 'detail';

    		graph.element.appendChild(element);

    	},

    	render: function(point) {

    		var graph = this.graph;
            if (point) {
        		this.element.innerHTML = '';
        		this.element.style.left = graph.x(point.x) + 'px';                
            }

    	},

    });
    
    Edgesense.Dashboard = function(){

        var configuration = undefined,
            analytics = {track: function(){ console.log(['analytics.track', arguments]); }},
            base_url = undefined,
            file = undefined,
            data = undefined,
            slider_date_format = function(date, from_time, to_time) {
                var _cache = {};
                var from_ts = d3.round(from_time.getTime()/1000);
                var to_ts = d3.round(to_time.getTime()/1000);
                var ts_key = from_ts+" "+to_ts;
                
                if (!_cache[ts_key]) {
                    _cache[ts_key] = d3.time.format.multi([
                        ["%B %e, %Y", function(d) { return from_time.getFullYear() != to_time.getFullYear(); }],
                        ["%B %e", function(d) { return from_time.getMonth() != to_time.getMonth() || ((to_time.getTime() - from_time.getTime()) > 7*24*60*60*1000); }],
                        ["%B %e - %H:%M", function(d) { return from_time.getDay() != to_time.getDay(); }],
                        ["%H:%M", function(d) { return true; }]
                    ]);
                }
                return _cache[ts_key](date);
                // d3.time.format('%B %d, %Y');
            },
            chart_date_format = function(date, from_time, to_time) {
                var _cache = {};
                var from_ts = d3.round(from_time.getTime()/1000);
                var to_ts = d3.round(to_time.getTime()/1000);
                var ts_key = from_ts+" "+to_ts;
                
                if (!_cache[ts_key]) {
                    _cache[ts_key] = d3.time.format.multi([
                        [" %e/%m", function(d) { return (from_time.getMonth() != to_time.getMonth()) || (from_time.getFullYear() != to_time.getFullYear()); }],
                        [" %e/%m", function(d) { return ((to_time.getTime() - from_time.getTime()) > 2*24*60*60*1000); }],
                        [" %H:%M", function(d) { return true; }]
                    ]);
                }
                return _cache[ts_key](date);
                // d3.time.format(' %e/%m');
            },
            track_date_format = d3.time.format('%Y/%m/%d %H:%M'),
            color_scale = d3.scale.category20(),
            generated = undefined,
            metrics_cf = undefined,
            metrics_bydate = undefined,
            nodes_cf = undefined,
            nodes_bydate = undefined,
            edges_cf = undefined,
            edges_bydate = undefined,
            from_date = undefined,
            to_date = undefined,
            graphs = {},
            current_metrics = undefined,
            first_metrics = undefined,
            last_metrics = undefined,
            network_graph = undefined,
            nodes_map = {},
            to_expose = undefined,
            network_lock = undefined,
            node_fill_transparent = 'rgba(204,204,204,0.1)',
            edge_transparent = 'rgba(204,204,204,0.1)',
            node_border_default = 'rgba(240, 240, 240, 1)', 
            node_border_transparent = 'rgba(240, 240, 240, 0.1)',
            node_fill_isolated = 'rgba(160,160,160,0.2)',
            node_border_isolated = 'rgba(250,250,250,1)',
            node_fill_team = 'rgba(32, 32, 32, 1)',
            selected_partitions = [],  
            current_user_filter = '',
            show_moderators = true,
            show_datapackage = false,
            names_map = {},
            mapped_name = function(name){
                // map names if the names_map is defined
                if (_.isObject(names_map) && _.has(names_map, name)){
                    return names_map[name];
                }
                return name;
            },
            preprocess_data = function(d){
                data = d;
                
                if (data['meta'] && data['meta']['generated']) {
                    data['meta']['generated'] = new Date(data['meta']['generated']*1000);                    
                }
                
                _.each(data['metrics'], function(e){
                    e['date'] = new Date(e['ts']*1000);           
                });

                _.each(data['nodes'], function(e){
                    e['date'] = new Date(e['created_ts']*1000); 
                    e['name'] = mapped_name(e['name']);
                });

                _.each(data['edges'], function(e){
                    e['date'] = new Date(e['ts']*1000);           
                });
                
            },
            update_filter = function(i){
                current_metrics = data['metrics'][i];
                metrics_bydate.filter([0, current_metrics.date]);
                
                // Update each metrics
                _.each($('.metric'), update_metric);
                
                // Update the markers
                _.each(graphs, update_marker);
                
                // Update the graph
                if (!network_graph) {
                    return;
                }
                // filter the edges and nodes
                nodes_bydate.filter([0, current_metrics.date]);
                edges_bydate.filter([0, current_metrics.date]);
                update_network_graph();
                
            },
            toggle_partition = function(e){
                var b = $(this);
                var shown = 0;
                if (_.indexOf(selected_partitions, b.data('partition'))>=0) {
                    selected_partitions = _.without(selected_partitions, b.data('partition')) 
                    b.find('.fa').removeClass('fa-check-square-o').addClass('fa-square-o');                        
                } else {
                    selected_partitions.push(b.data('partition'))
                    b.find('.fa').removeClass('fa-square-o').addClass('fa-check-square-o');
                    shown = 1;
                }
                update_network_graph();
                analytics.track('filter', 'toggle_partition', 'part #'+b.data('partition'), shown);
            },
            update_network_graph = function(){
                close_node_popover();
                network_graph.graph.clear();
                network_graph.graph.read(filtered_graph());
                update_hidden();
                update_exposed();
                network_graph.refresh();
            },
            update_hidden = function(){
                _.each(network_graph.graph.nodes(), function(n){ 
                    var partition = last_metrics.partitions[n.id];
                    var to_hide = _.indexOf(selected_partitions, partition)<0 && !n.isolated;
                    if (n.team) {
                        to_hide = to_hide || !show_moderators;
                    } 
                    n.hidden = to_hide;
                });
                network_graph.refresh();                
            },
            update_exposed = function(){
                network_graph.graph.nodes().forEach(function(n) {
                  if (!to_expose || to_expose[n.id]) {
                      n.color =  node_fill_color(n);
                      n.border_color = node_border_default;                      
                  } else {
                      n.color = node_fill_transparent;                      
                      n.border_color = node_border_transparent;                      
                  }
                });

                network_graph.graph.edges().forEach(function(e) {
                  if (!to_expose || (to_expose[e.source] && to_expose[e.target])) {
                      e.color = edge_color(e);                      
                  } else {
                      e.color = edge_transparent;                      
                  }
                });                
            },
            close_node_popover = function(){
                $('#node-marker').hide();
                $('#node-marker').popover('destroy');
                
            },
            node_popover_content = function(node){
                var in_degree = current_metrics[metric_name_prefixed('in_degree')][node.id];
                var out_degree = current_metrics[metric_name_prefixed('out_degree')][node.id];
                var betweenness = current_metrics[metric_name_prefixed('betweenness')][node.id];
                var cont_div = $('<div class="node-hover-content"><div class="node-hover-title"></div><ul class="node-hover-data"></ul></div>');
                if ( nodes_map[node.id].link ) {
                    var nodelink = $('<a>').
                                        attr('href', nodes_map[node.id].link).
                                        attr('target', "_blank").
                                        html(node.name);
                                        
                    cont_div.children('.node-hover-title').append(nodelink);                    
                } else {
                    cont_div.children('.node-hover-title').html(node.name);
                }
                cont_div.children('ul').append('<li><span>In degree:</span> '+in_degree+'</li>');
                cont_div.children('ul').append('<li><span>Out degree:</span> '+out_degree+'</li>');
                cont_div.children('ul').append('<li><span>Betweenness:</span> '+d3.round(betweenness, 4)+'</li>');
                return cont_div.html();
            },
            filtered_graph = function(){
                var G = {};
                G['nodes'] = _.map(nodes_bydate.top(Infinity), function(node){
                    var size = node.size ? node.size : 1;
                    return {
                      id: node.id,
                      // label: "",
                      name: node.name,
                      // Display attributes:
                      x: node.x,
                      y: node.y,
                      size: size,
                      color:  node_fill_color(node),
                      type: 'border',
                      border_color: node_border_color(node),
                      team: node.team,
                      isolated: node.isolated,
                      ts: node.created_ts,
                      date: node.date,
                      link: node.link
                    };
                });
                // merge multiedges
                var edges_map = {}
                _.each(edges_bydate.top(Infinity), function(edge){
                    var edge_id = edge.source+"_"+edge.target;
                    var merged_edge = edges_map[edge_id];
                    if(!merged_edge) {
                        merged_edge = {
                            id: edge_id,
                            source: edge.source,
                            target: edge.target,
                            weight: 1,
                            type: 'curve',
                            color: edge_color(edge)
                        }
                        edges_map[edge_id] = merged_edge;
                    } else {
                        merged_edge['weight'] = merged_edge['weight']+1;
                    }
                });
                G['edges'] = _.values(edges_map);
                return G
            },
            metric_name_prefixed = function(metric_name){
                if (show_moderators) {
                    return 'full:'+metric_name;
                } else {
                    return 'user:'+metric_name;
                }  
            },
            update_metric = function(e){
                var metric_name = metric_name_prefixed($(e).data('metric-name'));
                
                    
                var rounding = $(e).data('metric-round');
                if (!rounding) {
                    rounding = 4;
                }
                var value = d3.round(current_metrics[metric_name], rounding);
                $(e).find('.value').html(value);
                
                var chart_obj = graphs[metric_name];
                if (chart_obj) {
                    // chart.series[0].data=metric_series(metric_name);
                    chart_obj.chart.series[1].data=[{x:current_metrics['ts'],y:current_metrics[metric_name]}];
                    chart_obj.chart.update();
                }
            },
            update_marker = function(chart_obj) {
                if (chart_obj.marker) {
                    chart_obj.marker.render({x:current_metrics['ts']});
                }
            },
            metric_series = function(metric_name){
                var metric_values = _.map(metrics_bydate.top(Infinity), function(m){
                  return {
                      x: m['ts'],
                      y: m[metric_name]
                  }
                });
                metric_values = _.sortBy(metric_values, function(e){ return e.x; } )
                return metric_values;
            },            
            build_graph = function(e){
                var minichart = $(e).find('.minichart')[0];
                if (!minichart) { return; }
                var metric_name = metric_name_prefixed($(e).data('metric-name'));
                var complete_metric = global_metric_series(metric_name);
                var max_metric_value = _.max(complete_metric, function(e){ return e.y!=undefined ? e.y : 0; } ).y;
                var min_metric_value = _.min(complete_metric, function(e){ return e.y!=undefined ? e.y : max_metric_value; } ).y;
                var chart = new Rickshaw.Graph( {
                    element: minichart, 
                    renderer: 'multi',
                    interpolation: 'linear',
                    width: $(minichart).width(),
                    height: 73,
                    dotSize: 4,
                    max: max_metric_value+(max_metric_value*0.05),
                    min: min_metric_value-(min_metric_value*0.05),
                    padding: {
                        top: 0.06,
                        right: 0.06,
                        bottom: 0.06,
                        left: 0.02
                    },
                    series: [{
                        color: 'white',
                        data: global_metric_series(metric_name),
                        renderer: 'line'
                    },{
                        color: 'white',
                        data: [{x:current_metrics['ts'],y:current_metrics[metric_name]}],
                        renderer: 'scatterplot'                        
                    }]
                });
                chart.render();
                var from_ts = from_date.getTime()/1000;//ts here are in mill
                var to_ts = to_date.getTime()/1000;
                var unit = {
        			name: 'week',
        			seconds: (to_ts-from_ts)/6, 
        			formatter: function(d) { return chart_date_format(d, from_date, to_date); }
                };

                var axes = new Rickshaw.Graph.Axis.Time( {
                    graph: chart,
                    timeUnit: unit
                } );
                axes.render();
                
                graphs[metric_name] = {chart: chart};
                
            },
            metric_color = function(metric_name) {
              var regex = /(.+):/i;
              var match = regex.exec(metric_name);
              var color_map = {
                  team:'rgb(255, 127, 0)',
                  full:'rgb(51, 160, 44)',
                  user:'rgb(31, 120, 180)',
              };
              var color = color_map[match[1]];
              if (!color){ color = 'rgb(190, 190, 190)'; }
              return color;
            },
            global_metric_series = function(metric_name){
                var metric_values = _.map(data['metrics'], function(m){
                  return {
                      x: m['ts'],
                      y: m[metric_name]
                  }
                });
                metric_values = _.sortBy(metric_values, function(e){ return e.x; } )
                return metric_values;
            },
            build_multi_graph = function(e){
                var metric_names = $(e).data('metric-name').split(",");
                var metric_labels = $(e).data('metric-legend').split(",");
                var metric_colors = []
                if ($(e).data('metric-colors')) { metric_colors = $(e).data('metric-colors').split(",");}
                var series = [];
                _.each(metric_names, function(metric_name, idx){
                    var metric_series = global_metric_series(metric_name);
                    var color = metric_colors[idx]||metric_color(metric_name);
                    series.push({
                        color: color,
                        data: metric_series,
                        name: metric_labels[idx]                     
                    })
                })
                var series_values = _.flatten(_.map(series, function(e){ return _.map(e.data, function(j){ return j.y; });}));
                var max_metric_value = _.max(series_values);
                var min_metric_value = _.min(series_values);
                
                var outer_container = $(e).find('.chart-cnt');
                var base_size = (outer_container.width()*9.5/10.0)-20;
                outer_container.height(base_size).html('<div class="y_ax"></div><div class="chart"></div>');
                var graph_container = outer_container.find('.chart').width(base_size-10).height(base_size)[0];
                var y_axis_container = outer_container.find('.y_ax').width(30).height(base_size)[0];
                var chart = new Rickshaw.Graph( {
                    element: graph_container, 
                    renderer: 'line',
                    height: base_size-18,
                    max: max_metric_value+(max_metric_value*0.08),
                    min: min_metric_value-(min_metric_value*0.08),
                    padding: {
                      top: 0.015,
                      right: 0.015,
                      bottom: 0.02,
                      left: 0.015
                    },
                    interpolation: 'linear',
                    series: series
                });
                var x_axis = new Rickshaw.Graph.Axis.Time( { 
                    graph: chart, 
                    orientation: 'bottom'
                } );
                var y_axis = new Rickshaw.Graph.Axis.Y( {
                        graph: chart,
                        orientation: 'left',
                        tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
                        element: y_axis_container,
                } );
                var legend = $(e).find('.chart-legend');
                _.each(metric_names, function(metric_name, idx){
                    var color = metric_colors[idx]||metric_color(metric_name);
                    legend.append('<span style="color:'+color+';"><i class="fa fa-circle"></i>&nbsp;'+metric_labels[idx]+'</span>')
                })
                var marker = new VerticalMarker({ graph: chart });
                chart.render();
                marker.render({x:current_metrics['ts']});
                graphs[$(e).data('metric-name')] = {chart:chart, marker:marker};
                
            },
            circularize = function(nodes) {
              var R = 2000, i = 0, L = nodes.length;
              _.each(nodes, function(n){
                  n.x = Math.cos(Math.PI*(i++)/L)*R;
                  n.y = Math.sin(Math.PI*(i++)/L)*R;                      
              })
            },
            toggle_lock = function(event) {
                var mouse_enabled = network_graph.settings('mouseEnabled');
                network_graph.settings('mouseEnabled', !mouse_enabled)
                var touch_enabled = network_graph.settings('touchEnabled');
                network_graph.settings('touchEnabled', !touch_enabled);
                if (mouse_enabled) {
                    network_lock.find('.fa').removeClass('fa-unlock').addClass('fa-lock');                    
                } else {
                    network_lock.find('.fa').removeClass('fa-lock').addClass('fa-unlock');
                }
                analytics.track('control', 'toggle_lock', mouse_enabled);
            },
            toggle_team = function(show){
                show_moderators = show;
                // Update each metrics
                _.each($('.metric'), update_metric);
                // Update the network
                update_network_graph();
                network_graph.refresh();
                analytics.track('filter', 'toggle_team', show_moderators);
            },
            is_isolated = function(node){
                
            },
            node_fill_color = function(node){
                var com = last_metrics.partitions[node.id];
                if (node.isolated) { return node_fill_isolated; }
                return node.team ? node_fill_team : color_scale(com);
            },
            node_border_color = function(node){
              return node.isolated ? node_border_isolated : node_border_default;
            },
            edge_color = function(edge){
                var com = last_metrics.partitions[edge.source];
                return color_scale(com);
            },
            search_node = function(node_id_or_name){
                var re = RegExp("^"+node_id_or_name+"$", 'i');
                return _.find(
                            network_graph.graph.nodes(), 
                            function(n){
                                return n.id === node_id_or_name || n.name.match(re);
                            });                
            },
            expose_node = function(node){
                to_expose = network_graph.graph.neighbors(node.id);              
                to_expose[node.id] = node;
                update_exposed();
                network_graph.refresh();
            },
            search_and_expose = function(node_id_or_name){
                if (node_id_or_name!='') {
                    var node = search_node(node_id_or_name);
                    if (node) {
                        expose_node(node);
                    }                    
                } else {
                    unexpose_node();                    
                }
                
            },
            unexpose_node = function(){
                to_expose = undefined;
                $('#node-marker').hide();
                $('#node-marker').popover('destroy');
                update_exposed();
                network_graph.refresh();
            };

        function db(){
        };

        db.configuration = function(new_configuration){
            if (!arguments.length) return configuration;

            configuration = new_configuration;
            
            return db;
        };
        db.base = function(url){
            if (!arguments.length) return base_url;

            base_url = url;

            return db;
        };
        db.names_map = function(map) {
            if (!arguments.length) return names_map;

            names_map = map;
            
            return db;
        };
        db.load = function(filename){
            if (!arguments.length) return file;

            file = filename;
            
            $.ajax({
              dataType: "json",
              async: false,
              url: base_url+"/"+file, 
              success: preprocess_data
            });

            return db;
        };
        db.show_datapackage = function(do_show){
            if (!arguments.length) return show_datapackage;

            show_datapackage = !!do_show;

            return db;
        };
        db.slider_date_format = function(format){
            if (_.isFunction(format)) {
                slider_date_format = format;
            } else {
                slider_date_format = d3.time.format(format);
            }
            return db;
        };
        db.chart_date_format = function(format){
            if (_.isFunction(format)) {
                chart_date_format = format;
            } else {
                chart_date_format = d3.time.format(format);
            }
            return db;
        };
        db.track_date_format = function(format){
            if (_.isFunction(format)) {
                track_date_format = format;
            } else {
                track_date_format = d3.time.format(format);
            }
        };
        db.analytics = function(analytics_object){
            if (!arguments.length) return analytics;

            analytics = analytics_object;
            
            return db;
        };
        
        db.data = function(){
            return data;
        };
        db.network_graph = function(){
            return network_graph;
        };
        db.current_metrics = function(){
            return current_metrics;
        };
        db.close_node_popover = function(){
            close_node_popover();
        };
        db.search = function(node_id_or_name){
            return search_node(node_id_or_name);
        };
        db.expose = function(node){
            expose_node(node);
        };
        db.search_and_expose = function(node_id_or_name){
            search_and_expose(node_id_or_name);
        };
        db.toggle_team = function(show){
          toggle_team(show);
        };
        
        db.run = function(){
            $('#dashboard-controls').fadeIn();
            
            // Show the title
            var dashboard_name = configuration.get("dashboard_name");
            if (dashboard_name) {
                $('#dashboard-title').html(dashboard_name);
                document.title = dashboard_name+" | dashboard"
            }
                        
            // Show the date when it was generated
            if ( data && data['meta'] && data['meta']['generated']) {
                var format = d3.time.format('%B %d, %Y - %H:%M:%S');
                $("#generated-ts").html(format(data['meta']['generated']));
            }
            // create the metrics crossfilter
            metrics_cf = crossfilter(data['metrics']);
            metrics_bydate = metrics_cf.dimension(function(m) { return m.date; });
            from_date = metrics_bydate.bottom(1)[0].date;
            to_date = metrics_bydate.top(1)[0].date;
            var all_dates = _.map(data['metrics'], function(e){ return slider_date_format(e.date, from_date, to_date); });
            $("#date_range").ionRangeSlider({
                type: "single",
                values: all_dates,
                from: all_dates.length-1,
                hasGrid: true,
                onFinish: function(i){ 
                    update_filter(i.fromNumber); 
                    analytics.track('filter', 'date_range', track_date_format(current_metrics.date, from_date, to_date));
                } //onChange
            });
            update_filter(all_dates.length-1);
            _.each($('.metric'), build_graph);
            _.each($('.multi-metric'), build_multi_graph);
            
            // create the graph crossfilters
            nodes_cf = crossfilter(data['nodes']);
            nodes_bydate = nodes_cf.dimension(function(n) { return n.date; });
            edges_cf = crossfilter(data['edges']);
            edges_bydate = edges_cf.dimension(function(e) { return e.date; });

            // build the network graph
            last_metrics = metrics_bydate.top(1)[0];
            selected_partitions = _.uniq(_.values(last_metrics.partitions)).sort();
            var filter = $('#network-filter');
            
            _.each(selected_partitions, function(part){
                filter
                    .append('<button class="filter-btn btn btn-sm" style="background-color:'+color_scale(part)+'" data-partition="'+part+'"><i class="fa fa-check-square-o"></button>');
            });
            
            $('#filter-button').on('click', function(){
                _.each($('.filter-btn'), function(b){
                    b = $(b);
                    if (_.indexOf(selected_partitions, b.data('partition'))>=0) {
                        b.find('.fa').removeClass('fa-square-o').addClass('fa-check-square-o');
                    } else {
                        b.find('.fa').removeClass('fa-check-square-o').addClass('fa-square-o');                        
                    }
                    b.on('click', toggle_partition);
                })
            })
            
            // Setup datapackage save
            if (show_datapackage) {
                $('#datapackage-save').on('click', function(e){
                    try {
                        window.location = base_url+'../../../datapackage.json';
                    } catch(exc){
                        console.log(exc);
                    }
                    e.preventDefault();                    
                })
                $('#gexf-save').on('click', function(e){
                    try {
                        window.location = base_url+'/network.gexf';
                    } catch(exc){
                        console.log(exc);
                    }
                    e.preventDefault();                    
                })
                
            } else {
                $('#datapackage').html('');
            }
            
            $('#search-button').on('click', function(e){
                $('.user-search').find('input').val(current_user_filter);
                _.each($('.user-search-btn'), function(b){
                    $(b).on('click', function(e){
                        current_user_filter = $(this).closest('.user-search').find('input').val();
                        search_and_expose(current_user_filter);
                        e.preventDefault();
                    });
                })
                _.each($('.user-search-clear-btn'), function(b){
                    $(b).on('click', function(e){
                        unexpose_node();
                        e.preventDefault();
                    });
                })
            })

            nodes_map = {}
            _.each(data['nodes'], function(node){
                nodes_map[node.id] = node;
            });
            
            var initial_graph = filtered_graph();
            var isolated_nodes = _.where(initial_graph['nodes'], {isolated: true});
            initial_graph['nodes'] = _.reject(initial_graph['nodes'], function(n){ return n.isolated });
            
            circularize(_.sortBy(initial_graph['nodes'], function(node){ return last_metrics.partitions[node.id]; }));
            network_graph = new sigma({
              graph: initial_graph,
              renderer: {
                  container: document.getElementById('network'),
                  type: 'canvas'
                }
            });
            network_graph.settings({
                sideMargin: 8,
                defaultLabelSize: 12,
                labelThreshold: 30,
                maxNodeSize: 3,
                defaultEdgeType:'curve',
                mouseEnabled: false,
                touchEnabled: false,
                doubleClickEnabled: false,
                labelHoverShadow: false
            })
            network_graph.bind('doubleClickNode', function(e) {
                expose_node(e.data.node);
            });
            network_graph.bind('doubleClickStage', function(e) {
                unexpose_node();
            });
            network_graph.bind('clickNode', function(e) {
                var offset = $(this).offset();
                var left = e.data.node['renderer1:x'];
                var top = e.data.node['renderer1:y'];
                $('#node-marker').popover('destroy');
                $('#node-marker').show();
                $('#node-marker').css('left', (left) + 'px');
                $('#node-marker').css('top', (top) + 'px');                

                $('#node-marker').popover({
                    container: 'body',
                    html: true,
                    placement: 'auto right',
                    content: node_popover_content(e.data.node)
                });
                $('#node-marker').popover('show');
            });
            network_graph.bind('clickStage', close_node_popover);
            
            network_graph.refresh();
            $('#network').hide();
            network_graph.startForceAtlas2({
                linLogMode: false,
                outboundAttractionDistribution: false,
                adjustSize: false,
                adjustSizes: false,
                edgeWeightInfluence: 0,
                scalingRatio: 9000,
                strongGravityMode: false,
                gravity: 2000,
                slowDown: 1
              });
              setTimeout(function(){ 
                  network_graph.stopForceAtlas2();
                  // saving the computed positions
                  _.each(network_graph.graph.nodes(), function(n){
                      var node = nodes_map[n.id];
                      if (node) {
                          node.x = n.x;
                          node.y = n.y;
                      }
                  })
                  // re-add the isolated nodes 
                  // we put them on the bottom side evenly distributed
                  if (isolated_nodes) {
                      // Find the max and min x & y of the nodes
                      var max_x = _.max(network_graph.graph.nodes(), function(n){ return n.x; }).x;
                      var max_y = _.max(network_graph.graph.nodes(), function(n){ return n.y; }).y;
                      var min_x = _.min(network_graph.graph.nodes(), function(n){ return n.x; }).x;
                      var min_y = _.min(network_graph.graph.nodes(), function(n){ return n.y; }).y;
                      var origin_x = Math.floor(min_x);
                      var origin_y = Math.floor(max_y*1.03);
                      var step = Math.floor(Math.abs(max_x-min_x)/isolated_nodes.length+2);
                      var index = 1
                      _.each(isolated_nodes, function(n){
                          var node = nodes_map[n.id];
                          if (node) {
                              node.x = n.x = Math.floor(origin_x+(index*step)); 
                              node.y = n.y = origin_y; 
                              network_graph.graph.addNode(n);
                              index += 1;
                          }                          
                      });
                      network_graph.refresh();
                  }
                  $('#network-container .box-tools').show();
              }, 10000);
              $('#network').fadeIn();
            
            // setup network controls
            network_lock = $('#network-lock');
            network_lock.click(toggle_lock);
            
            $('#moderators-check').on('ifChanged', function(e){ toggle_team($(this).prop('checked')); });
            window.network_lock = network_lock;
            
            return db;
        };

        return db;
    };
    
});
