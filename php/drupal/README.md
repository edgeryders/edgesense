## Install 

Download and install the latest module: [edgesense_latest.tgz](../dist/edgesense_latest.tgz)

### Prerequisites

To use the module on your Drupal site, you'll need to install the python library on the server (see the [Python library README](python/README.md)), and have the following modules enbaled:

- Views
- JSON Views

## Setup

The module uses the private drupal filesystem which has to be configured for the module to work properly. 

The module will dump a script run configuration file in the directory <drupal private dir>/edgesense/script. You will need to protect this directory if you are going to setup a set of source URLs for the data that require a password, as the password will be written to that file.


    
