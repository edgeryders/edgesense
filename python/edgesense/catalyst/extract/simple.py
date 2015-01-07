from datetime import datetime
import time
import logging
from edgesense.catalyst.inference import SiocPost, CatalystPost, UserAccount, Created, HasCreator, ReplyOf
from rdflib import RDF

# find all the contents in the graph
def get_post_map(post, graph):
    try:
        post_map = {}
        post_map['id'] = str(post)
        created = datetime.strptime(str(graph.value(post, Created)), '%Y-%m-%dT%H:%M:%S')
        post_map['created'] = int(time.mktime(created.timetuple()))
        reply_of = graph.value(post, ReplyOf)
        if reply_of:
            post_map['reply_of'] = str(reply_of)
        else:
            post_map['reply_of'] = None
        author = graph.value(post, HasCreator)
        if author:
            post_map['author'] = str(author)
        else:
            post_map['author'] = None          
        return post_map
    except:
        return None
  
def map_user(mapped_post):
    user = {
        'uid': mapped_post['author'],
        'created': mapped_post['created']
    }
    return user

def map_node(mapped_post):
    node = {
        'nid': mapped_post['id'],
        'uid': mapped_post['author'],
        'created': mapped_post['created']
    }
    return node

def map_comment(mapped_post):
    comment = {
        'cid': mapped_post['id'],
        'nid': mapped_post['reply_of'],
        'uid': mapped_post['author'],
        'created': mapped_post['created']
    }
    return comment

def extract_users(posts_mapped):
    users_map = {}
    for user in [map_user(post) for post in posts_mapped]:
        if not(users_map.has_key(user['uid'])) or user['created'] <= users_map[user['uid']]['created']:
            users_map[user['uid']] = user
    return users_map.values()

def users_nodes_comments_from(graph):
    # mapping posts      
    all_posts_mapped = [get_post_map(post, graph) for post in graph.subjects(RDF.type, CatalystPost)]
    all_posts_mapped = filter(None, all_posts_mapped)
    # users are the creators of the posts
    all_users = extract_users(all_posts_mapped)
    # nodes are posts without a reply_of
    all_nodes = [map_node(post_mapped) for post_mapped in all_posts_mapped if not post_mapped['reply_of']]  
    # comments are posts with a reply_of
    all_comments = [map_comment(post_mapped) for post_mapped in all_posts_mapped if post_mapped['reply_of']]  
    return (all_users, all_nodes, all_comments)
