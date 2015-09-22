<?php

/**
 * @file
 * Definition of edgesense_views_access_plugin.
 */

/**
 * Edgesense Custom Access plugin.
 */
class edgesense_views_access_plugin extends views_plugin_access {
  function summary_title() {
    return t('Edgesense Permission or Token');
  }

  function access($account) {
    return edgesense_views_access_callback($account);
  }

  function get_access_callback() {
    return array('edgesense_views_access_callback', array());
  }
}

