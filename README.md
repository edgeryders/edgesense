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

### Source data format

The script that builds the metrics will expect three JSON source files, respectively for: users data, nodes (posts) data, comments data

Their structure is quite simple and the data used is minimal (the script doesn't mind if the files are more complex provided that the basic information is there).

#### Users data

The file should contain a top level object with a "users" property that should be an array of user objects.
Each user object should have at least the ```uid``` which is used to identify the user in the other files, the ```created``` field that is the date/time (as a timestamp) of the user creation. The administrators are identified as the users that have a ```roles``` field defined (the script doesn't look at the content of this file).

```
{
  "users": [
    {
      "user": {
        "uid": "1",
        "created": "1315483617",
        "roles": "****"      
      }
    },
    ...
  ]
}
```

#### Nodes data

The file should contain a top level object with a "nodes" property that should be an array of nodes objects.
Each node will be identified by the ```nid``` field. The ```uid``` field will be used to find the node author (among the users). The date of creation of the node is taken from the ```date``` field that has to have the format ```%d %b %Y - %H:%M``` e.g.: "22 May 2014 - 17:35".
If present the fields ```title``` and ```Full text``` are used to compute the 'weight' of the node and then used in some metrics.

```
{
  "nodes": [
    {
      "node": {
        "nid": "42",
        "uid": "4",
        "date": "14 Oct 2011 - 16:55",
        "title": "...",
        "Full text": "...,
      }
    },
    ...
  ]
}
```

#### Comments data

The file should contain a top level object with a "comments" property that should be an array of comments objects.
Each comment will be identified by the ```cid``` field while the ```nid``` field will be used to find the node where this comment was placed and the ```pid``` field to find the parent comment in case of threaded comments.
The ```uid``` field should be the id of the user that has written the comment. The ```timestamp``` field should be the date/time (as a timestamp) of the comment creation.
If present the ```comment``` and ```subject``` fields are used to compute the 'weight' of the comment and then used in some metrics.

```
{
  "comments": [
    {
      "comment": {
        "cid": "57",
        "nid": "27",
        "uid": "10",
        "pid": "30",
        "timestamp": "1320769943",
        "comment": "...",
        "subject": "...",
      }
    },
    ...
  ]
}
```

### Running the script

To build the metrics you need to run the python script:

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

### Configuring the dashboard

There are a few parameters that permit the configuration of the dashboad page. 
One of the first things the page does on load is to read the parameters from a configuration.json file in the static/json directory, so to customize them one just needs to create the file (there is an example file in the static/json directory)

The parameters currently available are:

- ```dashboard_name```: this is used to set the page title
- ```analytics_tracking_id```: this should be set to enable the google analytics tracking for the dashboard

### Analytics tracking 

If enabled in the parameters the dashboard will track with Google Analytics the events happening in the interface. This is tracked (beyond page loads):

- show / hide moderators (category: 'filter', action: 'toggle_team', label: 1/0 if the team was shown or hidden )
- drag time slider (category: 'filter', action: 'date_range', label: the date selected )
- show / hide partition (category: 'filter', action: 'toggle_partition', label: the partition, value: 1/0 if the partition was shown or hidden  )
- lock / unlock graph (category: 'control', action: 'toggle_lock', label: 1/0 if the graph was locked/unlocked )
- show contextual help (category: 'help', action: 'toggle', label: the help key toggled, value: 1/0 if the help message was shown or hidden )
