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
from edgesense.metrics import calculate_network_metrics

from flask import Flask
from flask import request
from flask import jsonify
from flask.ext.cors import CORS, cross_origin

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
static_path = os.path.abspath(os.path.join(basepath, "..", "..", "static"))
destination_path = os.path.abspath(os.path.join(static_path, "json"))
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
    create_datapackage = False 
    license_type = None
    license_url = None
    datapackage_title = None
    kind = 'both'
    moderator = None
    generated = datetime.now()
    
    source_json = request.form['source'] if request.form.has_key('source') else None
    if not source_json:
        raise InvalidUsage('Missing parameters', status_code=400)
    
    initialize_logger('./log')
    
    logging.info("parse_source - Started")
    logging.info("parse_source - Source: %(s)s" % {'s':source_json})
    logging.info("parse_source - Extraction Kind: %(s)s" % {'s':kind})
    
    # 1. load and parse the JSON file into a RDF Graph    
    graph = ec.inference.catalyst_graph_for(source_json)
    
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

    # return the result URL
    tag = generated.strftime('%Y-%m-%d-%H-%M-%S')
    base_path = os.path.join("/json/data", tag)
    result_path = os.path.join(base_path, "network.min.json")
    
    logging.info("Completed: %(s)s" % {'s':result_path})
    return jsonify({'last': tag, 'base_path': base_path, 'metrics': 'network.min.json', 'gexf': 'network.gexf', 'datapackage': 'datapackage.json' })



def main(debug=False):
    initialize_logger('./log')
    app.run(debug=debug, host=(None if debug else '0.0.0.0'))


if __name__ == "__main__":
    main(True)
