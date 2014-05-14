# This program rearranges raw Egderyders data and builds two lists of dicts, userlist and ciommentslist, containing 
# of the data needed to buildm graphs. These objects are then saved into files.
import os
import json
import csv
from datetime import datetime
import time
import networkx as nx
import community as co

def _mkdir(newdir):
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        if tail:
            os.mkdir(newdir)

def save_file(thing, filename, tag='', formatted=False):
    dirname = destination_path + tag + '/'
    _mkdir(dirname)
    filename = dirname + filename
    with open(filename, 'w') as outfile:
        if formatted:
            json.dump(thing, outfile, indent=4, sort_keys=True)
        else:
            json.dump(thing, outfile)

print "[%(d)s] Network processing - started" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Start reading the files
source_path = '' #PATH TO THE DIRECTORY CONTAINING THE SOURCE JSON FILES
destination_path = './public/json/'

# load comments
comments_filename = source_path + 'comments.json'
comments_data = open(comments_filename, 'r')
jcomments = json.load(comments_data)

# load nodes
nodes_filename = source_path + 'nodes.json' #remember to change this name to /users.json
nodes_data = open(nodes_filename, 'r')
jnodes = json.load(nodes_data)

# load users
users_filename = source_path + 'users.json' #remember to change this name to /users.json
users_data = open(users_filename, 'r')
jusers = json.load(users_data)

allcomments = jcomments['comments']
allnodes = jnodes['nodes']
allusers = jusers['users']

print "[%(d)s] file loaded" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# this is the network object
# going forward it should be read from a serialized format to handle caching
network = {}

# Add some file metadata
network['meta'] = {}
# Timestamp of the file generation (to show in the dashboard)
generated = datetime.now()
network['meta']['generated'] = int(generated.strftime("%s"))

# build a mapping of nodes (users) keyed on their id
nodes_map = {}
for user in [u['user'] for u in allusers]:
    if not nodes_map.has_key(user['uid']):
        user_data = {}
        user_data['id'] = user['uid']
        user_data['name'] = "User %(uid)s" % user
        # timestamps
        user_data['created_ts'] = int(user['created'])
        user_data['created_on'] = datetime.fromtimestamp(user_data['created_ts']).date().isoformat()
        # team membership
        user_data['team'] = user.has_key('roles')
        user_data['team_ts'] = user_data['created_ts'] if user_data['team'] else None # this would be different if we'd start from previous data dump
        user_data['team_on'] = user_data['created_on'] if user_data['team'] else None # this would be different if we'd start from previous data dump
        user_data['active'] = False
        nodes_map[user['uid']] = user_data
    else:
        print "User %(uid)s was alredy added to the map (??)" % user

network['nodes'] = nodes_map

print "[%(d)s] nodes collected" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# build a mapping of posts keyed by their post id (nid)
posts_map = {}
for post in [n['node'] for n in allnodes]:
    if not posts_map.has_key(post['nid']):
        post_data = {}
        post_data['id'] = post['nid']
        post_data['group_id'] = post['gid']
        # timestamps
        d = datetime.strptime(post['date'], "%d %b %Y - %H:%M")
        post_data['created_ts'] = int(time.mktime((d.year, d.month, d.day,d.hour, d.minute, d.second,-1, -1, -1)))
        post_data['created_on'] = d.date().isoformat()
        # author (& team membership)
        if post.has_key('uid') and nodes_map.has_key(post['uid']):
            post_data['author_id'] = post['uid']
            author = nodes_map[post_data['author_id']]
            post_data['team'] = author['team'] and author['team_ts'] <= post_data['created_ts']
        else:
            post_data['author_id'] = None
            post_data['team'] = False
        # length
        post_data['length'] = 0
        if post.has_key('Full text'):
            post_data['length'] += len(post['Full text'])
        if post.has_key('title'):
            post_data['length'] += len(post['title'])
        posts_map[post_data['id']] = post_data
    else:
        print "Post %(nid)s was alredy added to the map (??)" % post

print "[%(d)s] posts collected" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# build a mapping of comments keyed by their comment id
comments_map = {}
for comment in [c['comment'] for c in allcomments]:
    if not comments_map.has_key(comment['cid']):
        comment_data = {}
        comment_data['id'] = comment['cid']
        
        # timestamps
        comment_data['created_ts'] = int(comment['timestamp'])
        comment_data['created_on'] = datetime.fromtimestamp(comment_data['created_ts']).date().isoformat()
        
        # author (& team membership)
        if comment.has_key('uid') and nodes_map.has_key(comment['uid']):
            comment_data['author_id'] = comment['uid']
            author = nodes_map[comment_data['author_id']]
            comment_data['team'] = author['team'] and author['team_ts'] <= comment_data['created_ts']
        else:
            comment_data['author_id'] = None
            comment_data['team'] = False
        
        # author of the post & group id
        if comment.has_key('nid') and posts_map.has_key(comment['nid']):
            post = posts_map[comment['nid']]
            comment_data['post_author_id'] = post['author_id']
            comment_data['group_id'] = post['group_id']
        else:
            comment_data['post_author_id'] = None
            comment_data['group_id'] = None         
        
        # length
        comment_data['length'] = 0
        if comment.has_key('comment'):
            comment_data['length'] += len(comment['comment'])
        if comment.has_key('subject'):
            comment_data['length'] += len(comment['subject'])
        
        comments_map[comment['cid']] = comment_data
    
    else:
        print "Comment %(cid)s was alredy added to the map (??)" % comment
