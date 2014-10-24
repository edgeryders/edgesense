import os, sys
import json
import csv
from datetime import datetime
import time
import logging

from edgesense.utils.logger_initializer import initialize_logger
import edgesense.utils as eu
import edgesense.twitter as et

def write_file(elements, name, destination_path):
    # dump the network to a json file, formatted
    eu.resource.save(elements, name, destination_path, True)
    logging.info("Parsing tweets - Saved: %(d)s/%(n)s" % {'d':destination_path, 'n':name})

def parse_options(argv):
    import getopt
    # defaults
    source = None
    outdir = '.'
    dumpto = None
    
    try:
        opts, args = getopt.getopt(argv,"s:o:",["source-csv=","outdir=", "dumpto="])
    except getopt.GetoptError:
        logging.error('parse_tweets.py -s <source CSV> -o <output directory> --dumpto="<where to save the downloaded file>"')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
           logging.info('parse_tweets.py -s <source CSV> -o <output directory>')
           sys.exit()
        elif opt in ("-s", "--source-csv"):
           source = arg
        elif opt in ("-o", "--outdir"):
           outdir = arg
        elif opt in ("--dumpto"):
           dumpto = arg
           
    logging.info("parsing url %(s)s" % {'s': source})
    return (source,outdir,dumpto)

def main(argv):
    initialize_logger('./log')
    
    generated = datetime.now()
    source, outdir, dumpto = parse_options(argv)
    logging.info("Parsing tweets - Started")
    logging.info("Parsing tweets - Output directory: %(s)s" % {'s':outdir})
    
    # 1. load and parse the CSV file into a list of records
    if dumpto:
        tag = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')+'.csv'
        dump_to = os.path.join(dumpto, tag)
    else:
        dump_to = None
    tweets = et.csv_tweets.load_and_parse(source, sort_key='created_ts', dump_to=dump_to)
    
    # 2. extract the users from the tweets
    users = et.extract.extract_users(tweets)
    sorted_users = sorted(users, key=eu.sort_by('created'))
    # users = { 'users': [{'user': user_data} for user_data in users] }

    # 3. extract the nodes from the tweets
    nodes = et.extract.extract_nodes(tweets)
    sorted_nodes = sorted(nodes, key=eu.sort_by('created'))
    # nodes = { 'nodes': [{'node': node_data} for node_data in nodes] }
    
    # 4. extract the comments from the tweets
    comments = et.extract.extract_comments(tweets)
    sorted_comments = sorted(comments, key=eu.sort_by('created'))
    # comments = { 'comments': [{'comment': comment_data} for comment_data in comments] }
    
    # 5. saves the files
    write_file(tweets, 'tweets.json', outdir)
    write_file(sorted_users, 'users.json', outdir)
    write_file(sorted_nodes, 'nodes.json', outdir)
    write_file(sorted_comments, 'comments.json', outdir)
    logging.info("Parsing tweets - Completed")

if __name__ == "__main__":
   main(sys.argv[1:])

