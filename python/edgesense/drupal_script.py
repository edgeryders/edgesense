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
from edgesense.network.utils import extract_edges, build_network
from edgesense.metrics import compute_all_metrics
from edgesense.utils.extract import calculate_timestamp_range

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
    users_resource = 'users.json'
    nodes_resource = 'nodes.json'
    comments_resource = 'comments.json'
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
    basepath = os.path.dirname(__file__)
    destination_path = os.path.abspath(os.path.join(basepath, "..", "static", "json"))
    log_path = './log'
    create_datapackage = False
    datapackage_title = None
    license_type = None
    license_url = None
    site_url = None
    
    data = {}            
    try:
        with open(argv[0], 'r') as datafile:
            data = json.load(datafile)
    except:
        print 'Error reading the parameters file'
        sys.exit(2)
    
    if not(data):
           print 'edgesense_drupal <path to the parameters file>'
           sys.exit()

    if data.has_key('users') and data['users']:
     users_resource = data['users']
    
    if data.has_key('nodes') and data['nodes']:
     nodes_resource = data['nodes']
    
    if data.has_key('comments') and data['comments']:
     comments_resource = data['comments']
    
    if data.has_key('node_title') and data['node_title']:
     node_title_field = data['node_title']
    
    if data.has_key('timestep_size') and data['timestep_size']:
     timestep_size = int(data['timestep_size'])
    
    if data.has_key('count_window') and data['count_window']:
     timestep_window = int(data['count_window'])
    
    if data.has_key('timestep_count') and data['timestep_count']:
     timestep_count = int(data['timestep_count'])
    
    if data.has_key('auth'):
     try:
         username = data['auth']['username']
     except:
         username = None
     try:
         password = data['auth']['password']
     except:
         password = None
         
    if data.has_key('extraction_method') and data['extraction_method']:
     extraction_method = data['extraction_method']
    
    if data.has_key('moderator_roles') and data['moderator_roles']:
     admin_roles = set([e.strip() for e in data['moderator_roles'].split(",") if e.strip()])
    
    if data.has_key('exclude_isolated') and data['exclude_isolated']:
     exclude_isolated = True
    
    if data.has_key('dumpto') and data['dumpto']:
       dumpto = data['extraction_method']
    
    if data.has_key('destination_path') and data['destination_path']:
       destination_path = data['destination_path']
    
    if data.has_key('log_path') and data['log_path']:
       log_path = os.path.join(data['log_path'])
           
    if data.has_key('datapackage'):
     try:
         license_type = data['datapackage']['license_type']
         license_url = data['datapackage']['license_url']
         if data['datapackage'].has_key('title'):
             datapackage_title = data['datapackage']['title']
         site_url = data['datapackage']['site_url']
         create_datapackage = True
     except:
         license_type = None
         license_url = None
         site_url = None
         create_datapackage = True

    # set up logging to file (edgesense.log in the same dir as the parameters file)
    initialize_logger(log_path, file_level=logging.DEBUG, console_level=logging.DEBUG, file_mode='w')

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
            destination_path,
            create_datapackage,
            datapackage_title,
            license_type,
            license_url,
            site_url)

def main():
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
    destination_path, \
    create_datapackage, \
    datapackage_title, \
    license_type, \
    license_url, \
    site_url = parse_options(sys.argv[1:])
    
    generated = datetime.now()
    
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

    # filter out nodes that have not participated to the full:conversations
    inactive_nodes = [ v for v in nodes_map.values() if not v['active'] ]
    logging.info("inactive nodes: %(n)i" % {'n':len(inactive_nodes)})
    network['nodes'] = [ v for v in nodes_map.values() if v['active'] ]
    
    # Parameters    
    timestep, timesteps_range = calculate_timestamp_range(network, timestep_size, timestep_window, timestep_count)
    
    # build the whole network to use for metrics
    directed_multiedge_network=build_network(network)    
    logging.info("network built")  

    # calculate the metrics
    network['metrics'] = compute_all_metrics(nodes_map, posts_map, comments_map, directed_multiedge_network, timesteps_range, timestep, timestep_window)
    logging.info("network metrics done")  
    
    tag = generated.strftime('%Y-%m-%d-%H-%M-%S')
    tagged_dir = os.path.join(destination_path, 'data', tag)

    # dump the network to a json file, minified
    eu.resource.save(network, 'network.min.json', tagged_dir)
    logging.info("network dumped")  
    
    # create the datapackage
    if create_datapackage:
        try:
            # load the datapackage template
            basepath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))        
            with open(os.path.join(basepath, "datapackage_template.json"), 'r') as datafile:
                datapackage = json.load(datafile)
                datapackage['license'] = {'type': license_type, 'url': license_url}
                if datapackage_title:
                    datapackage['title'] = datapackage_title
                datapackage['last_updated'] = generated.strftime('%Y-%m-%dT%H:%M:%S')
                datapackage['resources'][0]['url'] = site_url
                datapackage['resources'][0]['path'] = os.path.join('data', tag, 'network.gexf')

                # dump the gexf file
                gexf_file = os.path.join(tagged_dir, 'network.gexf')
                eu.gexf.save_gexf(directed_multiedge_network, gexf_file)
                # dump the datapackage
                eu.resource.save(datapackage, 'datapackage.json', destination_path, True)
                logging.info("datapackage saved")  
        except:
            logging.error("Error reading the datapackage template")
            create_datapackage = False
    
    eu.resource.save({'last': tag, 'datapackage': create_datapackage}, 'last.json', destination_path)
    
    logging.info("Completed")  

if __name__ == "__main__":
   main()

