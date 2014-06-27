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
Each node will be identified by the ```nid``` field. The ```uid``` field will be used to find the node author (among the users). The date of creation of the node is taken from the ```created``` field (should be output as a timestamp).
If present the fields ```title``` and ```Full text``` are used to compute the 'weight' of the node and then used in some metrics.

```
{
  "nodes": [
    {
      "node": {
        "nid": "42",
        "uid": "4",
        "created": "1315483617",
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
The ```uid``` field should be the id of the user that has written the comment. The ```created``` field should be the date/time (as a timestamp) of the comment creation.
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
        "created": "1320769943",
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
       -w <the moving window of timesteps where the counts are taken> \
       --username <the Http Basic Auth username to access the remote file> \
       --password <the Http Basic Auth password to access the remote file
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
- if no username and password are specified then the script assumes that the remote file is openly accessible i.e. it uses no authentication when downloading the files.

### Output json files

The python script creates four different files:

- metrics.min.json contains only the metrics (without the network of nodes and edges)
- network-no-metrics.min.json contains only the network (without the metrics)
- network.json contains both the network and the metrics in a pretty-printed, indented form.
- network.min.json contains both the network and the metrics in a minified format (no new-lines, no-indentation).

The dashboard script (```app.js```) loads the ```network.min.json``` which has all the informations available, the others may be useful for different purposes (specially for the bigger networks where these files might get large.)

The python script saves these files in a timestamped directory and writes a file ```last.json``` with the name of the directory where the output can be found:

```
{"last": "2014-06-26-16-43-41"}
```

In this way it never overwrites the older extractions: this can be useful to debug the dashboard and to perform other analysis later. The dashboard object loads the last.json file (which it finds at a fixed location) and from its content knows where to look for the latest processing results.

#### Meta information

All the produced json files contain a meta element which holds information about the file itself. Currently the only information contained in the meta element is a generated field with the timestamp of the moment when the file was built:

```
{
    ...
    "meta": {
        "generated": 1403793821
    },
    ...
}
```

#### Metrics format

The result files that contain the metrics have a ```metrics``` element in the topmost JSON object. Metrics contain an array of objects each one of which holds the metrics for a given timestep (see above for how the timesteps are computed and used.) The ```ts``` field of the metric holds the timestamp of the reference point in time when the metrics are calculated, this timestamp is important when animating the dashboard because at any given time the time slider will identify one timestamp, and the corresponding values will be shown in the side metrics.

All the metrics have a prefix that says if they are calculated for the whole network, for just the end users network (filtering out the team), or only for the team (the latter is just for some metrics like the posts and comments count.). Some metrics that have value for a single user are represented as a map from the user id to the actual metric value (e.g. the degree.)

Here is an example of all the metrics that are calculated:

```
{
    "metrics": [
    {
        "user:avg_degree": 0,
        "full:avg_out_degree": 0,
        "user:posts_count": 2,
        "user:density": 0,
        "full:density": 0,
        "user:avg_betweenness_effort": 0,
        "full:posts_count": 14,
        "team:posts_count": 12,
        "user:team_comments_share": 0,
        "user:posts_share": 0.14285714285714285,
        "user:ts_comments_count": 0,
        "user:degree_effort": {
            "44": 0,
        },
        "user:comments_count": 0,
        "user:conversations": 0,
        "team:ts_comments_count": 4,
        "full:avg_betweenness": 0,
        "full:ts_comments_count": 4,
        "user:ts_team_comments_share": 0,
        "user:out_degree": {
            "44": 0,
        },
        "user:active_count": 0,
        "team:ts_posts_count": 12,
        "user:ts_team_posts_share": 0,
        "user:ts_posts_share": 0,
        "user:degree": {
            "44": 0,
        },
        "user:betweenness_count": {
            "44": 0,
        },
        "full:nodes_count": 10,
        "user:noteam_conversations": 0,
        "user:avg_in_degree": 0,
        "ts": 1363690920,
        "user:betweenness": {
            "44": 0,
        },
        "full:degree_effort": {
            "3": 0,
        },
        "user:louvain_modularity": null,
        "full:louvain_modularity": null,
        "full:avg_betweenness_effort": 0,
        "full:betweenness_count": {
            "3": 0,
        },
        "full:avg_degree_effort": 0,
        "user:ts_posts_count": 0,
        "full:avg_in_degree": 0,
        "user:noteam_active_count": 0,
        "team:comments_count": 4,
        "full:ts_posts_count": 12,
        "user:edges_count": 0,
        "user:active_share": 0,
        "full:betweenness": {
            "3": 0,
        },
        "user:avg_degree_count": 0,
        "full:betweenness_effort": {
            "3": 0,
        },
        "user:avg_betweenness_count": 0,
        "full:degree": {
            "3": 0,
        },
        "user:avg_out_degree": 0,
        "full:in_degree": {
            "3": 0,
        },
        "full:out_degree": {
            "3": 0,
        },
        "full:degree_count": {
            "3": 0,
        },
        "user:degree_count": {
            "44": 0,
        },
        "user:ts_comments_share": 0,
        "user:conversations_share": 0,
        "user:avg_betweenness": 0,
        "full:comments_count": 4,
        "user:avg_degree_effort": 0,
        "user:nodes_count": 2,
        "partitions": null,
        "user:team_posts_share": 6,
        "user:comments_share": 0,
        "user:in_degree": {
            "44": 0,
        },
        "user:avg_distance": null,
        "full:edges_count": 0,
        "full:avg_betweenness_count": 0,
        "full:avg_distance": null,
        "full:avg_degree": 0,
        "user:betweenness_effort": {
            "44": 0,
        },
        "full:avg_degree_count": 0
    },    
    ]
}
```

N.B. the metrics ending with "effort" are calculated taking into account a weight which is proportional to the dimension of the user contribution (e.g. the characters written in the comment)

#### Network format

The result files that contain the network representation have two elements in the top JSON object: a ```nodes``` object containing all te network nodes and an ```edges``` element containig all the network edges.

Here is an example of the nodes object:

```
{
    "nodes": [

        {
            "created_ts": 1367242609,
            "name": "John Doe",
            "team_ts": null,
            "created_on": "2014-06-27",
            "link": "http://example.com/001",
            "team": false,
            "active": true,
            "id": "001",
            "team_on": null
        },
    ]
}
```

Each edge object has a field for the source and the target nodes, a timestamp, and the indication if one of the two nodes is a moderator (team member.)

```
{
    "edges": [

        {
            "target": "56",
            "ts": 1363690920,
            "source": "3",
            "team": true,
            "effort": 0,
            "id": "3_56_1363690920"
        },
    ]
}
```

To allow different visualizations to be done later and to avoid losing too much information, all the edges between two given nodes are preserved in the output file, that is the network would be a multi-directed edges network. The current dashboard will merge all the edges between from node A to node B in a single edge but this could be changed later if a different representation is implemented.


### Analytics tracking 

If enabled in the parameters the dashboard will track with Google Analytics the events happening in the interface. This is tracked (beyond page loads):

- show / hide moderators (category: 'filter', action: 'toggle_team', label: 1/0 if the team was shown or hidden )
- drag time slider (category: 'filter', action: 'date_range', label: the date selected )
- show / hide partition (category: 'filter', action: 'toggle_partition', label: the partition, value: 1/0 if the partition was shown or hidden  )
- lock / unlock graph (category: 'control', action: 'toggle_lock', label: 1/0 if the graph was locked/unlocked )
- show contextual help (category: 'help', action: 'toggle', label: the help key toggled, value: 1/0 if the help message was shown or hidden )

### Tutorial

The user can also access an interactive tutorial from a link in the top-right of the page. A moderator of this community (or any user who has access to the dashboard) can follow the interactive tutorial to gain confidence with the tool interface, and most importantly start to learn how to interpret some of the social network analytics exposed by the metrics. Each tutorial step will ask a question that addresses a concrete problem that an administrator might have. Under each question a hint is shown, with information about how to use the EdgeSense interface to answer the question. 

The tutorial is implemented in the ```tutorial.js``` javascript file with most of the markup being included directly into the index.html page (inside a ```#tutorial``` div.)

If configured the tutorial posts the results to a remote URL for collection and further analysis (to help improve the dashboard and the metrics.)

In the php directory of the project there is a sample script that is being used to collect the tutorial answers:

The ```uploader.php``` script can be installed anywhere (even on a different host).

It receives a request from the tutorial javascript and:

1. includes the config file if it is found on the same dir
2. sets the CORS headers to allow calls from the origin host
3. saves the content of the result parameter to a .json file in the directory spceified by the configuration

### Configuring the dashboard

There are a few parameters that permit the configuration of the dashboad page. 
One of the first things the page does on load is to read the parameters from a configuration.json file in the static/json directory, so to customize them one just needs to create the file (there is an example file in the static/json directory)

The parameters currently available are:

- ```dashboard_name```: this is used to set the page title
- ```analytics_tracking_id```: this should be set to enable the google analytics tracking for the dashboard
- ```tutorial_upload```: this should be set to a URL which can receive the POSTs from the tutorial with the results to be saved.

