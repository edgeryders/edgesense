from threading import *

def promote_none_root_set_children(containers):
    result = []
    for ctr in containers:
        if not(ctr.message):
            for child in ctr.children:
                result.append(child)
        else:
            result.append(ctr)

    return result

def force_name_as_address(containers):
    for ctr in containers:
        if ctr.message and ctr.message.sender_name:
            ctr.message.sender_address = ctr.message.sender_name
        force_name_as_address(ctr.children)
    
def map_user(container, moderators, charset='utf-8'):
    user = {
        'uid': unicode(container.message.sender_address, charset),
        'created': container.message.created
    }
    if container.message.sender_name:
        user['name'] = unicode(container.message.sender_name, charset)
    if user['uid'] in moderators:
        user['roles'] = 'Moderator'
    return user

def map_node(container, charset='utf-8'):
    node = {
        'nid': unicode(container.message.message_id, charset),
        'uid': unicode(container.message.sender_address, charset),
        'created': container.message.created
    }
    return node

def map_comment(container, root_message, charset='utf-8'):
    comment = {
        'cid': unicode(container.message.message_id, charset),
        'uid': unicode(container.message.sender_address, charset),
        'nid': unicode(root_message.message.message_id, charset),
        'created': container.message.created
    }
    if container.parent and container.parent.message:
        comment['pid'] = container.parent.message.message_id
    return comment

def add_comments_from(container, root_message, comments, user_map, moderators, charset='utf-8'):
    for child in container.children:
        if child.message:
            comments.append(map_comment(child, root_message, charset))
            user = map_user(child, moderators, charset)
            if not(user_map.has_key(user['uid'])) or user_map[user['uid']]['created'] > user['created']:
                user_map[user['uid']] = user
        add_comments_from(child, root_message, comments, user_map, moderators, charset)
    
def users_nodes_comments_from(containers, moderators, charset='utf-8'):
    user_map = {}   
    nodes = []
    comments = []
    for container in containers:
        if container.message:
            nodes.append(map_node(container, charset))
            user = map_user(container, moderators, charset)
            if not(user_map.has_key(user['uid'])) or user_map[user['uid']]['created'] > user['created']:
                user_map[user['uid']] = user
        
        add_comments_from(container, container, comments, user_map, moderators, charset)
    
    users = user_map.values()
    return(users,nodes,comments)
