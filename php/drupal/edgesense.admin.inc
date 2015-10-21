<?php

/**
 * @file
 * Admin settings and config pages for edgesense.
 */

/**
 * Page callback: home of the admin
 */
function edgesense_admin_home_form($form, &$form_state) {

  $text = '';
  $text .= '<h3>Configuration for the Edgesense Social Network Analysis dashboard</h3>';
  $text .= '<p>The current Edgesense SNA tool is made up of two components:</p>';
  $text .= '<h5>A data processing script</h5>';
  $text .= '<p>This is used to build the network from the source json files and to compute all the metrics. See: <a href="https://github.com/Wikitalia/edgesense/blob/master/python/README.md" target="_blank">https://github.com/Wikitalia/edgesense/blob/master/python/README.md</a> for informations on how to install it.</p>';
  $text .= '<h5>This drupal module</h5>';
  $text .= '<p>It includes a dashboard that reads the output produced by the processing scripte and builds the visualization of the network and the metrics.</p>';
  $text .= '<h3>Configuring the script and dashboard</h3>';
  $text .= '<p>From these pages you can configure the Edgesense social network analytics dashboard for your Drupal community.</p>';
  $text .= '<p>The different pages allow you to setup different aspects of the module:</p>';
  $text .= '<p>';
  $text .= '<ol>';
  $text .= '<li>'.t('<a href="@url"><b>Script Configuration</b></a>', array('@url' => url('admin/edgesense/script-param'))).': this page allows you to change the parameters used by the processing script to extract data (you can even set the script to automatically run once a day.)</li>';
  $text .= '<li>'.t('<a href="@url"><b>Script Execution</b></a>', array('@url' => url('admin/edgesense/script-run'))).': from this page you can see when the script was last executed, how to run it manually and see the log from the last run.</li>';
  $text .= '<li>'.t('<a href="@url"><b>Dashboard configuration</b></a>', array('@url' => url('admin/edgesense/config'))).': here you can change the title of the dashboard, configure a Google anaytics ID and more.</li>';
  $text .= '<li>'.t('<a href="@url"><b>Inline Help Configuration</b></a>', array('@url' => url('admin/edgesense/help'))).': this page lets you update the dashboard inline help.</li>';
  $text .= '<li>'.t('<a href="@url"><b>Open Dashboard</b></a>', array('@url' => url('admin/edgesense/dashboard'))).': this is a link to the live dashboard.</li>';
  $text .= '</ol>';
  $text .= '</p>';
  $text .= '<hr>';
  
  if (!file_exists('public://edgesense/json/last.json')) {
    $text .= '<p>The Edgsense Python script has not run yet. Please follow </p> ';
    $text .= t('<a href="@url">the instructions</a> for running it.', array('@url' => url('admin/edgesense/script-run')));
    $text .= '<hr>';
  }
  else {
      $text .= '<br><p>' . t('<a class="button" href="@url">Click here to open the dashboard</a>', array('@url' => url('admin/edgesense/dashboard'))) . '</p>';      
  }

  
  $form['form_intro'] = array(
    '#markup' => $text,
  );

  return $form;
}

/**
 * Page callback: directory settings form to export json file.
 */
function edgesense_admin_config_form($form, &$form_state) {

  $form['edgesense_config_uri'] = array(
    '#type' => 'textfield',
    '#title' => t('Config file name with uri'),
    '#size' => 60,
    '#default_value' => variable_get('edgesense_config_uri', 'public://edgesense/json/configuration.json'),
  );

  $form['edgesense_help_uri'] = array(
    '#type' => 'textfield',
    '#title' => t('Config file name with uri'),
    '#size' => 60,
    '#default_value' => variable_get('edgesense_help_uri', 'public://edgesense/json/help.json'),
  );

  $form['edgesense_param_uri'] = array(
    '#type' => 'textfield',
    '#title' => t('Config file name with uri'),
    '#size' => 60,
    '#default_value' => variable_get('edgesense_param_uri', 'private://edgesense/script/run.json'),
  );

  return $form;
}

/**
 * Page callback: settings form to export config vars json file.
 */
