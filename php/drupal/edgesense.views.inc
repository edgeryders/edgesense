<?php

/**
 * @file
 * edgesense Views plugins file
 */

/**
 * Implements hook_views_plugins().
 */
function edgesense_views_plugins() {
  return array(
    'access' => array(
      'edgesense_views_perm_or_token' => array(
        'title' => t('Administer Edgesense Permission or Token'),
        'help' => t('Access is allowed only for users with the "Administer Edgesense" permission or a valid token.'),
        'handler' => 'edgesense_views_access_plugin',
      ),
    ),
  );
}

