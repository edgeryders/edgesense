# This program rearranges raw Egderyders data and builds two lists of dicts, userlist and ciommentslist, containing 
# of the data needed to buildm graphs. These objects are then saved into files.
import os, sys
import json
import csv
from datetime import datetime
import time
import networkx as nx
import logging

from edgesense.utils.logger_initializer import initialize_logger
import edgesense.utils as eu
import edgesense.network as en

def build(allusers, allnodes, allcomments, timestamp, node_title_field='uid', timestep_size=60*60*24*7, timestep_window=1, timestep_count=None, admin_roles=set(), exclude_isolated=False):
    # this is the network object
    # going forward it should be read from a serialized format to handle caching
    network = {}

    # Add some file metadata
    network['meta'] = {}
    # Timestamp of the file generation (to show in the dashboard)
    network['meta']['generated'] = int(timestamp.strftime("%s"))
    
    nodes_map, posts_map, comments_map = eu.extract.normalized_data(allusers, allnodes, allcomments, node_title_field, admin_roles, exclude_isolated)
    # build a mapping of nodes (users) keyed on their id

    network['nodes'] = nodes_map

    # build the whole network to dump on json
    links_list = []
    # a comment is 'valid' if it has a recipient and an author
    valid_comments = [e for e in comments_map.values() if e.get('recipient_id', None) and e.get('author_id', None)]
    logging.info("%(v)i valid comments on %(t)i total" % {'v':len(valid_comments), 't':len(comments_map.values())})
    
    # build the whole network to use for metrics
    for comment in valid_comments:
        link = {
            'id': "{0}_{1}_{2}".format(comment['author_id'],comment['recipient_id'],comment['created_ts']),
            'source': comment['author_id'],
            'target': comment['recipient_id'],
            'ts': comment['created_ts'],
            'effort': comment['length'],
            'team': comment['team']
        }
        if nodes_map.has_key(comment['author_id']):
            nodes_map[comment['author_id']]['active'] = True
        else:
            logging.info("error: node %(n)s was linked but not found in the nodes_map" % {'n':comment['author_id']})  
    
        if nodes_map.has_key(comment['recipient_id']):
            nodes_map[comment['recipient_id']]['active'] = True
        else:
            logging.info("error: node %(n)s was linked but not found in the nodes_map" % {'n':comment['recipient_id']})  
        links_list.append(link)


    network['edges'] = sorted(links_list, key=en.utils.sort_by('ts'))

    # filter out nodes that have not participated to the full:conversations
    inactive_nodes = []
    for node_id in nodes_map.keys():
        if not nodes_map[node_id]['active']:
            inactive_nodes.append(nodes_map.pop(node_id, None))

    logging.info("inactive nodes: %(n)i" % {'n':len(inactive_nodes)})  
    network['nodes'] = nodes_map

    # Parameters
    start_ts = network['edges'][0]['ts'] # first timestamp in the edges
    end_ts = network['edges'][-1]['ts'] # last timestamp in the edges
    day_ts = 60*60*24
    if timestep_count:
        timestep = max(int(round((end_ts-start_ts)/timestep_count)), day_ts)
    else:
        timestep = timestep_size
    
    timesteps_range = range(start_ts, end_ts, timestep)
    if timesteps_range[-1]<end_ts :
        timesteps_range.append(end_ts)
    
    metrics = {}
    # calculate content metrics
    # For each timestep:
    for ts in timesteps_range:
        ts_metrics = {
            'ts': ts,
            'full:users_count':0., # Number of Posts total
            'user:users_count':0., # Number of Posts total
            'team:users_count':0., # Number of Posts total
            'full:posts_count':0., # Number of Posts total
            'user:posts_count':0., #  - Number of Posts by contributors
            'team:posts_count':0., #  - Number of Posts by team
            'user:posts_share':0., #  - Share of User Generated Posts
            'user:team_posts_share':0., #  - Share of Team/User  Posts
            'full:ts_posts_count': 0.,  #  - Number of Posts in period
            'user:ts_posts_count':0., #  - Number of Posts by contributors in period
            'team:ts_posts_count':0., #  - Number of Posts by team in period
            'user:ts_posts_share': 0., #  - Share of User Generated Posts in period
            'user:ts_team_posts_share': 0., #  - Share of Team/User  Posts in period
            'full:comments_count':0., #  - Number of Comments total
            'user:comments_count': 0., #  - Number of Comments by contributors
            'team:comments_count': 0., #  - Number of Comments by team
            'user:comments_share': 0., #  - Share of Team/User Generated Comments
            'user:team_comments_share': 0., #  - Share of User Generated Comments
            'full:ts_comments_count':0., #  - Number of Comments total in period
            'user:ts_comments_count':0., #  - Number of Comments by contributors in period
            'team:ts_comments_count':0., #  - Number of Comments by contributors in period
            'user:ts_comments_share': 0., #  - Share of User Generated Comments in period
            'user:ts_team_comments_share': 0., #  - Share of Team/User Generated Comments in period
            'user:active_count': 0.,
            'user:noteam_active_count': 0.,
            'user:active_share': 0.,
            'user:conversations': 0.,
            'user:noteam_conversations': 0.,
            'user:conversations_share': 0.
        }
        # Users count metrics
        for u in allusers:
            if int(u['created'])<=ts:
                ts_metrics['full:users_count'] += 1
                if eu.extract.is_team(u, admin_roles):
                    ts_metrics['team:users_count'] += 1
                else:
                    ts_metrics['user:users_count'] += 1
        
        # Posts Count metrics
        for p in posts_map.values():
            if p['created_ts']<=ts:
                ts_metrics['full:posts_count'] += 1
                if p['team']:
                    ts_metrics['team:posts_count'] += 1
                else:
                    ts_metrics['user:posts_count'] += 1
            if p['created_ts']<=ts and p['created_ts']>=ts-timestep*timestep_window:
                ts_metrics['full:ts_posts_count'] += 1
                if p['team']:
                    ts_metrics['team:ts_posts_count'] += 1
                else:
                    ts_metrics['user:ts_posts_count'] += 1
        if ts_metrics['full:posts_count'] > 0:
            ts_metrics['user:posts_share'] = float(ts_metrics['user:posts_count'])/float(ts_metrics['full:posts_count'])    
        if ts_metrics['user:posts_count'] > 0:
            ts_metrics['user:team_posts_share'] = float(ts_metrics['team:posts_count'])/float(ts_metrics['user:posts_count'])    
        if ts_metrics['full:ts_posts_count'] > 0:
            ts_metrics['user:ts_posts_share'] = float(ts_metrics['user:ts_posts_count'])/float(ts_metrics['full:ts_posts_count'])
        if ts_metrics['user:ts_posts_count'] > 0:
            ts_metrics['user:ts_team_posts_share'] = float(ts_metrics['team:ts_posts_count'])/float(ts_metrics['user:ts_posts_count'])
    
        # Comments Count metrics
        for c in comments_map.values():
            if c['created_ts']<=ts:
                ts_metrics['full:comments_count'] += 1
                if c['team']:
                    ts_metrics['team:comments_count'] += 1
                else:
                    ts_metrics['user:comments_count'] += 1
            if c['created_ts']<=ts and c['created_ts']>=ts-timestep*timestep_window:
                ts_metrics['full:ts_comments_count'] += 1
                if c['team']:
                    ts_metrics['team:ts_comments_count'] += 1
                else:
                    ts_metrics['user:ts_comments_count'] += 1
        if ts_metrics['full:comments_count'] > 0:
            ts_metrics['user:comments_share'] = float(ts_metrics['user:comments_count'])/float(ts_metrics['full:comments_count'])
        if ts_metrics['user:comments_count'] > 0:
            ts_metrics['user:team_comments_share'] = float(ts_metrics['team:comments_count'])/float(ts_metrics['user:comments_count'])
        if ts_metrics['full:ts_comments_count'] > 0:
            ts_metrics['user:ts_comments_share'] = float(ts_metrics['user:ts_comments_count'])/float(ts_metrics['full:ts_comments_count'])
        if ts_metrics['user:ts_comments_count'] > 0:
            ts_metrics['user:ts_team_comments_share'] = float(ts_metrics['team:ts_comments_count'])/float(ts_metrics['user:ts_comments_count'])
    
        #  - User counts
        actives = set()
        noteam_actives = set()
        conversations = set()
        noteam_conversations = set()
        for c in comments_map.values():
            if c['created_ts']<=ts and nodes_map.has_key(c['author_id']) and nodes_map.has_key(c['recipient_id']):
                a = nodes_map[c['author_id']]
                r = nodes_map[c['recipient_id']]
                cnv = '-'.join(sorted([c['author_id'], c['recipient_id']]))
                if not (a['team'] and a['team_ts'] <=ts):
                    actives.add(c['author_id'])
                    conversations.add(cnv)
                    if not (r['team'] and r['team_ts'] <=ts):
                        noteam_actives.add(c['recipient_id'])
                        noteam_conversations.add(cnv)
        ts_metrics['user:active_count'] = len(actives)
        ts_metrics['user:noteam_active_count'] = len(noteam_actives)
        if ts_metrics['user:active_count'] > 0:
            ts_metrics['user:active_share'] = float(ts_metrics['user:noteam_active_count'])/float(ts_metrics['user:active_count'])    
        ts_metrics['user:conversations'] = len(conversations)
        ts_metrics['user:noteam_conversations'] = len(noteam_conversations)
        if ts_metrics['user:conversations'] > 0:
            ts_metrics['user:conversations_share'] = float(ts_metrics['user:noteam_conversations'])/float(ts_metrics['user:conversations'])
    
        metrics[ts] = ts_metrics

    logging.info("content metrics done")  

    # build the whole network to use for metrics
    MDG=nx.MultiDiGraph()

    for node in network['nodes'].values():
        MDG.add_node(node['id'], node)

    for edge in network['edges']:
        MDG.add_edge(edge['source'], edge['target'], attr_dict=edge)
    
    en.metrics.set_isolated(nodes_map, MDG)
    
    logging.info("network built")  

    
    for ts in timesteps_range:
        ts_metrics = metrics[ts]
        # all metrics
        ts_metrics.update(en.metrics.extract_network_metrics(MDG, ts))
        if ts_metrics.has_key('full:partitions'):
            ts_metrics['partitions'] = ts_metrics['full:partitions']
        else:
            ts_metrics['partitions'] = None
        ts_metrics.update(en.metrics.extract_network_metrics(MDG, ts, team=False))
    
    network['metrics'] = sorted(metrics.values(), key=en.utils.sort_by('ts'))
    logging.info("network metrics done")  

    # add the nodes as an array
    network['nodes'] = nodes_map.values()
    
    return network
    

