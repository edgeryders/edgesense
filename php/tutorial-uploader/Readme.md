The ```uploader.php``` script can be installed anywhere (even on a different host).

It receives a request from the tutorial javascript and:

1. includes the config file if it is found on the same dir
2. sets the CORS headers to allow calls from the origin host
3. saves the content of the result parameter to a .json file in the directory spceified by the configuration