# second pass over comments, connect the comments to the parent comment
for comment in [c['comment'] for c in allcomments]:
    if comments_map.has_key(comment['cid']):
        comment_data = comments_map[comment['cid']]
        # if the comment has a pid then it was a comment to a comment
        # otherwise it was a comment to a post and the recipient is
        # the author of the post
        if comment.has_key('pid'):
            if comments_map.has_key(comment['pid']):
                comment_data['recipient_id'] = comments_map[comment['pid']]['author_id']
            else:
                comment_data['recipient_id'] = None
        else:
            comment_data['recipient_id'] = comment_data['post_author_id']
        # # check if the comment recipient is on the team
        # if nodes_map.has_key(comment_data['recipient_id']) and not comment_data['team']:
        #     recipient = nodes_map[comment_data['recipient_id']]
        #     comment_data['team'] = recipient['team'] and recipient['team_ts'] <= comment_data['created_ts']
    else:
        print "Comment %(cid)s not found" % comment


print "[%(d)s] comments collected" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# build the whole network to dump on json
links_list = []
# a comment is 'valid' if it has a recipient and an author
valid_comments = [e for e in comments_map.values() if e.get('recipient_id', None) and e.get('author_id', None)]
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
        print "[%(d)s] error: node %(n)s was linked but not found in the nodes_map" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'n':comment['author_id']}
    
    if nodes_map.has_key(comment['recipient_id']):
        nodes_map[comment['recipient_id']]['active'] = True
    else:
        print "[%(d)s] error: node %(n)s was linked but not found in the nodes_map" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'n':comment['recipient_id']}
    links_list.append(link)

def sort_by(key):
    return (lambda e: e.get(key, None))

network['edges'] = sorted(links_list, key=sort_by('ts'))

# filter out nodes that have not participated to the full:conversations
inactive_nodes = []
for node_id in nodes_map.keys():
    if not nodes_map[node_id]['active']:
        inactive_nodes.append(nodes_map.pop(node_id, None))

print "[%(d)s] inactive nodes: %(n)i" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'n':len(inactive_nodes)}
network['nodes'] = nodes_map

# Parameters
timestep = 60*60*24*7 # 1 week's seconds
window = 4 # number of timesteps to use
start_ts = network['edges'][0]['ts'] # first timestamp in the edges
end_ts = network['edges'][-1]['ts'] # last timestamp in the edges

def extract_dpsg(mdg, ts, team=True):
    dg=nx.DiGraph()
    # add all the nodes present at the time ts
    for node in mdg.nodes_iter():
        if mdg.node[node]['created_ts'] < ts and (team or not mdg.node[node]['team']):
            dg.add_node(node, mdg.node[node])
    
    for node in mdg.nodes_iter():
        for neighbour in mdg[node].keys():
            count = sum(1 for e in mdg[node][neighbour].values() if e['ts'] < ts and (team or not e['team']))
            effort = sum(e['effort'] for e in mdg[node][neighbour].values() if e['ts'] < ts and (team or not e['team']))
            team_edge = sum(1 for e in mdg[node][neighbour].values() if e['ts'] < ts and e['team'])>0
            if count > 0 and (team or not team_edge):
               dg.add_edge(node, neighbour, {'source': node, 'target': neighbour, 'effort': effort, 'count': count, 'team': team_edge}) 
    
    return dg
    
