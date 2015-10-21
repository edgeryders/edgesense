<?php

/**
 * @file
 * Edgesense Drupal tutorial uploader.
 */

/**
 * Tutorial data upload
 */
function edgesense_tutorial_upload_api($form, &$form_state) {
  $data = $_POST["result"];
  if ($data) {
    $destination = 'private://edgesense/tutorial_uploads';
    $filename = "result" . "-" . rand() . "_" . time() . ".json";
    $thefile = $base_dir . "/" . $filename;
    $file = file_unmanaged_save_data($data, $thefile, FILE_EXISTS_REPLACE);
    header("X-Edgesense-Saved: " . $filename);
  }
  echo '';
  drupal_exit();
}

