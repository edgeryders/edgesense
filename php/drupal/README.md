# Install 

The Edgesense Drupal module requires other components to be installed on the server to function. The module itself checks for all the prerequisites and notifies you if anything is missing, but it is better to simply install them before configuring the module.

### Detailed procedure
1. [Install the data processing library](#1-install-the-data-processing-library)
2. [Enable the private files](#2-enable-the-private-files)
3. [Install the required drupal modules](#3-install-the-required-drupal-modules)
4. [Install the module](#4-install-the-module)

If you have an old stand-alone installation of edgesense working with your site, you'll need to do some cleanup beforehand. See [old edgesense installation cleanup](#b-old-edgesense-installation-cleanup) for details.

## 1. Install the data processing library

First you need to install the python library, [the instructions](../../python/README.md) are simple, on the computer where the drupal application is running (that is your site web server), you will need to:

- connect to the machine with `ssh` or other method
- execute `sudo pip install edgesense` on the console
- make sure the `edgesense_drupal` is available to the user running the drupal application (the directory where `edgesense_drupal` has been installed by the `pip install` command should be in the default PATH)

![pip install edgesense](../../documentation/images/pip_install_edgesense.gif)

If you are not able to do it on your own you need to **ask for help to your server administrator**. This may happen for instance if you don't have enough permissions to install new software on that server.

## 2. Enable the private files 

The private files directory is required to be setup in drupal since that is the place on the server where the module stores the configuration for the script that runs (the module requires it to be in the private files directory to make sure it's not accessible from the browser.)

To enable the private files directory you will need to:

- go in the drupal administration page, 
- open the **Configuration** > **File system** panel
- add a directory in the **Private file system** field
- save the configuration

![enable drupal private files](../../documentation/images/drupal_private_files.png)

The configured directory should:

- exist on the server filesystem
- be writable by the user running the drupal application


## 3. Install the required drupal modules

These modules are required and need to be installed:

- Chaos Tool Suite (CTools): 
    - download the module from https://www.drupal.org/project/ctools, 
    - uncompress it in `<drupal root>/sites/all/modules/contrib/ctools`       
- Views:
    - download the module from https://www.drupal.org/project/views,
    - uncompress it in `<drupal root>/sites/all/modules/contrib/views`
- Views Datasource:
    - download the module from https://www.drupal.org/project/views_datasource, 
    - uncompress it in `<drupal root>/sites/all/modules/contrib/views_datasource`
        
From the admin interface in Drupal, enable the following modules (at least): 

- Chaos tools, 
- Views, 
- Views JSON

![enable drupal chaos tools module](../../documentation/images/drupal_modules_chaos_tools.png)
![enable drupal views module](../../documentation/images/drupal_modules_views.png)

And save the configuration.

## 4. Install the module

- Download the module: [edgesense_latest.tgz](../dist/edgesense_latest.tgz)
- Unpack the module in `<drupal root>/sites/all/modules/contrib/edgesense`
- From the admin interface in Drupal, enable the Edgesense module

![enable edgesense views module](../../documentation/images/drupal_modules_edgesense.png)

During the install phase the module runs the script a first time, **this can take some time** but at the end of the install process you'll be greeted with a message that invites you to open the dashboard.

![edgesense installed](../../documentation/images/edgesense_installed.png)

The default install uses the Drupal's cron to run the processing scripts once per day. If you have a big community and the Drupal's cron system times out while processing, you'll have to disable the automatic daily run from the Edgesense admin pages and you will have to schedule the runs with a different method (e.g. using the server system's cron scheduler)

## Appendix

### A. Post install customizations

You can customize your Edgesense install in various ways:

- If you need to change the parameters by which the script processes the data, you can do so using the Edgesense configuration panel accessible from the Drupal admin interface: ![edgesense admin](../../documentation/images/edgesense_admin.png).
- If you need any special behaviour when selecting the data from the site you can customize the `edgesense_*` views, for instance if you want to filter somehow the data. If you have customized your views then updating the module in the future will not rebuild the views, but it'll keep your customizations.
- If you have a big community and the Drupal's cron system times out while processing, you'll have to disable the automatic daily run from the Edgesense admin pages and you will have to schedule the runs with a different method (e.g. using the server system's cron scheduler).

### B. Old edgesense installation cleanup

You will need to do some cleanup prior to the install if you had configured your drupal site for a standalone version of Edgesense. This is because the new module will create the views for you and it will not overwrite a view if it find one with the same name. If the old views were not configured correctly for the new module then the export of the data might fail when running the data processing step. Therefore it is advisable to remove o at least rename the views.

### C. Errors while installing

You may receive some error message when installing the module if some of the prerequisites are not met. In this case you will need to:

1. disable the Edgesense module (if it was enabled)
2. uninstall the Edgesense module (from the Drupal modules admin page)
3. fix the error (e.g. install the missing library)
4. enable again the Edgesense module 