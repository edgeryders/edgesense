from edgesense.utils import sort_by
from edgesense.content.metrics import extract_content_metrics
from edgesense.network.metrics import extract_network_metrics
import logging

def compute_all_metrics(nodes_map, posts_map, comments_map, network, timesteps_range, timestep, timestep_window):
    metrics = {}
    
    # calculate the network metrics
    for ts in timesteps_range:
        metrics[ts] = metrics_for_ts(nodes_map, posts_map, comments_map, network, ts, timestep, timestep_window)
        
    return sorted(metrics.values(), key=sort_by('ts'))

def metrics_for_ts(nodes_map, posts_map, comments_map, network, ts, timestep, timestep_window):
    # calculate content metrics
    ts_metrics = extract_content_metrics(nodes_map, posts_map, comments_map, ts, timestep, timestep_window)
    
    # calculate network metrics
    ts_metrics.update(extract_network_metrics(network, ts))
    if ts_metrics.has_key('full:partitions'):
        ts_metrics['partitions'] = ts_metrics['full:partitions']
    else:
        ts_metrics['partitions'] = None
    ts_metrics.update(extract_network_metrics(network, ts, team=False))
    
    return ts_metrics
    