metrics = {}
# calculate content metrics
# For each timestep:
for ts in range(start_ts, end_ts, timestep):
    ts_metrics = {
        'ts': ts,
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
    # Posts Count metrics
    for p in posts_map.values():
        if p['created_ts']<ts:
            ts_metrics['full:posts_count'] += 1
            if p['team']:
                ts_metrics['team:posts_count'] += 1
            else:
                ts_metrics['user:posts_count'] += 1
        if p['created_ts']<ts and p['created_ts']>=ts-timestep*window:
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
        if c['created_ts']<ts:
            ts_metrics['full:comments_count'] += 1
            if c['team']:
                ts_metrics['team:comments_count'] += 1
            else:
                ts_metrics['user:comments_count'] += 1
        if c['created_ts']<ts and c['created_ts']>=ts-timestep*window:
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
        if c['created_ts']<ts and nodes_map.has_key(c['author_id']) and nodes_map.has_key(c['recipient_id']):
            a = nodes_map[c['author_id']]
            r = nodes_map[c['recipient_id']]
            cnv = '-'.join(sorted([c['author_id'], c['recipient_id']]))
            if not (a['team'] and a['team_ts'] <ts):
                actives.add(c['author_id'])
                conversations.add(cnv)
                if not (r['team'] and r['team_ts'] <ts):
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

print "[%(d)s] content metrics done" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#### Logging the metrics
# for t in sorted(metrics.keys()):
#     m = {'ts':datetime.fromtimestamp(t).date().isoformat()}
#     print datetime.fromtimestamp(t).date().isoformat()
#     print json.dumps(metrics[t], indent=4, sort_keys=True)
# print "[%(d)s] content metrics printed" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# build the whole network to use for metrics
MDG=nx.MultiDiGraph()

for node in network['nodes'].values():
    MDG.add_node(node['id'], node)

for edge in network['edges']:
    MDG.add_edge(edge['source'], edge['target'], attr_dict=edge)

print "[%(d)s] network built" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# build the deparallelized subnetworks to use for metrics
# compute the metrics by timestep on the deparallelized network
# Cluster, K-Cores, PageRank, 
# betweennessCentralityCount, betweennessCentralityEffort
# graphDensity, modularityCount, modularityEffort
# averageClusteringCoefficient
# Indegree, Outdegree
def extract_network_metrics(mdg, ts, team=True):
    met = {}
    dsg = extract_dpsg(mdg, ts, team)
    if team :
        pre = 'full:'
    else:
        pre = 'user:'
    met[pre+'density'] = nx.density(dsg)
    met[pre+'betweenness'] = nx.betweenness_centrality(dsg)
    met[pre+'avg_betweenness'] = float(sum(met[pre+'betweenness'].values()))/float(len(met[pre+'betweenness'].values()))
    met[pre+'betweenness_count'] = nx.betweenness_centrality(dsg, weight='count')
    met[pre+'avg_betweenness_count'] = float(sum(met[pre+'betweenness_count'].values()))/float(len(met[pre+'betweenness_count'].values()))
    met[pre+'betweenness_effort'] = nx.betweenness_centrality(dsg, weight='effort')
    met[pre+'avg_betweenness_effort'] = float(sum(met[pre+'betweenness_effort'].values()))/float(len(met[pre+'betweenness_effort'].values()))
    met[pre+'degree'] = nx.degree(dsg)
    met[pre+'avg_degree'] = float(sum(met[pre+'degree'].values()))/float(len(met[pre+'degree'].values()))
    met[pre+'degree_count'] = nx.degree(dsg, weight='count')
    met[pre+'avg_degree_count'] = float(sum(met[pre+'degree_count'].values()))/float(len(met[pre+'degree_count'].values()))
    met[pre+'degree_effort'] = nx.degree(dsg, weight='effort')
    met[pre+'avg_degree_effort'] = float(sum(met[pre+'degree_effort'].values()))/float(len(met[pre+'degree_effort'].values()))
    usg = dsg.to_undirected()
    dendo = co.generate_dendrogram(usg)
    if len(dendo)>0 and isinstance(dendo, list):
        partition = co.partition_at_level(dendo, len(dendo) - 1 )
        met[pre+'partitions'] = {}
        for com in set(partition.values()):
            members = [nodes for nodes in partition.keys() if partition[nodes] == com]
            for member in members:
                met[pre+'partitions'][member] = com
        met[pre+'louvain_modularity'] = co.modularity(partition, usg)
    else:
        met[pre+'louvain_modularity'] = None
    connected_components = nx.connected_component_subgraphs(usg)
    shortest_paths = [nx.average_shortest_path_length(g) for g in connected_components if g.size()>1]
    if len(shortest_paths) > 0:
        met[pre+'avg_distance'] = max(shortest_paths)
    else:
        met[pre+'avg_distance'] = None
    return met
    
for ts in range(start_ts, end_ts, timestep):
    ts_metrics = metrics[ts]
    # all metrics
    ts_metrics.update(extract_network_metrics(MDG, ts))
    if ts_metrics.has_key('full:partitions'):
        ts_metrics['partitions'] = ts_metrics['full:partitions']
    else:
        ts_metrics['partitions'] = None
    ts_metrics.update(extract_network_metrics(MDG, ts, team=False))
    
network['metrics'] = sorted(metrics.values(), key=sort_by('ts'))
print "[%(d)s] network metrics done" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

tag = generated.strftime('%Y-%m-%d-%H-%M-%S')

# add the nodes as an array
network['nodes'] = nodes_map.values()

# dump the network to a json file, minified
save_file(network, 'network.min.json', tag)
print "[%(d)s] network dumped" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# dump the network to a json file, formatted
save_file(network, 'network.json', tag, True)
print "[%(d)s] network large dumped" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# dump the metrics and the network to separate files:
network.pop('metrics', None)
save_file(network, 'network-no-metrics.min.json', tag)
save_file(metrics, 'metrics.min.json', tag)
print "[%(d)s] network+metrics dumped" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

save_file({'last': tag}, 'last.json')
print "[%(d)s] Completed" % {'d':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}


