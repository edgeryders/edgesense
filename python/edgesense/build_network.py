# This program rearranges raw Egderyders data and builds two lists of dicts, userlist and ciommentslist, containing 
# of the data needed to buildm graphs. These objects are then saved into files.
import os, sys
import json
import csv
from datetime import datetime
import time
import networkx as nx
import logging

import edgesense.utils as eu
from edgesense.utils.logger_initializer import initialize_logger
from edgesense.network.utils import extract_edges, extract_multiauthor_post_edges, build_network
from edgesense.metrics import calculate_network_metrics

def load_files(users_resource, nodes_resource, comments_resource, username, password, extraction_method, dumpto, generated):
    if dumpto:
        base_dump_dir = os.path.join(dumpto, generated.strftime('%Y-%m-%d-%H-%M-%S'))
        eu.resource.mkdir(base_dump_dir)
    
    # load users
    if dumpto:
        dump_to = os.path.join(base_dump_dir, 'users.json')
    else:
        dump_to = None
    jusers = eu.resource.load(users_resource, username=username, password=password, dump_to=dump_to)
    allusers = eu.extract.extract(extraction_method, 'users', jusers)

    # load nodes
    if dumpto:
        dump_to = os.path.join(base_dump_dir, 'nodes.json')
    else:
        dump_to = None
    jnodes = eu.resource.load(nodes_resource, username=username, password=password, dump_to=dump_to)
    allnodes = eu.extract.extract(extraction_method, 'nodes', jnodes)

    # load comments
    if dumpto:
        dump_to = os.path.join(base_dump_dir, 'comments.json')
    else:
        dump_to = None
    jcomments = eu.resource.load(comments_resource, username=username, password=password, dump_to=dump_to)
    allcomments = eu.extract.extract(extraction_method, 'comments', jcomments)

    logging.info("file loaded")
    return (allusers,allnodes,allcomments)
    
def parse_options(argv):
    import getopt
    # defaults
    try:
        source_path = os.environ['EDGESENSE_SOURCE_DIR']
    except KeyError:
        source_path = ''
    users_resource = source_path + 'users.json'
    nodes_resource = source_path + 'nodes.json'
    comments_resource = source_path + 'comments.json'
    node_title_field = 'uid'
    timestep_size = 60*60*24*7
    timestep_window = 1
    timestep_count = None
    username = None
    password = None
    extraction_method = 'nested'
    admin_roles = set()
    exclude_isolated = False
    dumpto = None
    create_datapackage = False
    license_type = None
    license_url = None
    datapackage_title = None
    destination_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "json"))

    try:
        opts, args = getopt.getopt(argv,"hu:n:c:t:s:w:f:o:",["users=","nodes=","comments=", "node-title=", "timestep-size=", "timestep-window=", "timestep-count=", "output-directory=", "username=", "password=", "extraction-method=", "admin-roles=", "exclude-isolated", "datapackage-license-type=", "datapackage-license-url=", "datapackage-title=", "dumpto="])
    except getopt.GetoptError:
        print 'build_network.py -u <users_resource> -n <nodes_resource> -c <comments_resource> -t <node title field> -s <timestep in seconds> -w <timestep window> -f <timestep count> -o <output directory>'
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
           print 'build_network.py -u <users_resource> -n <nodes_resource> -c <comments_resource> -t <node title field> -s <timestep in seconds> -w <timestep window> -f <timestep count> -o <output directory> --username="<http basic auth user>" --password="<http basic auth password>" --admin-roles="<comma separated list of roles marking a user as part of the community team>" --exclude-isolated --datapackage-license-type="<license name for the datapackage>" --datapackage-license-url="<license url for the datapackage>" --datapackage-title="<title for the datapackage>" --dumpto="<where to save the downloaded file>"' 
           sys.exit()
        elif opt in ("-u", "--users"):
           users_resource = arg
        elif opt in ("-n", "--nodes"):
           nodes_resource = arg
        elif opt in ("-c", "--comments"):
           comments_resource = arg
        elif opt in ("-t", "--node-title"):
           node_title_field = arg
        elif opt in ("-s", "--timestep-size"):
           timestep_size = int(arg)
        elif opt in ("-w", "--timestep-window"):
           timestep_window = int(arg)
        elif opt in ("-f", "--timestep-count"):
           timestep_count = int(arg)
        elif opt in ("-o", "--output-directory"):
           destination_path = arg
        elif opt in ("--username"):
           username = arg
        elif opt in ("--password"):
           password = arg
        elif opt in ("--extraction-method"):
           extraction_method = arg
        elif opt in ("--admin-roles"):
           admin_roles = set([e.strip() for e in arg.split(",") if e.strip()])
        elif opt in ("--exclude-isolated"):
           exclude_isolated = True
        elif opt in ("--dumpto"):
           dumpto = arg
        elif opt in ("--datapackage-license-type"):
           license_type = arg
        elif opt in ("--datapackage-license-url"):
           license_url = arg
        elif opt in ("--datapackage-title"):
           datapackage_title = arg
    
    if license_type and license_url:
        create_datapackage = True
      
    logging.info("parsing files %(u)s %(n)s %(c)s" % {'u': users_resource, 'n': nodes_resource, 'c': comments_resource})       
    return (users_resource, 
            nodes_resource,
            comments_resource,
            node_title_field,
            timestep_size,
            timestep_window,
            timestep_count,
            username, password,
            extraction_method,
            admin_roles,
            exclude_isolated,
            dumpto,
            create_datapackage,
            datapackage_title,
            license_type,
            license_url,
            destination_path)

def main():
    initialize_logger('./log')
    generated = datetime.now()
    
    users_resource, \
    nodes_resource, \
    comments_resource, \
    node_title_field, \
    timestep_size, \
    timestep_window, \
    timestep_count, \
    username, \
    password, \
    extraction_method, \
    admin_roles, \
    exclude_isolated, \
    dumpto, \
    create_datapackage, \
    datapackage_title, \
    license_type, \
    license_url, \
    destination_path = parse_options(sys.argv[1:])
    
    logging.info("Network processing - started")
    
    # Load the files
    allusers, allnodes, allcomments = load_files(users_resource, nodes_resource, comments_resource, username, password, extraction_method, dumpto, generated)
    
    # extract a normalized set of data
    nodes_map, posts_map, comments_map = eu.extract.normalized_data(allusers, allnodes, allcomments, node_title_field, admin_roles, exclude_isolated)

    # this is the network object
    # going forward it should be read from a serialized format to handle caching
    network = {}

    # Add some file metadata
    network['meta'] = {}
    # Timestamp of the file generation (to show in the dashboard)
    network['meta']['generated'] = int(generated.strftime("%s"))
        
    network['edges'] = extract_edges(nodes_map, comments_map)
    network['edges'] += extract_multiauthor_post_edges(nodes_map, posts_map)

    # filter out nodes that have not participated to the full:conversations
    inactive_nodes = [ v for v in nodes_map.values() if not v['active'] ]
    logging.info("inactive nodes: %(n)i" % {'n':len(inactive_nodes)})
    network['nodes'] = [ v for v in nodes_map.values() if v['active'] ]
    
    directed_multiedge_network = calculate_network_metrics(nodes_map, posts_map, comments_map, network, timestep_size, timestep_window, timestep_count)
    
    eu.resource.write_network(network, \
                     directed_multiedge_network, \
                     generated, \
                     create_datapackage, \
                     datapackage_title, \
                     license_type, \
                     license_url, \
                     destination_path)
    
    logging.info("Completed")  

if __name__ == "__main__":
   main()