function edgesense_admin_param_form($form, &$form_state) {

  edgesense_display_not_run_message();
  $file = variable_get('edgesense_config_uri', 'public://edgesense/json/configuration.json');
  $config_file = file_exists($file) ? drupal_realpath($file) : NULL;
  $config_data = !empty($config_file) ? drupal_json_decode(file_get_contents($config_file, FALSE, NULL)) : NULL;

  $form['form_intro'] = array(
    '#markup' => '
        <p>There are a few parameters that permit the configuration of the dashboad page. One of the first things the page does on load is to read the parameters from a configuration.json file in the [drupal root]/sites/default/files/edgesense/json/ directory, so to customize them one just needs to create the file.</p>
    ',
  );

  $form['dashboard_name'] = array(
    '#type' => 'textfield',
    '#title' => t('Dashboard Name'),
    '#required' => TRUE,
    '#default_value' => !empty($config_data['dashboard_name']) ? $config_data['dashboard_name'] : NULL,
    '#description' => t('The name that will appear in the title of the Edgesense dashboard'),
  );

  $form['analytics_tracking_id'] = array(
    '#type' => 'textfield',
    '#title' => t('Analytics Tracking ID'),
    '#required' => FALSE,
    '#default_value' => !empty($config_data['analytics_tracking_id']) ? $config_data['analytics_tracking_id'] : NULL,
    '#description' => t('Your google analytics ID, will allow you to collect also tracking events from the dashboard in your google analytics'),
  );

  $form['base_data_url'] = array(
    '#type' => 'textfield',
    '#title' => t('Base Data Path'),
    '#required' => FALSE,
    '#default_value' => !empty($config_data['base_data_url']) ? $config_data['base_data_url'] : NULL,
    '#description' => t('This optional parameter should be set to the absolute URL where the page can access the data saved by the python script. If it is empty it will be the ' . file_create_url('public://edgesense/json/data') . ' URL. You can use this to separate the serving of the dashboard from the processing of the files (e.g. have the dashboard live at /edgesense and the data live at /data. N.B. it is possible to have the processed data needs to reside on a different server but you\'ll have to proxy the json files from the same server as the dashboard.'),
  );

  $form['tutorial_upload'] = array(
    '#type' => 'textfield',
    '#title' => t('Tutorial Upload URL'),
    '#required' => FALSE,
    '#default_value' => !empty($config_data['tutorial_upload']) ? $config_data['tutorial_upload'] : url('edgesense/tutorial_upload'),
    '#description' => t('This should be set to a URL which can receive the POSTs from the tutorial with the results to be saved. If left empty the edgesense module upload URL will be used and the files will be saved locally in the '),
  );

  $form['submit'] = array(
    '#type' => 'submit',
    '#value' => t('Save'),
  );

  return $form;
}

/**
 * Validation for the variable settings form.
 */
function edgesense_admin_param_form_validate($form, &$form_state) {
  unset($form_state['values']['form_id'], $form_state['values']['form_token'],
    $form_state['values']['form_build_id'], $form_state['values']['op'], $form_state['values']['submit']
  );

  if ($form_state['values']['tutorial_upload'] && valid_url($form_state['values']['tutorial_upload'], TRUE) == FALSE) {
    form_set_error('tutorial_upload', t('Please enter valid url'));
  }
}

/**
 * Validation for the variable settings form.
 */
function edgesense_admin_param_form_submit($form, &$form_state) {
  $file = NULL;
  if (!empty($form_state['values'])) {
    $data = drupal_json_encode($form_state['values']);
    $destination = variable_get('edgesense_config_uri', 'public://edgesense/json/configuration.json');
    $file = file_unmanaged_save_data($data, $destination, FILE_EXISTS_REPLACE);
  }

  if ($file) {
    drupal_set_message(t('Configuration successfully generated.'), 'status');
  }
  else {
    drupal_set_message(t("Couldn't generate json file."), 'error');
  }
}

/**
 * Page callback: settings form to export help vars to json file.
 */
