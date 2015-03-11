import os, sys
import json
import csv
from datetime import datetime
import time
import logging
from functools import partial

from edgesense.utils.logger_initializer import initialize_logger
import edgesense.utils as eu
import edgesense.catalyst as ec
from edgesense.metrics import calculate_network_metrics

def write_file(elements, name, destination_path):
    # dump the network to a json file, formatted
    eu.resource.save(elements, name, destination_path, True)
    logging.info("Parsing catalyst - Saved: %(d)s/%(n)s" % {'d':destination_path, 'n':name})

def parse_options(argv):
    import getopt
    # defaults
    source = None
    kind = 'both'
    moderator = None
    timestep_size = 60*60*24*7
    timestep_window = 1
    timestep_count = None
    create_datapackage = False
    license_type = None
    license_url = None
    datapackage_title = None
    destination_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "json"))

    try:
        opts, args = getopt.getopt(argv,"k:s:o:m:",["kind=","source-json=","output-directory=","moderator="])
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
        elif opt in ("-o", "--output-directory"):
           destination_path = arg
        elif opt in ("-m", "--moderator"):
           moderator = arg
        elif opt in ("-s", "--timestep-size"):
           timestep_size = int(arg)
        elif opt in ("-w", "--timestep-window"):
           timestep_window = int(arg)
        elif opt in ("-f", "--timestep-count"):
           timestep_count = int(arg)
        elif opt in ("--datapackage-license-type"):
           license_type = arg
        elif opt in ("--datapackage-license-url"):
           license_url = arg
        elif opt in ("--datapackage-title"):
           datapackage_title = arg

    if license_type and license_url:
        create_datapackage = True

    logging.info("parsing url %(s)s" % {'s': source})
    return (kind, source, destination_path, moderator, timestep_size, timestep_window, timestep_count,
            create_datapackage, license_type, license_url, datapackage_title)

def main():
    initialize_logger('./log')
    
    generated = datetime.now()
    kind, source, destination_path, moderator, timestep_size, timestep_window, timestep_count, create_datapackage, license_type, license_url, datapackage_title = parse_options(sys.argv[1:])
    logging.info("Parsing catalyst - Started")
    logging.info("Parsing catalyst - Source file: %(s)s" % {'s':source})
    logging.info("Parsing catalyst - Output directory: %(s)s" % {'s':destination_path})
    logging.info("Parsing catalyst - Extraction Kind: %(s)s" % {'s':kind})
    
    # 1. load and parse the JSON file into a RDF Graph
    
    graph = ec.inference.catalyst_graph_for(source)
    
    # 2. extract the usersnodes,comments from the graph
    use_posts = (kind == 'posts') or (kind == 'both')
    use_ideas = (kind == 'ideas') or (kind == 'both')
    assert use_ideas or use_posts, "kind must be ideas, posts or both"
    moderator_test = None
    if moderator:
        moderator_test = partial(ec.extract.is_moderator, graph, moderator_roles=(moderator,))
    network = ec.extract.ideas.graph_to_network(generated, graph, use_ideas, use_posts, moderator_test)
    
    directed_multiedge_network = calculate_network_metrics({}, {}, {}, network, timestep_size, timestep_window, timestep_count)
    
    eu.resource.write_network(network, \
                     directed_multiedge_network, \
                     generated, \
                     create_datapackage, \
                     datapackage_title, \
                     license_type, \
                     license_url, \
                     destination_path)

    logging.info("Parsing catalyst - Completed")

if __name__ == "__main__":
   main()

