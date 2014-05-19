## Edgesense

The current incarnation of the edgesense SNA tool is made up of two components:

- a python script used to build the network from the source json files and to compute all the metrics. This script is contained in the python directory (it is build_network.py) 
- a single-page HTML5/javascript application that reads the json produced by the python script and builds a dashboard with the visualization of the network and the metrics

### Prerequisites

To run the python script you'll need to install networkx and the python louvain modularity module

#### networkx

```
sudo pip install networkx
```

#### louvain module

1. download the louvain module: https://bitbucket.org/taynaud/python-louvain
2. install the software ```python setup.py install```

### Running the script

To bulid the metrics you need to run the python script:

```
python python/build_network.py 
```

By default it looks for the source files ```users.json```, ```nodes.json```, ```comments.json``` in the directory specified by the ```EDGESENSE_SOURCE_DIR``` environment variable. An alternative is to pass arguments to the script.

```
python python/build_network.py \
       -u <url or path to users json> \
       -n <url or path to nodes json> \
       -c <url or path to comments json>
```

The arguments passed may be URLs to remote json files (e.g. json views from a Drupal site.)

