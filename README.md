## Edgesense

The current version of the Edgesense SNA tool is made up of:

- a data processing script used to build the network from the source json files and to compute all the metrics. This script is contained in the python directory and can be installed via a simple command. 
- a single-page HTML5/javascript application that reads the json produced by the python script and builds a dashboard with the visualization of the network and the metrics
- a Drupal module for easy installation of the dashboard in a Drupal site.

### Data processing

See the Python library [README](python/README.md) for details on how to install the script.

### Drupal module

See the Drupal module [README](php/drupal/README.md) for installation instructions.

### Dashboard documentation

See the [dashboard documentation](documentation/DASHBOARD.md) for details on the configuration.

