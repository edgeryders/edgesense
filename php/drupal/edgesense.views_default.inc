<?php

/**
 * @file
 * include edgesense default views
 */

/**
 * Implements hook_views_default_views().
 */
function edgesense_views_default_views() {
  $views = array();
  $files = file_scan_directory(drupal_get_path('module', 'edgesense') . '/views', '/\.view/');
  foreach ($files as $filepath => $file) {
    require $filepath;
    if (isset($view)) {
      $views[$view->name] = $view;
    }
    unset($view);
  }
  return $views;
}

