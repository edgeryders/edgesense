### Configuring the dashboard

The dashboard single-page-app is included in the static directory, to make it accessible to the users you'll need to expose the contents of the static directory from a webserver.
It can be installed either as the root directory of a site or under a higher level path (e.g. http://example.com/edgesense).

There are a few parameters that permit the configuration of the dashboad page. 
One of the first things the page does on load is to read the parameters from a configuration.json file in the ```[dashboard url]/json``` directory, so to customize them one just needs to create the file (there is an example file in the ```[dashboard url]/json``` directory)

The parameters currently available are:

- ```dashboard_name```: this is used to set the page title
- ```analytics_tracking_id```: this should be set to enable the google analytics tracking for the dashboard
- ```tutorial_upload```: this should be set to a URL which can receive the POSTs from the tutorial with the results to be saved.
- ```base_data_url```: this optional parameter should be set to the absolute URL where the page can access the data saved by the python script. If it is empty it will be the ```[dashboard url]/json/data``` URL. You can use this to separate the serving of the dashboard from the processing of the files (e.g. have the dashboard live at ```/edgesense``` and the data live at ```/data```. N.B. it is possible to have the processed data needs to reside on a different server but you'll have to proxy the json files from the same server as the dashboard.

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

