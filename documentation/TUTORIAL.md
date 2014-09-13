## Processing the data

To extract the data collected from the interactive tutorial there is a script in the python 
directory which parses the json files and extracts a CSV file with a row for each tutorial run
that has been completed. 

The script can be called with two parameters:

```
python tutorial.py -s <source dir> -f <output filename>
```

The columns in the output file are the following:

- run_id: an id used to join the various files that may be sent for a tutorial run
- base: the 'version' of the data that was presented in the dashboard to the user that did this tutorial run
- betweenness_bin: the first tutorial question
- relationship_percentage: the second tutorial question
- posts_percentage: the third tutorial question
- comments_share: the fourth tutorial question
- modularity_increase: the fifth tutorial question
- survey-1: the first survey question
- survey-2: the second survey question
- survey-3: the third survey question
- survey-4: the fourth survey question
- survey-5: the fifth survey question
- comments: the comments left by the user
