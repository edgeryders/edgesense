from datetime import datetime
import time
import logging
from edgesense.catalyst.inference import SiocPost, CatalystPost, UserAccount, Created, HasCreator, ReplyOf, HasTarget, HasSource, Excerpt, ExpressesIdea, GenericIdeaNode
from rdflib import RDF
from edgesense.catalyst.extract.simple import map_node, get_post_map, map_comment, extract_users

FAKE_USER = "_plato"

def get_idea_map(idea, graph):
    try:
        idea_map = {}
        idea_map['id'] = str(idea)
        created = datetime.strptime(str(graph.value(idea, Created)), '%Y-%m-%dT%H:%M:%S')
        idea_map['created'] = int(time.mktime(created.timetuple()))
        idea_map['author'] = FAKE_USER
        return idea_map
    except:
        return None

#  - find the target, from the target find the hasSource, from that the content id
#  - find the body, from that find the expressesIdea, from that find the idea id
#  - extract the created from the excerpt    
def get_excerpt_map(excerpt, graph):
    try:
        excerpt_map = {}
        specific_resource = graph.value(excerpt, HasTarget)
        post = graph.value(specific_resource, HasSource)
        excerpt_map['id'] = str(post)
        created = datetime.strptime(str(graph.value(post, Created)), '%Y-%m-%dT%H:%M:%S')
        excerpt_map['created'] = int(time.mktime(created.timetuple()))
        reply_of = graph.value(specific_resource, ExpressesIdea)
        if reply_of:
            excerpt_map['reply_of'] = str(reply_of)
        else:
            excerpt_map['reply_of'] = None
        author = graph.value(post, HasCreator)
        if author:
            excerpt_map['author'] = str(author)
        else:
            excerpt_map['author'] = None          
        return excerpt_map
    except:
        return None

def users_nodes_comments_from(graph):
    # find all the generic idea nodes, with data: id, date
    all_ideas = [get_idea_map(idea, graph) for idea in graph.subjects(RDF.type, GenericIdeaNode)]
    # add a fake user 
    all_users = [{'uid': FAKE_USER, 'created': min([i['created'] for i in all_ideas if i])}]
    # add a post for each idea node
    all_nodes = [map_node(idea) for idea in all_ideas if idea]

    # find all the content items,
    all_posts_mapped = [get_post_map(post, graph) for post in graph.subjects(RDF.type, CatalystPost)]
    # add a user for each content item author
    all_users += extract_users(all_posts_mapped)

    # find all the excerpts, for each one:
    all_excerpts_mapped = [get_excerpt_map(excerpt, graph) for excerpt in graph.subjects(RDF.type, Excerpt)]
    #  add a comment from the content_id to the idea_id on the excerpt created date
    #  by the content author
    all_comments = [map_comment(excerpt_mapped) for excerpt_mapped in all_excerpts_mapped if excerpt_mapped]
    return (all_users, all_nodes, all_comments)
