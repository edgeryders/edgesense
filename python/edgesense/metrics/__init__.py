from edgesense.utils import sort_by
from edgesense.content.metrics import extract_content_metrics
from edgesense.network.metrics import extract_network_metrics
from edgesense.utils.extract import calculate_timestamp_range
from edgesense.network.utils import build_network
import logging

def compute_all_metrics(nodes_map, posts_map, comments_map, network, timesteps_range, timestep, timestep_window):
    metrics = {}
    
    # calculate the network metrics
    for ts in timesteps_range:
        metrics[ts] = metrics_for_ts(nodes_map, posts_map, comments_map, network, ts, timestep, timestep_window)
        
    return sorted([m for m in metrics.values() if m is not None], key=sort_by('ts'))

def metrics_for_ts(nodes_map, posts_map, comments_map, network, ts, timestep, timestep_window):
    # calculate network metrics
    net_metrics = extract_network_metrics(network, ts)
    
    if len(net_metrics) > 0:
        # calculate content metrics
        ts_metrics = extract_content_metrics(nodes_map, posts_map, comments_map, ts, timestep, timestep_window)
    
        ts_metrics.update(net_metrics)
        if ts_metrics.has_key('full:partitions'):
            ts_metrics['partitions'] = ts_metrics['full:partitions']
        else:
            ts_metrics['partitions'] = None
        ts_metrics.update(extract_network_metrics(network, ts, team=False))
    
        return ts_metrics

def calculate_network_metrics(nodes_map, posts_map, comments_map, network, timestep_size, timestep_window, timestep_count):
    # Parameters    
    timestep, timesteps_range = calculate_timestamp_range(network, timestep_size, timestep_window, timestep_count)
    
    # build the whole network to use for metrics
    directed_multiedge_network = build_network(network)    
    logging.info("network built")  

    # calculate the metrics
    network['metrics'] = compute_all_metrics(nodes_map, posts_map, comments_map, directed_multiedge_network, timesteps_range, timestep, timestep_window)

    logging.info("network metrics done")
    return directed_multiedge_network