function edgesense_admin_help_form($form, &$form_state) {

  edgesense_display_not_run_message();
  $file = variable_get('edgesense_help_uri', 'public://edgesense/json/help.json');
  $config_file = file_exists($file) ? drupal_realpath($file) : NULL;
  $file_data = !empty($config_file) ? drupal_json_decode(file_get_contents($config_file, FALSE, NULL)) : NULL;

  if (!empty($file_data)) {
    foreach ($file_data as $lang_key => $lang_data) {
      $config_data['lang'] = $lang_key;
      foreach ($lang_data as $key => $value) {
        $config_data[$key] = $value;
      }
    }
  }

  $languages = current(language_list('enabled'));
  $lang_opt = array();
  foreach ($languages as $key => $lang) {
    $lang_opt[$key] = $lang->name;
  }

  $form['form_intro'] = array(
    '#markup' => '<p>These are the help texts used for the dashboard. You can tweak them if needed by your users.</p>',
  );

  $form['lang'] = array(
    '#type' => 'select',
    '#title' => t('Language'),
    '#required' => TRUE,
    '#options' => $lang_opt,
    '#default_value' => !empty($config_data['lang']) ? $config_data['lang'] : NULL,
  );

  $form['numberOfNodes'] = array(
    '#type' => 'textarea',
    '#title' => t('Number of Nodes'),
    '#default_value' => !empty($config_data['numberOfNodes']) ? $config_data['numberOfNodes'] : NULL,
  );

  $form['numberOfEdges'] = array(
    '#type' => 'textarea',
    '#title' => t('Number of Edges'),
    '#default_value' => !empty($config_data['numberOfEdges']) ? $config_data['numberOfEdges'] : NULL,
  );

  $form['averageDistance'] = array(
    '#type' => 'textarea',
    '#title' => t('Average Distance'),
    '#default_value' => !empty($config_data['averageDistance']) ? $config_data['averageDistance'] : NULL,
  );

  $form['modularity'] = array(
    '#type' => 'textarea',
    '#title' => t('Modularity'),
    '#default_value' => !empty($config_data['modularity']) ? $config_data['modularity'] : NULL,
  );

  $form['postsByContributor'] = array(
    '#type' => 'textarea',
    '#title' => t('Posts by Contributor'),
    '#default_value' => !empty($config_data['postsByContributor']) ? $config_data['postsByContributor'] : NULL,
  );

  $form['commentsByContributor'] = array(
    '#type' => 'textarea',
    '#title' => t('Comments by Contributor'),
    '#default_value' => !empty($config_data['commentsByContributor']) ? $config_data['commentsByContributor'] : NULL,
  );

  $form['shareOfCommunityGeneratedContent'] = array(
    '#type' => 'textarea',
    '#title' => t('Share of Community-Generated Content'),
    '#default_value' => !empty($config_data['shareOfCommunityGeneratedContent']) ? $config_data['shareOfCommunityGeneratedContent'] : NULL,
  );

  $form['submit'] = array(
    '#type' => 'submit',
    '#value' => t('Submit'),
  );

  return $form;
}

/**
 * Validation for the variable settings form.
 */
function edgesense_admin_help_form_submit($form, &$form_state) {

  unset($form_state['values']['form_id'], $form_state['values']['form_token'],
    $form_state['values']['form_build_id'], $form_state['values']['op'], $form_state['values']['submit']
  );

  $new_arr = array();
  foreach ($form_state['values'] as $key => $value) {
    if ($key == 'lang') {
      $lang = $value;
      $new_arr[$lang] = array();
    }
    else {
      $new_arr[$lang][$key] = $value;
    }
  }
  $file = NULL;

  if (!empty($new_arr)) {
    $data = drupal_json_encode($new_arr);
    $destination = variable_get('edgesense_help_uri', 'public://edgesense/json/help.json');
    $file = file_unmanaged_save_data($data, $destination, FILE_EXISTS_REPLACE);
  }

  if ($file) {
    drupal_set_message(t('Json file successfully generated with Parameters'), 'status');
  }
  else {
    drupal_set_message(t("Couldn't generate json file."), 'error');
  }
}

/**
 * Page callback: settings form to export help vars to json file.
 */
