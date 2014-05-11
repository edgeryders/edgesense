## Edgesense demo

The demo directory contains the current edgesense demo code:

- The bulid_network.py file is the script used to build the network from the source json files and to compute all the metrics
- The public directory contains the visualization / dashboard code (mainly javascript and HTML that read the json produced by the python script)

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

You need to set the directory where the script can find the source jsons (set the source_path variable in the build_network.py file)

```
python build_network.py
```

