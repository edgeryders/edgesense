import datetime
import time
from itertools import chain

from dateutil import parser as dtparse

from ..namespaces import *
import edgesense.utils as eu

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


def is_moderator(graph, account, moderator_roles=None):
    if not moderator_roles:
        return False
    roles = {role for (s, p, role) in graph.triples((account, SIOC.has_function, None))}
    for role in roles:
        role_names = graph.value(role, SIOC.name)
        if role_name and str(role_name) in moderator_roles:
            return True
    return False


def account_as_node(graph, account, profile_of_account, moderator_test=None):
    # We have a bug in early CIF files where posts are linked directly to users
    user = graph.value(account, SIOC.account_of) or account
    profile_of_account[account] = user
    moderator_test = moderator_test or (lambda user: False)
    info = dict(user_template)
    info['id'] = str(user)
    info['name'] = stringify(graph.value(user, FOAF.name)) or str(user)
    info['team'] = moderator_test(account)
    created = graph.value(account, DCTERMS.created)
    if not created:
        t = graph.triples((None, SIOC.has_creator, account))
        if account is not user:
            t = chain(t, graph.triples((None, SIOC.has_creator, user)))
        posts = {post for (post, p, u) in t}
        created = {graph.value(post, DCTERMS.created) for post in posts}
        created.discard(None)
        if created:
            created = min(created)
        else:
            created = None
    info['created_on'] = str(created)
    info['created_ts'] = as_timestamp(created)
    info['link'] = stringify(graph.value(user, FOAF.homepage))
    print info
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
        graph, post, post_id, reply_to_post, post_author=None, reply_to_post_author=None, moderator_test=None):
    info = dict(post_template)
    moderator_test = moderator_test or (lambda account: False)
    if not post_author:
        post_author = stringify(graph.value(post, SIOC.has_creator))
    if not reply_to_post_author:
        reply_to_post_author = stringify(graph.value(reply_to_post, SIOC.has_creator))
    if (not post_author) or (not reply_to_post_author):
        return None
    info["source"] = stringify(post_author)
    info['target'] = stringify(reply_to_post_author)
    info["reply_of"] = stringify(reply_to_post)
    info["id"] = post_id
    info['ts'] = as_timestamp(graph.value(post, DCTERMS.created))
    info['team'] = moderator_test(post_author) or moderator_test(reply_to_post_author)
    return info

def convert_to_network(generated, graph, posts, creator_of_post, reply_of, moderator_test=None):
    all_creators = {creator_of_post.get(n, None) for n in posts}
    all_creators.discard(None)
    profile_of_account = {}
    nodes = [account_as_node(graph, account, profile_of_account, moderator_test) for account in all_creators]
    edges = []
    for post in posts:
        for i, replying in enumerate(reply_of.get(post, ())):
            post_id = stringify(post)
            if i:
                 post_id = '%s__%d' % (post_id, i)
            edges.append(post_as_link(
                graph, post, post_id, replying, profile_of_account[creator_of_post[post]],
                profile_of_account[creator_of_post[replying]], moderator_test))

    nodes.sort(key=eu.sort_by('created_ts'))
    edges.sort(key=eu.sort_by('ts'))

    # this is the network object
    # going forward it should be read from a serialized format to handle caching
    return {
        'meta': {
            'generated': int(generated.strftime("%s"))
        },
        'edges': edges,
        'nodes': nodes
    }

import simple
import excerpts
import ideas
