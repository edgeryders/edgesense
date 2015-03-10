import datetime
import time

from dateutil import parser as dtparse

from ..namespaces import *

def stringify(val):
    if val is not None:
        return str(val)
    # else None

def as_timestamp(val):
    if val is not None:
        try:
            val = dtparse.parse(val)
            return int(time.mktime(val.timetuple()))
        except:
            return None

def post_as_data(post, graph, info=None):
    info = info or {}
    info['id'] = str(idea)
    created = graph.value(idea, DCTERMS.created)
    if created:
        created = datetime.strptime(str(created), '%Y-%m-%dT%H:%M:%S')
        info['created'] = int(time.mktime(created.timetuple()))
    if 'reply_of' not in info:
        info['reply_of'] = stringify(graph.value(idea, SIOC.reply_of))
    if 'author' not in info:
        info['author'] = stringify(graph.value(idea, SIOC.has_creator))
    return info

def idea_as_data(idea, graph, info=None):
    # Not that different
    return post_as_data(idea, graph, info)

user_template = {
    "created_ts": 0,
    "name": "",
    "team_ts": None,
    "created_on": "",
    "link": "",
    "team": False,
    "active": True,
    "id": "001",
    "team_on": None
}


def is_moderator(graph, user, moderator_roles=None):
    if not moderator_roles:
        return False
    roles = {role for (s, p, role) in graph.triples(user, SIOC.has_function, None)}
    for role in roles:
        role_names = graph.value(role, FOAF.name)
        if role_name and str(role_name) in moderator_roles:
            return True
    return False


def user_as_node(graph, user, moderator_test=None):
    moderator_test = moderator_test or (lambda graph, user: False)
    info = dict(user_template)
    info['id'] = str(user)
    info['name'] = stringify(graph.value(user, FOAF.name)) or str(user)
    info['team'] = moderator_test(graph, user)
    created = graph.value(user, DCTERMS.created)
    if not created:
        posts = {post for (post, p, u) in graph.triples((None, SIOC.has_creator, user))}
        created = {graph.value(post, DCTERMS.created) for post in posts}
        created.discard(None)
        if created:
            created = min(created)
        else:
            created = None
    info['created_on'] = str(created)
    info['created_ts'] = as_timestamp(created)
    info['link'] = stringify(graph.value(user, FOAF.homepage))
    return info


post_template = {
    "target": "",
    "ts": 0,
    "source": "",
    "team": True,
    "effort": 0,
    "id": ""
}

def post_as_link(
        graph, post, reply_to_post, post_author=None, reply_to_post_author=None, moderator_test=None):
    info = dict(post_template)
    if not post_author:
        post_author = stringify(graph.value(post, SIOC.has_creator))
    if not reply_to_post_author:
        reply_to_post_author = stringify(graph.value(reply_to_post, SIOC.has_creator))
    if (not post_author) or (not reply_to_post_author):
        return None
    info["source"] = post_author
    info['target'] = reply_to_post_author
    info["id"] = post
    info['ts'] = as_timestamp(graph.value(post, DCTERMS.created))
    if moderator_test is not None:
        info['team'] = moderator_test(graph, post_author) or moderator_test(graph, reply_to_post_author)
    else:
        info['team'] = False
    return info

def convert_to_network(graph, posts, creator_of_post, reply_of, moderator_test=None):
    all_creators = {creator_of_post.get(n, None) for n in posts}
    all_creators.discard(None)
    nodes = [user_as_node(graph, user, moderator_test) for user in all_creators]
    edges = []
    for post in posts:
        for replying in reply_of[post]:
            edges.append(post_as_link(graph, post, replying, creator_of_post[post], creator_of_post[replying], moderator_test))
    return nodes, edges


import simple
import excerpts
import ideas
