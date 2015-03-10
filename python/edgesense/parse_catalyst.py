import os, sys
import json
import csv
from datetime import datetime
import time
import logging

from edgesense.utils.logger_initializer import initialize_logger
import edgesense.utils as eu
import edgesense.catalyst as ec

def write_file(elements, name, destination_path):
    # dump the network to a json file, formatted
    eu.resource.save(elements, name, destination_path, True)
    logging.info("Parsing catalyst - Saved: %(d)s/%(n)s" % {'d':destination_path, 'n':name})

def parse_options(argv):
    import getopt
    # defaults
    source = None
    outdir = '.'
    kind = 'both'
    
    try:
        opts, args = getopt.getopt(argv,"k:s:o:",["kind=","source-json=","outdir="])
    except getopt.GetoptError:
        logging.error('parse_catalyst.py -k <extraction kind (simple)> -s <source JSON> -o <output directory> ')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
           logging.info('parse_catalyst.py -k <extraction kind (simple)> -s <source JSON> -o <output directory> ')
           sys.exit()
        elif opt in ("-k", "--kind"):
           kind = arg
        elif opt in ("-s", "--source-json"):
           source = arg
        elif opt in ("-o", "--outdir"):
           outdir = arg
           
    logging.info("parsing url %(s)s" % {'s': source})
    return (kind,source,outdir)

def main():
    initialize_logger('./log')
    
    generated = datetime.now()
    kind, source, outdir = parse_options(sys.argv[1:])
    logging.info("Parsing catalyst - Started")
    logging.info("Parsing catalyst - Source file: %(s)s" % {'s':source})
    logging.info("Parsing catalyst - Output directory: %(s)s" % {'s':outdir})
    logging.info("Parsing catalyst - Extraction Kind: %(s)s" % {'s':kind})
    
    # 1. load and parse the JSON file into a RDF Graph
    
    graph = ec.inference.catalyst_graph_for(source)
    
    # 2. extract the usersnodes,comments from the graph
    use_posts = (kind == 'posts') or (kind == 'both')
    use_ideas = (kind == 'ideas') or (kind == 'both')
    assert use_ideas or use_posts, "kind must be ideas, posts or both"
    nodes, edges = ec.extract.ideas.graph_to_network(graph, use_ideas, use_posts)
    # 3. sort the lists
    nodes.sort(key=eu.sort_by('created'))
    edges.sort(key=eu.sort_by('created'))
    # 4. saves the files
    write_file(nodes, 'nodes.json', outdir)
    write_file(edges, 'edges.json', outdir)

    logging.info("Parsing catalyst - Completed")

if __name__ == "__main__":
   main()

