<?php

// The config.php file should define
// the following variables:
//   - $base_dir: is the base directory where the files are written
//   - $valid_origin: is the hostname of from which we accept the CORS requests 
$config = 'config.php';
if (file_exists($config)) {
    include $config;
} else {
    // defaults 
    $base_dir = '/tmp';
    $valid_origin = '';
}

if ($_SERVER['HTTP_ORIGIN']==$valid_origin) {
    header('Access-Control-Allow-Origin: '.$_SERVER['HTTP_ORIGIN']);
    header('Access-Control-Allow-Methods: GET, PUT, POST, DELETE, OPTIONS');
    header('Access-Control-Max-Age: 1000');
    header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');
    $towrite = $_POST["result"];
    if ($towrite) {
        $thefile = $base_dir."/result_".time().".json"; 
        $openedfile = fopen($thefile, "w");
        fwrite($openedfile, $towrite);
        fclose($openedfile);    
    }
}
return "";

?>