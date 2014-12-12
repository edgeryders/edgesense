# requires flask and flask-cors
import os, sys, urlparse
import json
from datetime import datetime
import time
import logging
import networkx as nx

from edgesense.utils.logger_initializer import initialize_logger
import edgesense.utils as eu
import edgesense.catalyst as ec
from edgesense.network.utils import extract_edges, build_network
from edgesense.metrics import compute_all_metrics
from edgesense.utils.extract import calculate_timestamp_range

from flask import Flask
from flask import request
from flask import jsonify
from flask.ext.cors import CORS, cross_origin


def parse_cif(source, kind):
    logging.info("parse_source - Started")
    logging.info("parse_source - Source: %(s)s" % {'s':source})
    logging.info("parse_source - Extraction Kind: %(s)s" % {'s':kind})
    
    # 1. load and parse the JSON file into a RDF Graph    
    graph = ec.inference.catalyst_graph_for(source)
    
    # 2. extract the usersnodes,comments from the graph
    if kind == 'simple':
        users,nodes,comments = ec.extract.simple.users_nodes_comments_from(graph)
    elif kind == 'excerpts':
        users,nodes,comments = ec.extract.excerpts.users_nodes_comments_from(graph)
    else:
        logging.info("Parsing catalyst - Extraction kind not supported")
        return
        
    # 3. sort the lists
    sorted_users = sorted(users, key=eu.sort_by('created'))
    sorted_nodes = sorted(nodes, key=eu.sort_by('created'))
    sorted_comments = sorted(comments, key=eu.sort_by('created'))
    
    # 4. return the data
    logging.info("Parsing catalyst - Completed")
    return (sorted_users, sorted_nodes, sorted_comments)
   
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

basepath = os.path.dirname(__file__)
static_path = os.path.abspath(os.path.join(basepath, "..", "static"))
app = Flask(__name__, static_folder=static_path, static_url_path='')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
    
@app.route("/")
def index():
    return ""

@app.route("/parse", methods=['GET','POST'])
def parse():
    node_title_field = 'uid'
    timestep_size = 60*60*24*7
    timestep_window = 1
    timestep_count = 20
    username = None
    password = None
    extraction_method = 'nested'
    admin_roles = set()
    exclude_isolated = False
    generated = datetime.now()
    
    source_json = request.form['source'] if request.form.has_key('source') else None
    if not source_json:
        raise InvalidUsage('Missing parameters', status_code=400)
    
    # Download the remote URL
    users, nodes, comments = parse_cif(source_json, 'simple')

    # extract a normalized set of data
    nodes_map, posts_map, comments_map = eu.extract.normalized_data(users, nodes, comments, node_title_field, admin_roles, exclude_isolated)

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
    
    # save the results
    tag = generated.strftime('%Y-%m-%d-%H-%M-%S')
    destination_path = os.path.abspath(os.path.join(static_path, "json"))
    tagged_dir = os.path.join(destination_path, "data", tag)

    # dump the network to a json file, minified
    eu.resource.save(network, 'network.min.json', tagged_dir)
    logging.info("network dumped")  
    
    # dump the gexf file
    gexf_file = os.path.join(tagged_dir, 'network.gexf')
    eu.gexf.save_gexf(directed_multiedge_network, gexf_file)
    
    # return the result URL
    base_path = os.path.join("/json/data", tag)
    result_path = os.path.join(base_path, "network.min.json")
    
    logging.info("Completed: %(s)s" % {'s':result_path})  
    return jsonify({'last': tag, 'base_path': base_path, 'metrics': 'network.min.json', 'gexf': 'network.gexf' })


if __name__ == "__main__":
    initialize_logger('./log')
    app.run(debug=True)