import networkx as nx
import community as co
from edgesense.network.utils import extract_dpsg
from datetime import datetime

def extract_content_metrics(nodes_map, posts_map, comments_map, ts, timestep, timestep_window):
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
    for u in nodes_map.values():
        if int(u['created_ts'])<=ts:
            ts_metrics['full:users_count'] += 1
            if u['team']:
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
            cnv = '-'.join(sorted([str(c['author_id']), str(c['recipient_id'])]))
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
    
    return ts_metrics

