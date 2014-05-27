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
    
    sigma.classes.graph.addMethod('neighbors', function(nodeId) {
      var k,
          neighbors = {},
          index = this.allNeighborsIndex[nodeId] || {};

      for (k in index)
        neighbors[k] = this.nodesIndex[k];

      return neighbors;
    });
    
    sigma.utils.pkg('sigma.canvas.nodes');
    sigma.canvas.nodes.border = (function() {
      var _cache = {},
          _loading = {},
          _callbacks = {};

      // Return the renderer itself:
      var renderer = function(node, context, settings) {
        var args = arguments,
            prefix = settings('prefix') || '',
            size = node[prefix + 'size'],
            color = node.color || settings('defaultNodeColor'),
            border_color = node.border_color || settings('defaultNodeColor');

        // Draw the border:
        context.fillStyle = color;
        context.beginPath();
        context.arc(
          node[prefix + 'x'],
          node[prefix + 'y'],
          node[prefix + 'size'],
          0,
          Math.PI * 2,
          true
        );

        context.closePath();
        context.lineWidth = size / 8;
        context.strokeStyle = border_color;
        context.fill();        
        context.stroke();
      };
      return renderer;
    })();

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
    
    var Help = function(){

        var base_url = '/json',
            file = 'help.json',
            lang = 'en',
            data = undefined,
            helped = undefined,
            popovers = [],
            make_popover = function(element, key, placement){
              $(element).popover({
                  placement: placement||'auto',
                  content: data[lang][key],
                  trigger: 'manual'
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
                      $(element).popover('toggle')
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
    
    var Dashboard = function(){

        var base_url = undefined,
            file = undefined,
            data = undefined,
            date_format = d3.time.format('%B %d, %Y'),
            scale = d3.scale.category20(),
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
            // spinner = new Spinner({ radius: 50, color:'#ffffff' }).spin(document.getElementById('network-container')),
            node_fill_transparent = 'rgba(204,204,204,0.1)',
            edge_transparent = 'rgba(204,204,204,0.1)',
            node_border_default = 'rgba(240, 240, 240, 1)', //'rgba(32, 32, 32, 1)',
            node_border_transparent = 'rgba(240, 240, 240, 0.1)',
            selected_partitions = [],  
            show_moderators = true,  
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
                if (_.indexOf(selected_partitions, b.data('partition'))>=0) {
                    selected_partitions = _.without(selected_partitions, b.data('partition')) 
                    b.find('.fa').removeClass('fa-check-square-o').addClass('fa-square-o');                        
                } else {
                    selected_partitions.push(b.data('partition'))
                    b.find('.fa').removeClass('fa-square-o').addClass('fa-check-square-o');
                }
                update_network_graph();
            },
            update_network_graph = function(){
                network_graph.graph.clear();
                network_graph.graph.read(filtered_graph());
                update_hidden();
                update_exposed();
                network_graph.refresh();
            },
            update_hidden = function(){
                _.each(network_graph.graph.nodes(), function(n){ 
                    var to_hide = _.indexOf(selected_partitions, last_metrics.partitions[n.id])<0;
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
                      n.color = node_color(n);
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
            node_popover_content = function(node){
                var current_metrics = metrics_bydate.top(1)[0];
                var in_degree = current_metrics[metric_name_prefixed('in_degree')][node.id];
                var out_degree = current_metrics[metric_name_prefixed('out_degree')][node.id];
                var betweenness = current_metrics[metric_name_prefixed('betweenness')][node.id];
                var cont_div = $('<div class="node-hover-content"><div class="node-hover-title"></div><ul class="node-hover-data"></ul></div>');
                cont_div.children('.node-hover-title').html(node.name);
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
                      color: node_color(node),
                      type: 'border',
                      border_color: node_border_default,
                      team: node.team,
                      ts: node.created_ts,
                      date: node.date
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
                var metric_name = metric_name_prefixed($(e).data('metric-name'));
                var minichart = $(e).find('.minichart')[0];
                var complete_metric = global_metric_series(metric_name);
                var max_metric_value = _.max(complete_metric, function(e){ return e.y!=undefined ? e.y : 0; } ).y;
                var min_metric_value = _.min(complete_metric, function(e){ return e.y!=undefined ? e.y : max_metric_value; } ).y;
                var chart = new Rickshaw.Graph( {
                    element: minichart, 
                    renderer: 'multi',
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
        			formatter: function(d) { return d3.time.format(' %e/%m')(d); }
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
              var R = 900, i = 0, L = nodes.length;
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
                    network_lock.tooltip('hide').attr('data-original-title', "Unlock").tooltip('fixTitle').tooltip('show');
                } else {
                    network_lock.find('.fa').removeClass('fa-lock').addClass('fa-unlock');
                    network_lock.tooltip('hide').attr('data-original-title', "Lock").tooltip('fixTitle').tooltip('show');
                }
            },
            toggle_team = function(e){
                show_moderators = $(this).prop('checked');
                // Update each metrics
                _.each($('.metric'), update_metric);
                // Update the network
                update_network_graph();
                network_graph.refresh();
            },
            node_color = function(node){
                var com = last_metrics.partitions[node.id];
                return node.team ? '#606060' : scale(com);
            },
            edge_color = function(edge){
                var com = last_metrics.partitions[edge.source];
                return scale(com);
            };

        function db(){
        };


        db.base = function(url){
            if (!arguments.length) return base_url;

            base_url = url;

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
        
        db.data = function(){
            return data;
        };

        db.network_graph = function(){
            return network_graph;
        };

        db.run = function(){
            // Load the data
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
            var all_dates = _.map(data['metrics'], function(e){ return date_format(e.date); });
            $("#date_range").ionRangeSlider({
                type: "single",
                values: all_dates,
                from: all_dates.length-1,
                hasGrid: true,
                onFinish: function(i){ update_filter(i.fromNumber); } //onChange
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
                    .append('<button class="filter-btn btn btn-sm" style="background-color:'+scale(part)+'" data-partition="'+part+'"><i class="fa fa-check-square-o"></button>');
            });
            
            $('#fa-filter-btn').on('click', function(){
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
            nodes_map = {}
            _.each(data['nodes'], function(node){
                nodes_map[node.id] = node;
            });
 
            circularize(_.sortBy(data['nodes'], function(node){ return last_metrics.partitions[node.id]; }));
            network_graph = new sigma({
              graph: filtered_graph(),
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
                labelHoverShadow: false
            })
            network_graph.bind('clickNode', function(e) {
                  to_expose = network_graph.graph.neighbors(e.data.node.id);              
                  to_expose[e.data.node.id] = e.data.node;
                  console.log(e);
                  update_exposed();
                  network_graph.refresh();
            });

            network_graph.bind('clickStage', function(e) {
                to_expose = undefined;
                update_exposed();
                network_graph.refresh();
            });
            network_graph.bind('overNode', function(e) {
                var offset = $(this).offset();
                var left = e.data.node['renderer1:x'];
                var top = e.data.node['renderer1:y'];
                $('#node-marker').show();
                $('#node-marker').css('left', (left) + 'px');
                $('#node-marker').css('top', (top) + 'px');                
 
                $('#node-marker').popover({
                    container: '#network-container',
                    html: true,
                    placement: 'auto right',
                    content: node_popover_content(e.data.node)
                });
                $('#node-marker').popover('show');
            });
            network_graph.bind('outNode', function(e) {
                $('#node-marker').hide();
                $('#node-marker').popover('destroy');
            });
            
            network_graph.refresh();
            $('#network').hide();
            network_graph.startForceAtlas2({
                autoSettings: false,
                linLogMode: true,
                outboundAttractionDistribution: false,
                adjustSizes: true,
                edgeWeightInfluence: 0,
                scalingRatio: 0.2,
                strongGravityMode: false,
                gravity: -0.5,
                jitterTolerance: 2,
                barnesHutOptimize: false,
                barnesHutTheta: 1.2,
                speed: 2,
                outboundAttCompensation: -1.5,
                totalSwinging: 0,
                totalEffectiveTraction: 0,
                complexIntervals: 500,
                simpleIntervals: 1000
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
                  // stop the spinner and show the network
                  // spinner.stop();
                  // $('#network').fadeIn();
                  $('#network-container .box-tools').show();
              }, 8000)
              // spinner.stop();
              $('#network').fadeIn();
              // $('#network-container .box-tools').show();
            
            // setup network controls
            network_lock = $('#network-lock');
            network_lock.click(toggle_lock);
            
            $('#moderators-check').on('ifChanged', toggle_team);
            window.network_lock = network_lock;
            return db;
        };

        return db;
    };
    
    // The script produces an index json with the last date when it was run
    $.ajax({
      dataType: "json",
      async: false,
      url: "/json/last.json", 
      success: function( d ) {
          window.Dashboard = Dashboard()
                              .base('/json/data/'+d.last)
                              .load('network.min.json');
    
          window.Dashboard.run();
          
          Help().load();
      }
    });

    

});


// TODO: add network png save
// var image = canvas.toDataURL("image/png").replace("image/png", "image/octet-stream"); 
// $('.save').attr({
// 'download': 'image.png',  /// set filename
// 'href'    : image              /// set data-uri
//  });