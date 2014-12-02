<?php

// The config.php file should define
// the following variables:
//   - $base_dir: is the base directory where the files are written
//   - $valid_origin: is the hostname of from which we accept the CORS requests
$config = './config.php';
if (file_exists($config)) {
    include $config;
} else {
    // defaults
    $base_dir = '/tmp';
    $valid_origin = '';
    $script_base = '';
}

$incoming_origin = array_key_exists('HTTP_ORIGIN', $_SERVER) ? $_SERVER['HTTP_ORIGIN'] : null;
if (($incoming_origin !== null && $incoming_origin==$valid_origin) || $valid_origin==='') {
    if ($incoming_origin !== null && $valid_origin!=='') {
        header('Access-Control-Allow-Origin: '.$valid_origin);
        header('Access-Control-Allow-Methods: GET, PUT, POST, DELETE, OPTIONS');
        header('Access-Control-Max-Age: 1000');
        header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');
    }
    $towrite = $_POST["result"];
    if ($towrite) {
        $filename = "result"."-".rand()."_".time().".json";
        $thefile = $base_dir."/".$filename; 
        $openedfile = fopen($thefile, "w");
        fwrite($openedfile, $towrite);
        fclose($openedfile);
        header("X-Edgesense-Saved: ".$filename);
    }
}
return "";

?>