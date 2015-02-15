## Edgesense

This is the python library and scripts for the Edgsense social network analysis tool (see: https://github.com/Wikitalia/edgesense )

The python scripts build the network from source json files and compute all the metrics.

### Prerequisites

To run the basic python script you'll need to install networkx and the python louvain modularity module.

There is a requirements.txt file that includes also the optional libraries required to process files in the Catalyst Interchange Format (CIF)

To install only the basic parsing:

```
sudo pip install edgesense
```


To add the catalyst parsing:

```
sudo pip install -r requirements-catalyst.txt
```

To install all the required libraries:

```
sudo pip install -r requirements.txt
```

### Source data format

The script that builds the metrics will expect three JSON source files, respectively for: users data, nodes (posts) data, comments data

Their structure is quite simple and the data used is minimal (the script doesn't mind if the files are more complex provided that the basic information is there).

#### Users data

The file should contain a top level object with a "users" property that should be an array of user objects.
Each user object should have at least the ```uid``` which is used to identify the user in the other files, the ```created``` field that is the date/time (as a timestamp) of the user creation. 

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

The administrators are identified looking at the ```roles``` field, and the behaviour is slightly different depending wether the ```admin-roles``` parameter is specified or not. The script option ```admin-roles```, if specified, should be a list of roles of the role names separated by a comma.

The default behaviour when no ```admin-roles``` are indicated is to consider part of the moderators team any user who has a *non empty* roles field (the script doesn't look at the content of the field in this case).

If the option is passed to the script, then only the users who have one of the given roles are considered part of the team.

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
python python/run_script.py build_network
```

if you have installed the library with pip, a convenient wrapper has been created:

```
edgesense_build_network 
```

By default it looks for the source files ```users.json```, ```nodes.json```, ```comments.json``` in the directory specified by the ```EDGESENSE_SOURCE_DIR``` environment variable. An alternative is to pass arguments to the script.

```
edgesense_build_network \
       -u <url or path to users json> \
       -n <url or path to nodes json> \
       -c <url or path to comments json> \
       -o <path to the directory where the json files will be generated> \
       -t <field in the users json to use for the user label> \
       -s <the size of the timestep to use in seconds> \
       -f <the exact number of timesteps to use> \
       -w <the moving window of timesteps where the counts are taken> \
       --username <the Http Basic Auth username to access the remote file> \
       --password <the Http Basic Auth password to access the remote file> \
       --admin-roles="<comma separated list of roles marking a user as part of the community team>"
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
- if no admin roles are specified the deafult behaviour is to consider part of the moderators team any user who has a *non empty* roles field
- the script includes in the network also all the isolated active nodes, meaning nodes that have written a post but not received any comments. To exclude them you need to pass the ```--exclude-isolated``` option to the script
- if you want to generate an open data package with the raw data from the network data, then you'll need to pass the license type and license url to customize the datapackage that is generated: ```--datapackage-license-type="<license name for the datapackage>" --datapackage-license-url="<license url for the datapackage>"```

#### Parsing the CATALYST format

The following command allows one to parse the catalyst format and obtain a set of json files in the format accepted by the build_network script

```
edgesense_parse_catalyst -s <parse source file or URL> -o <output directory>
```

Then you would run the build_network script on the output files:

```
edgesense_build_network \
       -u <output directory>/users.json \
       -n <output directory>/nodes.json \
       -c <output directory>/comments.json
```

#### Parsing a mailing list archive

It is possible to use Edgesense to analyse the network of interactions that happen in a mailing list. All you need to do is to download an archive of the mailing list in mbox format and run the parsing script on the archive. The most common mailing list software usually permit creating such archive files.
 

```
edgesense_parse_mailinglist -s <archive files (if more than one put them here separated by a comma, without spaces)> \
                            -o <output directory> \
                            -m <moderators emails, comma separated> \
                            --charset="<charset of the archive file (default utf-8)>"
```

Then you would run the build_network script on the output files:

```
edgesense_build_network \
       -u <output directory>/users.json \
       -n <output directory>/nodes.json \
       -c <output directory>/comments.json
```


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