def write_network(network, timestamp):
    tag = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
    basepath = os.path.dirname(__file__)
    destination_path = os.path.abspath(os.path.join(basepath, "..", "static", "json"))
    tagged_dir = os.path.join(destination_path, "data", tag)

    # dump the network to a json file, minified
    eu.resource.save(network, 'network.min.json', tagged_dir)
    logging.info("network dumped")  

    # dump the network to a json file, formatted
    eu.resource.save(network, 'network.json', tagged_dir, True)
    logging.info("network large dumped")  

    # dump the metrics and the network to separate files:
    metrics = network.pop('metrics', None)
    eu.resource.save(network, 'network-no-metrics.min.json', tagged_dir)
    eu.resource.save(metrics, 'metrics.min.json', tagged_dir)
    logging.info("network+metrics dumped")  

    eu.resource.save({'last': tag}, 'last.json', destination_path)

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
    try:
        opts, args = getopt.getopt(argv,"hu:n:c:t:s:w:f:",["users=","nodes=","comments=", "node-title=", "timestep-size=", "timestep-window=", "timestep-count=", "username=", "password=", "extraction-method=", "admin-roles=", "exclude-isolated"])
    except getopt.GetoptError:
        print 'build_network.py -u <users_resource> -n <nodes_resource> -c <comments_resource> -t <node title field> -s <timestep in seconds> -w <timestep window> -f <timestep count>'
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
           print 'build_network.py -u <users_resource> -n <nodes_resource> -c <comments_resource> -t <node title field> -s <timestep in seconds> -w <timestep window> -f <timestep count> --username="<http basic auth user>" --password="<http basic auth password>" --admin-roles="<comma separated list of roles marking a user as part of the community team>" --exclude-isolated' 
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
           
    logging.info("parsing files %(u)s %(n)s %(c)s" % {'u': users_resource, 'n': nodes_resource, 'c': comments_resource})       
    return (users_resource,nodes_resource,comments_resource, node_title_field, timestep_size, timestep_window, timestep_count, username, password, extraction_method, admin_roles, exclude_isolated)

def main(argv):
    initialize_logger('./log')

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
    exclude_isolated = parse_options(argv)
    
    logging.info("Network processing - started")  
    # load users
    jusers = eu.resource.load(users_resource, username=username, password=password)
    allusers = eu.extract.extract(extraction_method, 'users', jusers)

    # load nodes
    jnodes = eu.resource.load(nodes_resource, username=username, password=password)
    allnodes = eu.extract.extract(extraction_method, 'nodes', jnodes)

    # load comments
    jcomments = eu.resource.load(comments_resource, username=username, password=password)
    allcomments = eu.extract.extract(extraction_method, 'comments', jcomments)

    logging.info("file loaded")  
    
    generated = datetime.now()
    
    network = build(allusers, \
                    allnodes, \
                    allcomments, \
                    generated, \
                    node_title_field=node_title_field, \
                    timestep_size=timestep_size, \
                    timestep_window=timestep_window, \
                    timestep_count=timestep_count, \
                    admin_roles=admin_roles, \
                    exclude_isolated=exclude_isolated)
    
    write_network(network, generated)
    
    logging.info("Completed")  

if __name__ == "__main__":
   main(sys.argv[1:])

