import networkx as nx
import logging
import edgesense.utils as eu
from datetime import datetime
import itertools 

def set_isolated(nodes_list, mdg):
    ts = int(datetime.now().strftime("%s"))
    dsg = extract_dpsg(mdg, ts, True)
    usg = dsg.to_undirected()
    isolated_nodes = set(nx.isolates(usg))
    for node in nodes_list:
        if node['id'] in isolated_nodes:
            node['isolated'] = True
        
def extract_dpsg(mdg, ts, team=True):
    dg=nx.DiGraph()
    # add all the nodes present at the time ts
    for node in mdg.nodes_iter():
        nts = mdg.node[node].get('created_ts', None)
        if nts and nts <= ts and (team or not mdg.node[node]['team']):
            dg.add_node(node, mdg.node[node])
    
    for node in dg.nodes_iter():
        for neighbour in mdg[node].keys():
            count = sum(1 for e in mdg[node][neighbour].values() if e['ts'] <= ts and (team or not e['team']))
            effort = sum(e['effort'] for e in mdg[node][neighbour].values() if e['ts'] <= ts and (team or not e['team']))
            team_edge = sum(1 for e in mdg[node][neighbour].values() if e['ts'] <= ts and e['team'])>0
            # an edge should be added here only if either ends are included
            if count > 0 and (team or not team_edge) and dg.has_node(neighbour):
               dg.add_edge(node, neighbour, {'source': node, 'target': neighbour, 'effort': effort, 'count': count, 'team': team_edge}) 
    
    return dg

def build_network(network):
    MDG=nx.MultiDiGraph()

    for node in network['nodes']:
        MDG.add_node(node['id'], node)

    for edge in network['edges']:
        MDG.add_edge(edge['source'], edge['target'], attr_dict=edge)
    
    set_isolated(network['nodes'], MDG)
    
    return MDG

def make_edge(comment, recipient):
    link = {
        'id': "{0}_{1}_{2}".format(comment['author_id'],recipient,comment['created_ts']),
        'source': comment['author_id'],
        'target': recipient,
        'ts': comment['created_ts'],
        'effort': comment['length'],
        'team': comment['team']
    }
    return link
    
def extract_edges(nodes_map, comments_map):
    # build the list of edges
    edges_list = []
    # a comment is 'valid' if it has a recipient and an author
    valid_comments = [e for e in comments_map.values() if e.get('recipient_id', None) and e.get('author_id', None)]
    logging.info("%(v)i valid comments on %(t)i total" % {'v':len(valid_comments), 't':len(comments_map.values())})
    
    # build the comments network to use for metrics
    for comment in valid_comments:
        if nodes_map.has_key(comment['author_id']):
            nodes_map[comment['author_id']]['active'] = True
        else:
            logging.info("error: node %(n)s was linked but not found in the nodes_map" % {'n':comment['author_id']})  
        
        if comment.get('post_all_authors', None) and hasattr(comment['post_all_authors'], '__iter__'):
            links = [make_edge(comment, recipient) for recipient in comment['post_all_authors']]
        else:
            links = [make_edge(comment, comment['recipient_id'])]
        
        for link in links:
            if nodes_map.has_key(link['target']):
                nodes_map[link['target']]['active'] = True
            else:
                logging.info("error: node %(n)s was linked but not found in the nodes_map" % {'n':link['target']})  
            edges_list.append(link)


    return sorted(edges_list, key=eu.sort_by('ts'))

def extract_multiauthor_post_edges(nodes_map, posts_map):
    # build the list of edges
    edges_list = []
    # a comment is 'valid' if it has a recipient and an author
    multiauthor_posts = [e for e in posts_map.values() if e.get('all_authors', None) and hasattr(e.get('all_authors', None), '__iter__') and len(e.get('all_authors', None))>1]
    logging.info("%(v)i multiauthor posts on %(t)i total" % {'v':len(multiauthor_posts), 't':len(posts_map.values())})
    
    # build the posts network to use for metrics
    for post in multiauthor_posts:
        for authors in itertools.product(post['all_authors'], post['all_authors']):
            if authors[0]!=authors[1]:
                link = {
                    'id': "{0}_{1}_{2}".format(authors[0],authors[1],post['created_ts']),
                    'source': authors[0],
                    'target': authors[1],
                    'ts': post['created_ts'],
                    'effort': post['length'],
                    'team': post['team']
                }
                if nodes_map.has_key(authors[0]):
                    nodes_map[authors[0]]['active'] = True
                else:
                    logging.info("error: node %(n)s was linked but not found in the nodes_map" % {'n':authors[0]})  
        
                if nodes_map.has_key(authors[1]):
                    nodes_map[authors[1]]['active'] = True
                else:
                    logging.info("error: node %(n)s was linked but not found in the nodes_map" % {'n':authors[1]})  
                edges_list.append(link)

    return sorted(edges_list, key=eu.sort_by('ts'))

def extract_inactive_nodes(nodes_map):
    # filter out nodes that have not participated to the full:conversations
    inactive_nodes = []
    for node_id in nodes_map.keys():
        if not nodes_map[node_id]['active']:
            inactive_nodes.append(nodes_map.pop(node_id, None))

    return inactive_nodes

