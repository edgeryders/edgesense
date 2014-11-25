import networkx as nx
import community as co
from edgesense.network.utils import extract_dpsg
from datetime import datetime
import logging
   
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
    
    # avoid trying to compute metrics for  
    # the case of empty networks 
    if dsg.number_of_nodes()==0:
        return met
    
    met[pre+'nodes_count'] = dsg.number_of_nodes()
    met[pre+'edges_count'] = dsg.number_of_edges()
    met[pre+'density'] = nx.density(dsg)
    met[pre+'betweenness'] = nx.betweenness_centrality(dsg)
    met[pre+'avg_betweenness'] = float(sum(met[pre+'betweenness'].values()))/float(len(met[pre+'betweenness'].values()))
    met[pre+'betweenness_count'] = nx.betweenness_centrality(dsg, weight='count')
    met[pre+'avg_betweenness_count'] = float(sum(met[pre+'betweenness_count'].values()))/float(len(met[pre+'betweenness_count'].values()))
    met[pre+'betweenness_effort'] = nx.betweenness_centrality(dsg, weight='effort')
    met[pre+'avg_betweenness_effort'] = float(sum(met[pre+'betweenness_effort'].values()))/float(len(met[pre+'betweenness_effort'].values()))
    met[pre+'in_degree'] = dsg.in_degree()
    met[pre+'avg_in_degree'] = float(sum(met[pre+'in_degree'].values()))/float(len(met[pre+'in_degree'].values()))
    met[pre+'out_degree'] = dsg.out_degree()
    met[pre+'avg_out_degree'] = float(sum(met[pre+'out_degree'].values()))/float(len(met[pre+'out_degree'].values()))
    met[pre+'degree'] = dsg.degree()
    met[pre+'avg_degree'] = float(sum(met[pre+'degree'].values()))/float(len(met[pre+'degree'].values()))
    met[pre+'degree_count'] = dsg.degree(weight='count')
    met[pre+'avg_degree_count'] = float(sum(met[pre+'degree_count'].values()))/float(len(met[pre+'degree_count'].values()))
    met[pre+'degree_effort'] = dsg.degree(weight='effort')
    met[pre+'avg_degree_effort'] = float(sum(met[pre+'degree_effort'].values()))/float(len(met[pre+'degree_effort'].values()))
    usg = dsg.to_undirected()
    louvain = extract_louvain_modularity(usg)
    met[pre+'partitions'] = louvain['partitions']
    met[pre+'louvain_modularity'] = louvain['modularity']        
    connected_components = nx.connected_component_subgraphs(usg)
    shortest_paths = [nx.average_shortest_path_length(g) for g in connected_components if g.size()>1]
    if len(shortest_paths) > 0:
        met[pre+'avg_distance'] = max(shortest_paths)
    else:
        met[pre+'avg_distance'] = None
    return met


def extract_louvain_modularity(g):
    met = {}
    usg = g.copy()
    isolated = nx.isolates(usg)
    usg.remove_nodes_from(isolated)
    dendo = co.generate_dendrogram(usg)
    if len(dendo)>0 and isinstance(dendo, list):
        partition = co.partition_at_level(dendo, len(dendo) - 1 )
        met['partitions'] = {}
        for com in set(partition.values()):
            members = [nodes for nodes in partition.keys() if partition[nodes] == com]
            for member in members:
                met['partitions'][member] = com
        met['modularity'] = co.modularity(partition, usg)
        # for node in isolated:
        #     met['partitions'][node] = None
    else:
        met['partitions'] = None
        met['modularity'] = None
    
    return met