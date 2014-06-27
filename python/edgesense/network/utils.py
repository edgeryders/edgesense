import networkx as nx

def sort_by(key):
    return (lambda e: e.get(key, None))

def extract_dpsg(mdg, ts, team=True):
    dg=nx.DiGraph()
    # add all the nodes present at the time ts
    for node in mdg.nodes_iter():
        if mdg.node[node]['created_ts'] <= ts and (team or not mdg.node[node]['team']):
            dg.add_node(node, mdg.node[node])
    
    for node in mdg.nodes_iter():
        for neighbour in mdg[node].keys():
            count = sum(1 for e in mdg[node][neighbour].values() if e['ts'] <= ts and (team or not e['team']))
            effort = sum(e['effort'] for e in mdg[node][neighbour].values() if e['ts'] <= ts and (team or not e['team']))
            team_edge = sum(1 for e in mdg[node][neighbour].values() if e['ts'] <= ts and e['team'])>0
            if count > 0 and (team or not team_edge):
               dg.add_edge(node, neighbour, {'source': node, 'target': neighbour, 'effort': effort, 'count': count, 'team': team_edge}) 
    
    return dg