function edgesense_admin_script_param_form($form, &$form_state) {

  edgesense_display_not_run_message();
  global $base_url;
  $views_key = variable_get('edgesense_views_key', NULL);

  $file = variable_get('edgesense_param_uri', 'private://edgesense/script/run.json');
  $config_file = file_exists($file) ? drupal_realpath($file) : NULL;
  $file_data = !empty($config_file) ? drupal_json_decode(file_get_contents($config_file, FALSE, NULL)) : NULL;

  $config_data = $file_data;
  if (!empty($file_data['moderator_roles'])) {
    $config_data['moderator_roles'] = explode(', ', $file_data['moderator_roles']);
  }

  // Restore the default values of the users, nodes & comments fields if the user hasn't updated them
  $run_cron_js = <<<EOF
(function ($) {
  Drupal.behaviors.edgesense = {
    attach: function (context, settings) {
      $('#edit-run-during-cron').bind('change', function() {
        var default_value = this.checked ? 1 : 0;
        var updated_value = this.checked ? 0 : 1;
        if ($('#edit-users').val() == Drupal.settings.edgesense[updated_value].users) {
          $('#edit-users').val(Drupal.settings.edgesense[default_value].users);
        }
        if ($('#edit-nodes').val() == Drupal.settings.edgesense[updated_value].nodes) {
          $('#edit-nodes').val(Drupal.settings.edgesense[default_value].nodes);
        }
        if ($('#edit-comments').val() == Drupal.settings.edgesense[updated_value].comments) {
          $('#edit-comments').val(Drupal.settings.edgesense[default_value].comments);
        }
      });
    }
  }
})(jQuery);
EOF;

  drupal_add_js($run_cron_js, 'inline');

  // JS settings array for the run_during_cron checkbox
  // Used for checking default values when the user checks/unchecks run_during_cron
  // and also for updating the values to point to the correct (default) locations
  $js_settings = array(
    array(
      'users' => $base_url . '/edgesense_users.json?edgesense_views_key=' . $views_key,
      'nodes' => $base_url . '/edgesense_nodes.json?edgesense_views_key=' . $views_key,
      'comments' => $base_url . '/edgesense_comments.json?edgesense_views_key=' . $views_key,
    ),
    array(
      'users' => drupal_realpath('private://edgesense/site_data/edgesense_users.json'),
      'nodes' => drupal_realpath('private://edgesense/site_data/edgesense_nodes.json'),
      'comments' => drupal_realpath('private://edgesense/site_data/edgesense_comments.json'),
    ),
  );

  $form['run_during_cron'] = array(
    '#type' => 'checkbox',
    '#title' => t('Run During Cron'),
    '#default_value' => variable_get('edgesense_run_during_cron', TRUE),
    '#description' => t('Controls whether the edgesense Views will be saved to disk and the python will run during Drupal\'s cron.'),
    '#attached' => array(
      'js' => array(
        array(
          'data' => array(
            'edgesense' => $js_settings,
          ),
          'type' => 'setting',
        ),
      ),
    ),
  );

  $form['users'] = array(
    '#type' => 'textfield',
    '#title' => t('Users'),
    '#required' => TRUE,
    '#default_value' => !empty($config_data['users']) ? $config_data['users'] : NULL,
    '#description' => t('<p>Url or path to users data json. The json must be in the <a href="https://github.com/Wikitalia/edgesense/blob/master/python/README.md#users-data" target="_blank">correct format</a>.</p>' .
      '<p>If you choose to not run the script during cron then please append "?edgesense_views_key=' . $views_key . '" to the end of your URL\'s.</p><p>For example: ' . $base_url . '/edgesense_users.json?edgesense_views_key=' . $views_key . '</p>'
    ),
  );

  $form['nodes'] = array(
    '#type' => 'textfield',
    '#title' => t('Nodes'),
    '#required' => TRUE,
    '#default_value' => !empty($config_data['nodes']) ? $config_data['nodes'] : NULL,
    '#description' => t('<p>Url or path to nodes data json. The json must be in the <a href="https://github.com/Wikitalia/edgesense/blob/master/python/README.md#nodes-data" target="_blank">correct format</a>.</p>' .
      '<p>If you choose to not run the script during cron then please append "?edgesense_views_key=' . $views_key . '" to the end of your URL\'s.</p><p>For example: ' . $base_url . '/edgesense_nodes.json?edgesense_views_key=' . $views_key . '</p>'
    ),
  );

  $form['comments'] = array(
    '#type' => 'textfield',
    '#title' => t('Comments'),
    '#required' => TRUE,
    '#default_value' => !empty($config_data['comments']) ? $config_data['comments'] : NULL,
    '#description' => t('<p>Url or path to comments data json. The json must be in the <a href="https://github.com/Wikitalia/edgesense/blob/master/python/README.md#comments-data" target="_blank">correct format</a>.</p>' .
      '<p>If you choose to not run the script during cron then please append "?edgesense_views_key=' . $views_key . '" to the end of your URL\'s.</p><p>For example: ' . $base_url . '/edgesense_comments.json?edgesense_views_key=' . $views_key . '</p>'
    ),
  );

  $form['auth'] = array(
    '#type' => 'fieldset',
    '#title' => t('Source data basic auth'),
    '#collapsible' => TRUE,
    '#collapsed' => empty($config_data['auth']['use_basic_auth']),
    '#tree' => TRUE,
    '#description' => t('If the source data URL require a username and password to be accessed then you\'ll need to write them here and select the checkbox below.<br/><br/>'),
  );

  $form['auth']['use_basic_auth'] = array(
    '#type' => 'checkbox',
    '#title' => t('Use the basic auth username and password.'),
    '#default_value' => !empty($config_data['auth']['use_basic_auth']) ? $config_data['auth']['use_basic_auth'] : NULL,
  );

  $form['auth']['username'] = array(
    '#type' => 'textfield',
    '#title' => t('Basic Auth Username'),
    '#default_value' => !empty($config_data['auth']['username']) ? $config_data['auth']['username'] : NULL,
    '#attributes' => array('autocomplete' => 'off'),
  );

  $form['auth']['password'] = array(
    '#type' => 'password',
    '#title' => t('Basic Auth Password'),
    '#default_value' => !empty($config_data['auth']['password']) ? $config_data['auth']['password'] : NULL,
    '#attributes' => array('autocomplete' => 'off'),
  );

  $form['moderator_roles'] = array(
    '#type' => 'checkboxes',
    '#title' => t('Moderator roles'),
    '#options' => drupal_map_assoc(user_roles()),
    '#default_value' => !empty($config_data['moderator_roles']) ? drupal_map_assoc($config_data['moderator_roles']) : array(),
    '#description' => t('<p>
        The community moderators are identified looking at the <code>roles</code> field in the users data, and the behaviour is slightly different depending wether the moderator_roles parameter is specified or not. If specified, it will be a list of roles of the role names separated by a comma.

        The default behaviour when no moderator_roles are indicated is to consider part of the moderators team any user who has a non empty roles field (the script doesn\'t look at the content of the field in this case).

        If the option is passed to the script, then only the users who have one of the given roles are considered part of the team.        
        </p>'),
  );

  $form['node_title'] = array(
    '#type' => 'textfield',
    '#title' => t('Title field'),
    '#default_value' => !empty($config_data['node_title']) ? $config_data['node_title'] : NULL,
    '#description' => t('<p>
        The value of this field will determine which field of the users JSON will be used to populate the title of the network graph nodes.
        The default if this parameter is not specified is to use the uid of the user object.
        </p>'),
  );

  $form['timestep_count'] = array(
    '#type' => 'textfield',
    '#title' => t('Timestep count'),
    '#default_value' => !empty($config_data['timestep_count']) ? $config_data['timestep_count'] : NULL,
    '#description' => t('<p>
        This parameter is used to specify the number of steps in which the whole period over which we have data is divided to calculate the intermediate metrics. The whole period is divided in the given number of timesteps and the default is null, that is don\'t divide in an exact number of timesteps.<br>
        This parameter is alternative to the \'Timestep size\' and takes precedence over that (if both are defined then the script will use the timestep count only.)
        </p>'),
  );

  $form['timestep_size'] = array(
    '#type' => 'textfield',
    '#title' => t('Timestep size'),
    '#default_value' => !empty($config_data['timestep_size']) ? $config_data['timestep_size'] : 60 * 60 * 24 * 7,
    '#description' => t('<p>
        This parameter is used to specify the size of the timestep to use in seconds. The whole period over which we have data is divided into timesteps of with size to calculate the intermediate metrics. The default is one week.<br>
        This parameter is alternative to the \'Timestep count\' and if both are defined then the script will use the timestep count only.
        </p>'),
  );

  $form['count_window'] = array(
    '#type' => 'textfield',
    '#title' => t('Count window'),
    '#default_value' => !empty($config_data['count_window']) ? $config_data['count_window'] : 1,
    '#description' => t('<p>
        The moving window of timesteps where the counts are taken. The option can be used to define a moving window of time (in number of timesteps) which is used to calculate the counts for the objects in the timestep. The deafult is 1 (meaning that only the current timestep is used for the sums). Specifying a window > 1 smoothes the graphing where the timestep resolution is too short with respect to the variations being reported. N.B. this influences only the following metrics that are computer over "a period", that is:
    <ul>
    <li>Number of Posts in period</li>
    <li>Number of Posts by contributors in period</li>
    <li>Number of Posts by team in period</li>
    <li>Share of User Generated Posts in period</li>
    <li>Share of Team/User Posts in period</li>
    <li>Number of Comments total in period</li>
    <li>Number of Comments by contributors in period</li>
    <li>Number of Comments by contributors in period</li>
    <li>Share of User Generated Comments in period</li>
    <li>Share of Team/User Generated Comments in period</li>
    </ul>
        </p>'),
  );

  $form['exclude_isolated'] = array(
    '#type' => 'checkbox',
    '#title' => t('Exclude isolated nodes'),
    '#default_value' => !empty($config_data['exclude_isolated']) ? $config_data['exclude_isolated'] : NULL,
    '#description' => t('<p>
        The script includes in the network also all the isolated active nodes, meaning nodes that have written a post but not received any comments. To exclude them you need to select this option.
        </p>'),
  );

  $form['datapackage'] = array(
    '#type' => 'fieldset',
    '#title' => t('Data package'),
    '#collapsible' => TRUE,
    '#collapsed' => empty($config_data['datapackage']['create_datapackage']),
    '#tree' => TRUE,
    '#description' => t('These parameters allow you to generate an open data version of the network. The data will be generated in the GEXF format which is the standard exchange format for many social network analysis tools (e.g. Gephi), and it will generate a <a href="http://data.okfn.org/doc/data-package">datapackage descriptor</a>.'),
  );

  $form['datapackage']['create_datapackage'] = array(
    '#type' => 'checkbox',
    '#title' => t('Create the GEXF export and the datapackage.'),
    '#default_value' => !empty($config_data['datapackage']['create_datapackage']) ? $config_data['datapackage']['create_datapackage'] : NULL,
  );

  $form['datapackage']['license_type'] = array(
    '#type' => 'textfield',
    '#title' => t('Data License Type'),
    '#default_value' => !empty($config_data['datapackage']['license_type']) ? $config_data['datapackage']['license_type'] : NULL,
    '#description' => t('It should be the name of the license (e.g. CC-BY).'),
  );

  $form['datapackage']['license_url'] = array(
    '#type' => 'textfield',
    '#title' => t('Data License URL'),
    '#default_value' => !empty($config_data['datapackage']['license_url']) ? $config_data['datapackage']['license_url'] : NULL,
    '#description' => t('It should be the URL to the license text.'),
  );

  $form['submit'] = array(
    '#type' => 'submit',
    '#value' => t('Submit'),
  );

  return $form;
}

/**
 * Validation for the variable settings form.
 */
function edgesense_admin_script_param_form_validate($form, &$form_state) {
  unset($form_state['values']['form_id'], $form_state['values']['form_token'],
    $form_state['values']['form_build_id'], $form_state['values']['op'], $form_state['values']['submit']
  );

  if (!empty($form_state['values']['timestep_count'])) {
    $value = (int) $form_state['values']['timestep_count'];
    if ($value <= 0) {
      form_set_error('timestep_count', t('Params:Timestep count - Please enter valid numeric (>0) value (or leave the field empty)'));
    }
  }

  if (!empty($form_state['values']['timestep_size'])) {
    $value = (int) $form_state['values']['timestep_size'];
    if ($value <= 0) {
      form_set_error('timestep_size', t('Params:Timestep size - Please enter valid numeric (>0) value (or leave the field empty)'));
    }
  }

  if (!empty($form_state['values']['count_window'])) {
    $value = (int) $form_state['values']['count_window'];
    if ($value <= 0) {
      form_set_error('count_window', t('Params:Count window - Please enter valid numeric (>0) value (or leave the field empty)'));
    }
  }
}

/**
 * Validation for the variable settings form.
 */
function edgesense_admin_script_param_form_submit($form, &$form_state) {

  $values = $form_state['values'];
  $values['moderator_roles'] = implode(', ', array_filter($values['moderator_roles']));

  // Update Views and URL's to use key or not
  variable_set('edgesense_run_during_cron', $values['run_during_cron']);
  edgesense_set_manual_run(empty($values['run_during_cron']));
  unset($values['run_during_cron']);

  if (!$values['auth']['use_basic_auth']) {
    unset($values['auth']);
  }

  $values['destination_path'] = drupal_realpath('public://edgesense/json');
  $values['log_path'] = drupal_realpath('private://edgesense/script');

  if (!$values['datapackage']['create_datapackage']) {
    unset($values['datapackage']);
  }
  $values['datapackage']['site_url'] = file_create_url('public://edgesense/json');

  $file = NULL;
  if (!empty($values)) {
    $data = drupal_json_encode($values);
    $destination = variable_get('edgesense_param_uri', 'private://edgesense/script/run.json');
    $file = file_unmanaged_save_data($data, $destination, FILE_EXISTS_REPLACE);
  }

  if ($file) {
    drupal_set_message(t('Script run parameters saved to file.'), 'status');
  }
  else {
    drupal_set_message(t("Couldn't generate json file."), 'error');
  }
}

/**
 * Page callback: running the script
 */
function edgesense_script_run_form($form, &$form_state) {

  edgesense_display_not_run_message();
  $logfile = drupal_realpath('private://edgesense/script/edgesense.log');
  if (file_exists($logfile)) {
    $handle = fopen($logfile, "r");
    $contents = fread($handle, filesize($logfile));
    fclose($handle);
  }
  else {
    $contents = 'The script has not run';
  }
  $run_during_cron = variable_get('edgesense_run_during_cron', NULL);
  
  $text = '<h3>Generating the metrics</h3><br>';
  if (!`which edgesense_drupal`) {
    $text .= '
        <h4>Installing the edgesense_drupal command</h4>
        <p>To prepare the metrics and populate the dashboard the <code>edgesense_drupal</code> command needs to run periodically, but it seems that it is <b>not installed</b> on the server.</p>
        <p>See <a href="https://github.com/Wikitalia/edgesense/blob/master/python/README.md" target="_blank">the python library github page</a> for details on how to install the <code>edgesense_drupal</code> command.</p>
        <hr>
        ';
  }
  else {
      $text .= '
            <p>To prepare the metrics and populate the dashboard the following command needs to run on the server periodically:</p>
            <p><pre>edgesense_drupal ' . drupal_realpath('private://edgesense/script/run.json') . '</pre></p>
            ';
      if (!empty($run_during_cron)) {
        $text .= '<p>The command above is <b>scheduled to run once a day via hook_cron</b> (Drupal periodic actions.)</p>';
      }
      else {
        $text .= '<p>You need to <b>run the above command on the server manually or schedule it</b> (e.g. via cron.)</p>';    
      }      
  }
  $text .= '
        <hr>
        <h4>Last run log</h4>
        <p>This is the log from the last time the script has run:</p>
        <p><pre>' . $contents . '</pre></p>
        <hr>
        ';
        
  $form['form_intro'] = array(
    '#markup' => $text,
  );

  // $form['submit'] = array(
  //   '#type' => 'submit',
  //   '#value' => t('Run now'),
  // );

  return $form;
}

/**
 * Form submit callback
 */
function edgesense_script_run_form_submit($form, &$form_state) {

  unset($form_state['values']['form_id'], $form_state['values']['form_token'],
    $form_state['values']['form_build_id'], $form_state['values']['op'], $form_state['values']['submit']
  );


  drupal_set_message(t('Script was run.'), 'status');
}

function edgesense_open_dashboard() {
  global $base_url;
  drupal_goto($base_url . '/' . drupal_get_path('module', 'edgesense') . '/static/dashboard.html');
}

function edgesense_tutorial_upload_api() {
  $towrite = $_POST["result"];
  if ($towrite) {
    $filename = "result" . "-" . rand() . "_" . time() . ".json";
    $destination = "private://edgesense/tutorial_uploads/" . $filename;
    $file = file_unmanaged_save_data($towrite, $destination, FILE_EXISTS_REPLACE);
    header("X-Edgesense-Saved: " . $filename);
  }
  print t('{result: \'ok\'}');
  exit();
}

