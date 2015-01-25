## TODO

- add metadata subpage
- package the module for drush (registration?)
- add a way to upload tutorial results
- add customization of dashboard

#### Notes

 - when installing / packaging the default json files should be loaded into the public directory ()
 - how to serve a new
 
## Done

- add the help to the help page
- add a way to configure the module
- add all configuration parameters to the config page
- add all the runtime parameters to the page for the parameters configuration
- add a way to schedule the script
- add a way for the script to be launched with a single json file for the parameters
- add some help text to the fields
- add a way to configure the directory were the files are stored
- add an edgesense dashboard to the module
- package the module (add build scripts via make?)

## Setup

The module uses the private drupal filesystem which has to be configured for the module to work properly. 

The module will dump a script run configuration file in the directory <drupal private dir>/edgesense/script. You will need to protect this directory if you are going to setup a set of source URLs for the data that require a password, as the password will be written to that file.
    
