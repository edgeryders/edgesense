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
       -c <url or path to comments json> \
       -t <field in the users json to use for the user label> \
       -s <the size of the timestep to use in seconds> \
       -f <the exact number of timesteps to use> \
       -w <the moving window of timesteps where the counts are taken> 
```

- The arguments passed to -u, -n, -c may be URLs to remote json files (e.g. json views from a Drupal site.)
- The default for the field used as the user label (-t) is the uid of the user object
- The timesteps size and the timesteps count options are alternative, with -f taking precedence. If the -f parameter is used then the whole period is divided in the given number of timesteps (the default is null, that is don't divide in an exact number of timesteps). If the calculated timestep is less than one day then 1 day is used. The default for -s is 1 week.
- The -w option can be used to define a moving window of time (in number of timesteps) which is used to calculate the counts for the objects in the timestep. The deafult is 1 (meaning that only the current timesteamp is used for the sums). Specifying a window > 1 smoothes the graphing where the timestep resolution is too short with respect to the variations being reported. N.B. this influences only the following metrics that are computer over "a period", that is:
    - Number of Posts in period
    - Number of Posts by contributors in period
    - Number of Posts by team in period
    - Share of User Generated Posts in period
    - Share of Team/User  Posts in period
    - Number of Comments total in period
    - Number of Comments by contributors in period
    - Number of Comments by contributors in period
    - Share of User Generated Comments in period
    - Share of Team/User Generated Comments in period
    