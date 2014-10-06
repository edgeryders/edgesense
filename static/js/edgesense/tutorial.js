jQuery(function($) {
    "use strict";
    
    /*
     * Simple linear regression to find the m in:
     * y = x * m + b
     * if m > 0 the series of values is increasing
     * if m < 0 the series is decreasing
     */
    var find_slope = function(values_y) {
        var sum_x = 0;
        var sum_y = 0;
        var sum_xy = 0;
        var sum_xx = 0;
        var count = values_y.length;

        /*
         * Calculate the sum for each of the parts necessary.
         */
        for (var x = 0; x < values_y.length; x++) {
            var y = values_y[x];
            sum_x += x;
            sum_y += y;
            sum_xx += x*x;
            sum_xy += x*y;
        }

        var m = (count*sum_xy - sum_x*sum_y) / (count*sum_xx - sum_x*sum_x);

        return m;
    }
    
    var guid = (function() {
      function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
                   .toString(16)
                   .substring(1);
      }
      return function() {
        return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
               s4() + '-' + s4() + s4() + s4();
      };
    })();
    
    var tutorial = function(){
        
        var steps = [],
            dashboard = undefined,
            open_btn = undefined,
            close_btn = undefined,
            main_cnt = undefined,
            title_cnt = undefined,
            header_cnt = undefined,
            tutorial_cnt = undefined,
            run_id = undefined,
            base_data = function(){
                var url = window.location.protocol +
                           '//' + window.location.hostname +
                           window.location.pathname +
                           window.location.search;
                
                return {
                    'dashboard': dashboard.configuration().get("dashboard_name"), 
                    'host': url,
                    'base': dashboard.base(),
                    'run_id': run_id
                };
            },
            repad = function(){
                // main_cnt.css('padding-top', header_cnt.outerHeight()+4);
            },
            slide_in = function(e){
                tutorial_cnt.slideDown(500, function(){
                    open_btn.closest('li').hide();
                    repad();
                });
                e.preventDefault();                
            },
            slide_out = function(e){
                tutorial_cnt.slideUp(500, function(){
                    open_btn.closest('li').show();            
                    repad();
                });
                e.preventDefault();
                
            },
            setup_closing_step = function(step){
                step.on('shown.bs.tab', function (e) {
                    post_results();
                });
                
                // Setup feedback form
                var form_group = $('<div>').addClass('form-group');
                var textarea = $('<textarea>').attr('name', 'comments').addClass('form-control');
                form_group.append(textarea);                 
                step.find('.tut-result').append(form_group);
                
                add_step_button(step.find('.tut-control'), "Submit feedback", undefined, function(button){
                    var feedback = base_data();
                    feedback.comments = $(textarea).val();
                    upload(feedback);
                    step.find('.tut-result').html('<div class="alert alert-info"><i class="fa fa-info"></i>Thank you!</div>');
                    $(button).hide();
                });
                add_step_button(step.find('.tut-control'), "Restart", 1, restart);
                
            },
            setup_step = function(step, number){
                step.attr('id', 'tut-step-'+number).
                     data('target', '#tut-step-'+number).
                     data('toggle', 'tab').
                     append('<div class="col-lg-12"><div class="tut-result"></div><div class="tut-control pull-right"></div></div>');
                
                _.each(step.find('.tut-help'), function(help){
                    $(help).
                        html('<p class="callout callout-warning">'+$(help).html()+'</p>');
                        // html('<p class="text-muted"><i class="fa fa-info"></i>: '+$(help).html()+'</p>');
                        // html('<div class="alert alert-info"><i class="fa fa-info"></i>'+$(help).html()+'</div>');
                });
                
                // setup the answer via the callback (if present) or using the generic survey callback
                var step_number = step.data('tut-step');
                if (_.isFunction(answers_setup['step_'+step_number])) {
                   answers_setup['step_'+step_number](step); 
                }
                
            },
            add_step_button = function(where, label, goto_step_number, callback){
                var button = $('<a>').
                                text(label).
                                addClass('btn btn-default btn-sm').
                                data('target', '#tut-step-'+goto_step_number).
                                data('toggle', 'tab').
                                on('click', function(e){ 
                                    if (_.isFunction(callback)){
                                        callback(this);
                                    }
                                    if (goto_step_number) {                                        
                                        show_step(goto_step_number);
                                    }
                                    e.preventDefault();
                                })
                where.append(button).append('&nbsp;');
            },
            show_step = function(step_number){
                var step = $('#tut-step-'+step_number);
                step.tab('show');
                title_cnt.html(step.data('tut-title'));
                repad();
            },
            surveys = [],
            record_survey = function(step, option){
                var survey_key = $(step).data('survey');
                
                $(step).find('input[name='+survey_key+']').iCheck('disable');
                surveys.push({step: survey_key, value: option.val() });
 
                // goto next step (add button to do so)
                var next = step.data('tut-step-next');
                add_step_button($(step).find('.tut-control'), "Next", next);
                
                update_end_results();
                
                repad();               
                
            },
            answers_setup = function(){},
            answers = [],
            show_answer = function(step, success, message, callback){
                $(step).
                    find('.tut-result').
                    html('<div class="alert alert-'+(success ? "success" : "warning" )+'"><i class="fa fa-'+(success ? "check" : "warning")+'"></i>'+message+'</div>');

                // goto next step (add button to do so)
                var next = step.data('tut-step-next');
                add_step_button($(step).find('.tut-control'), "Next", next, callback);
                
                update_end_results();
                
                repad();               
            },
            // setup the step verifiers (functions called to check the step answer);
            betweenness_bin_respond = false,
            betweenness_bin = function(step, node){
                if (!betweenness_bin_respond) {
                    return;
                }
                // what percentile of the betweenness does the current node
                var betweenness = _.values(Edgesense.current.current_metrics()['full:betweenness']);
                var node_betweenness = Edgesense.current.current_metrics()['full:betweenness'][node.id];
                var counts = _.countBy(betweenness, function(n){ return (n >= node_betweenness ? 'greater' : 'smaller') });
                var percent = Math.round((counts.greater/betweenness.length)*100); // how many % are bigger than this?
                
                var success = false;
                var percent_message = undefined;
                if(percent>50) {
                    percent_message ='50% least central';
                } else if (percent>25 && percent<=50) {
                    percent_message ='50% most central';
                } else if (percent>10 && percent<=25) {
                    percent_message ='25% most central';
                    success = true;
                } else if (percent>5 && percent<=10) {
                    percent_message ='10% most central';
                    success = true;                    
                } else if (percent>1 && percent<=5) {
                    percent_message ='5% most central';
                    success = true;                    
                } else if (percent<=1) {
                    percent_message ='1% most central';
                    success = true;                    
                }

                answers.push({step: 'betweenness_bin', success: success, value: percent });

                $('#node-marker').hide();
                $('#node-marker').popover('destroy');
                
                var message = "You have selected "+node.name+". It is one of the "+percent_message+" nodes of this network. Try again?";
                
                show_answer(step, success, message, function(){ betweenness_bin_respond = false; });
                
            },
            relationship_percentage = function(step, option){
                // what % of the links are from the moderators? the metric is edges_count
                // 1. disable
                $(step).find('input[name=tut-step-2-answers]').iCheck('disable');
                // 2. find the right answer
                var total_edges = dashboard.current_metrics()['full:edges_count'];
                var user_edges = dashboard.current_metrics()['user:edges_count'];
                var answer = (total_edges-user_edges)/total_edges;
                var success = false;
                switch (option.val()) {
                    case 'lt-20':
                        success = answer<0.2;
                        break;
                    case '20-40':
                        success = (answer>=0.2 && answer<0.4);
                        break;
                    case '40-60':
                        success = (answer>=0.4 && answer<0.6);
                        break;
                    case '60-80':
                        success = (answer>=0.6 && answer<0.8);
                        break;
                    case 'gt-80':
                        success = answer>=0.8;
                        break;
                }
                
                answers.push({step: 'relationship_percentage', success: success, value: option.val(), correct: answer });
                
                // 3. show answer
                var message = (success ? "Well done! " : "")+"Moderators in this network account for "+d3.round(answer*100)+"% of all relationships.";
                show_answer(step, success, message);
            },
            posts_percentage = function(step, option){
                // what % of the posts are from the moderators? the metric is user:ts_posts_share
                // 1. disable
                $(step).find('input[name=tut-step-3-answers]').iCheck('disable');
                // 2. find the right answer
                var answer = dashboard.current_metrics()['user:ts_posts_share'];
                var success = false;
                switch (option.val()) {
                    case 'lt-20':
                        success = answer<0.2;
                        break;
                    case '20-40':
                        success = (answer>=0.2 && answer<0.4);
                        break;
                    case '40-60':
                        success = (answer>=0.4 && answer<0.6);
                        break;
                    case '60-80':
                        success = (answer>=0.6 && answer<0.8);
                        break;
                    case 'gt-80':
                        success = answer>=0.8;
                        break;
                }
                
                answers.push({step: 'posts_percentage', success: success, value: option.val(), correct: answer });
                
                // 3. show answer
                var message = (success ? "Well done! " : "")+"Your non-moderator community members have contributed "+d3.round(answer*100)+"% of all posts."
                show_answer(step, success, message);
            },
            comments_share = function(step, option){
                // Do the comment share of community content rise? the metric is user:ts_comments_share
                // 1. disable
                $(step).find('input[name=tut-step-4-answers]').iCheck('disable');
                // 2. find the right answer
                var metrics_cf = crossfilter(dashboard.data()['metrics']);
                var metrics_bydate = metrics_cf.dimension(function(m) { return m.date; });
                var last_metrics = _.map(metrics_bydate.top(5), function(m){ return m['user:ts_comments_share'];});
                var slope = find_slope(last_metrics.reverse());
                var success = false;
                var message = '';
                var messages = [
                    "Well done! The share of comments written by non-moderators has increased. This means that the conversation has become more self-sustaining lately. Good work!",
                    "Well done! The share of comments written by non-moderators has decreased. This means that the conversation has become less self-sustaining lately. Is it a random fluctuation or a trend? Do you have a plan to fix it?",
                    "The share of comments written by non-moderators has indeed increased. And yes, that indicates that the conversation might have become more self-sustaining, less dependant on moderators. Good work!",
                    "The share of comments written by non-moderators has indeed decreased. However, if anything this means that the conversation might have become less self-sustaining lately, not more. Is it a random fluctuation or a trend? Do you have a plan to fix it?"
                    ];
                switch (option.val()) {
                    case 'incr-more':
                        if (slope>0) {
                            message = messages[0];
                            success = true;
                        } else {
                            message = messages[2];
                            success = false;                            
                        }
                        break;
                    case 'decr-more':
                        if (slope>0) {
                            message = messages[2];
                            success = false;
                        } else {
                            message = messages[3];
                            success = false;                            
                        }
                        break;
                    case 'incr-less':
                        if (slope>0) {
                            message = messages[2];
                            success = false;
                        } else {
                            message = messages[3];
                            success = false;                            
                        }
                        break;
                    case 'decr-less':
                        if (slope>0) {
                            message = messages[2];
                            success = false;
                        } else {
                            message = messages[1];
                            success = true;                            
                        }
                        break;
                }
                
                answers.push({step: 'comments_share', success: success, value: option.val(), correct: slope });
                
                // 3. show answer
                show_answer(step, success, message);
            },
            modularity_increase = function(step, option){
                // Do the moderators increase or decrease modularity? the metric is louvain_modularity
                // 1. disable
                $(step).find('input[name=tut-step-5-answers]').iCheck('disable');
                // 2. find the right answer
                var total_modularity = dashboard.current_metrics()['full:louvain_modularity'];
                var user_modularity = dashboard.current_metrics()['user:louvain_modularity'];
                var modularity_increased_by_moderators = (total_modularity>user_modularity)
                var success = false;
                var message = '';
                
                if (modularity_increased_by_moderators) {
                    message = "Your moderators do indeed increase modularity. This may indeed signal that they are talking mostly to each other, or to a small group of people in the community";
                } else {
                    message = "Your moderators do indeed decrease modularity. This may happen because moderators try to engage many or most new users, and so they end up acting as hubs, pulling the whole network together.";
                }
                    
                switch (option.val()) {
                    case 'incr-team':
                        if (modularity_increased_by_moderators) {
                            message = "Well done! "+message;
                            success = true;
                        }
                        break;
                    case 'incr-other':
                        break;
                    case 'decr-team':
                        break;
                    case 'decr-other':
                        if (!modularity_increased_by_moderators) {
                            message = "Well done! "+message;
                            success = true;
                        }
                        break;
                }
                answers.push({step: 'modularity_increase', success: success, value: option.val(), correct: modularity_increased_by_moderators });
                
                // 3. show answer
                show_answer(step, success, message);
            },
            update_end_results = function(){
                var correct_answers = _.filter(answers, function(r){ return r.success; }).length;
                $('.tut-end-result').html(correct_answers);
            },
            restart = function(){
                run_id = guid();
                answers = [];
                surveys = [];
                betweenness_bin_respond = false;
                $('.tut-step input[type=radio]').iCheck('enable').iCheck('uncheck');
                $('.tut-control').html('');
                $('.tut-end-result').html('-');
            },
            upload = function(what){
                var tutorial_upload = dashboard.configuration().get("tutorial_upload");
                if (_.isUndefined(tutorial_upload)) {
                    return;
                }
                                                
                $.ajax({
                    type: 'POST',
                    url: tutorial_upload,
                    crossDomain: true,
                    data: { result: JSON.stringify(what)}
                });
                
            },
            post_results = function(){
                var result = base_data();
                result.answers= answers;
                result.surveys= surveys;
                upload(result);
            };
            
        // add the step answer setup code
        answers_setup.step_1 = function(step){
            step.on('shown.bs.tab', function (e) {
                dashboard.close_node_popover();
                betweenness_bin_respond = true;
            })
            
            // setup the dashboard node callback
            dashboard.network_graph().bind('clickNode', function(e){ 
                betweenness_bin(step, e.data.node);
            });
        }

        answers_setup.step_2 = function(step){
            $(step).find('input[name=tut-step-2-answers]').on('ifChecked', function(event){
                relationship_percentage(step, $(this));
            });
        }

        answers_setup.step_3 = function(step){
            $(step).find('input[name=tut-step-3-answers]').on('ifChecked', function(event){
                posts_percentage(step, $(this));
            });
        }
        
        answers_setup.step_4 = function(step){
            $(step).find('input[name=tut-step-4-answers]').on('ifChecked', function(event){
                comments_share(step, $(this));
            });
        }

        answers_setup.step_5 = function(step){
            $(step).find('input[name=tut-step-5-answers]').on('ifChecked', function(event){
                modularity_increase(step, $(this));
            });
        }

        answers_setup.step_survey = function(step){
            // Add the radiobuttons
            var survey_key = $(step).data('survey');
            var survey_results = _.compact(($(step).data('survey-result')||"very useful|somewhat useful|useless").split("|"));
            
            if (survey_results.length>0 && survey_key) {
                var form_group = $('<div>').addClass('form-group');
                _.each(survey_results, function(result){
                    var radio_cnt = $('<div>').addClass('radio');
                    var radio = '<label><input type="radio" name="'+survey_key+'" value="'+result+'">&nbsp;'+result+'</label>';
                    radio_cnt.html(radio);
                    form_group.append(radio_cnt);
                    
                })
                $(step).find('.tut-text').append(form_group);
                
                $(step).find('input[name='+survey_key+']')
                        .iCheck({radioClass: 'iradio_minimal'})
                        .on('ifChecked', function(event){
                            record_survey(step, $(this));
                        });               
            }
        }
        
        
        function t(){
        };
        
        t.post_results = function(){
            post_results();
        }
        
        t.dashboard = function(db){
            if (!arguments.length) return dashboard;

            dashboard = db;

            return t;
        }
        
        t.setup = function(){
            run_id = guid();
            open_btn = $('#tutorial-open');
            close_btn = $('#tutorial-close');
            main_cnt = $('#main-block');
            header_cnt = $('.content-header');
            tutorial_cnt = $('#tutorial');
            
            open_btn.on('click', slide_in);
            close_btn.on('click', slide_out);

            // load all the steps from the page
            steps = _.map($('.tut-step'), function(s){ return $(s) });
            var index = 0;
            _.each(steps, function(step){
                setup_step(step, index);
                index += 1;
            });
            
            // add back/next buttons
            var first_step = _.first(steps);
            add_step_button(first_step.find('.tut-control'), "Start", 1);
            first_step.data('tut-step-next', 1);
            
            var middle_steps = _.initial(_.rest(steps));
            var index = 1;
            _.each(middle_steps, function(s){
                // var step_number = s.data('tut-step');
                s.data('tut-step-prev', index-1);
                s.data('tut-step-next', index+1);
                index+=1;
            });

            var last_step = _.last(steps);
            setup_closing_step(last_step);
            
            // setup title
            title_cnt = $('<span>')
            $('#tutorial .box-title').append(' - ').append(title_cnt);
            title_cnt.html(first_step.data('tut-title'));
            return t;
        }
        
        return t;
    };
    Edgesense.Tutorial = tutorial();
        
});

