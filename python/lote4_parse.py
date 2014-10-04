import os, sys
import json
import csv
from datetime import datetime
import time
import logging

from edgesense.utils.logger_initializer import initialize_logger
from edgesense.network.utils import sort_by
import edgesense.utils as eu
import edgesense.twitter as et

def write_file(elements, name, destination_path):
    # dump the network to a json file, formatted
    eu.resource.save(elements, name, destination_path, True)
    logging.info("file %(s)s saved" % {'s': name})  

def parse_options(argv):
    import getopt
    # defaults
    source = None
    outdir = '.'
    
    try:
        opts, args = getopt.getopt(argv,"s:o:",["source=","outdir="])
    except getopt.GetoptError:
        logging.error('lote4_parser.py -s <source url> -o <output directory>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
           logging.info('lote4_parser.py -s <source url> -o <output directory>')
           sys.exit()
        elif opt in ("-s", "--source"):
           source = arg
        elif opt in ("-o", "--outdir"):
           outdir = arg
           
    logging.info("parsing url %(s)s" % {'s': source})
    return (source,outdir)

def main(argv):
    initialize_logger('./log')
    
    generated = datetime.now()
    source, outdir = parse_options(argv)
    logging.info("LOTE4 tweets - Started")
    
    # 1. download the remote CSV file
    # 2. parse the CSV file into a list of records
    raw_tweets = eu.resource.load_csv(source)
    tweets = [et.extract.map_data(t) for t in raw_tweets]
    sorted_tweets = sorted(tweets, key=sort_by('created_ts'))
    
    # 3. extract the users from the tweets
    users = et.extract.extract_users(tweets)
    sorted_users = sorted(users, key=sort_by('created'))
    # users = { 'users': [{'user': user_data} for user_data in users] }

    # 4. extract the nodes from the tweets
    nodes = et.extract.extract_nodes(tweets)
    sorted_nodes = sorted(nodes, key=sort_by('created'))
    # nodes = { 'nodes': [{'node': node_data} for node_data in nodes] }
    
    # 5. extract the comments from the tweets
    comments = et.extract.extract_comments(tweets)
    sorted_comments = sorted(comments, key=sort_by('created'))
    # comments = { 'comments': [{'comment': comment_data} for comment_data in comments] }
    
    # 6. save the files
    write_file(sorted_tweets, 'tweets.json', outdir)
    write_file(sorted_users, 'users.json', outdir)
    write_file(sorted_nodes, 'nodes.json', outdir)
    write_file(sorted_comments, 'comments.json', outdir)
    logging.info("LOTE4 tweets - Completed")

if __name__ == "__main__":
   main(sys.argv[1:])

