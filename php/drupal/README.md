## Install 

The Edgesense Drupal module requires other components to be installed on the server to function. It checks for all the prerequisites and notifies you if anything is missing, but it is better to simply install them before configuring the module.

### 1. Data processing library

You need to install the python library, [the instructions](../../python/README.md) are simple:

- execute `sudo pip install edgesense` on the server whgere the Drupal application runs
- make sure the `edgesense_drupal` is available to the user running the drupal application (it should be in the default PATH)

### 2. Enable the private files 

The private files directory is required to be setup since there the module stores the configuration for the script that runs (to make sure it's not accessible from the browser.)

### 3. Install the required drupal modules

These modules are required and need to be installed:

- Chaos Tool Suite (CTools): 
    - download the module from https://www.drupal.org/project/ctools, 
    - uncompress it in `<drupal root>/sites/all/modules/contrib/ctools`       
- Views:
    - download the module https://www.drupal.org/project/views,
    - uncompress it in `<drupal root>/sites/all/modules/contrib/views`
- Views Datasource:
    - download the module from https://www.drupal.org/project/views_datasource, 
    - uncompress it in `<drupal root>/sites/all/modules/contrib/views_datasource`
        
From the admin interface in Drupal, enable the following modules (at least): 

- Chaos tools, 
- Views content panes, 
- Views, 
- Views JSON

### 4. Install the module: 

- Download the module: [edgesense_latest.tgz](../dist/edgesense_latest.tgz)
- Unpack the module in `<drupal root>/sites/all/modules/contrib/edgesense`
- From the admin interface in Drupal, enable the Edgesense module

The module during the install phase runs the script a first time, this can take some time but at the end of the install process you'll be greeted with a message that invites you to open the dashboard.

The default install uses the Drupal's cron to run the processing scripts once per day. If you have a big community and the Drupal's cron system times out while processing, you'll have to disable the automatic daily run from the Edgesense admin pages and you will have to schedule the runs with a different method (e.g. using the server system's cron scheduler)


    
