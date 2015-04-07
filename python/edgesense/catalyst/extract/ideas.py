from collections import defaultdict
from edgesense.catalyst.namespaces import SIOC, DCTERMS, RDF, IDEA, ASSEMBL
from . import convert_to_network


def extract_ideas(graph, creator_of_post=None):
    # mapping ideas
    node_ids = list(graph.subjects(RDF.type, IDEA.GenericIdeaNode))
    edge_ids = list(graph.subjects(RDF.type, IDEA.DirectedIdeaRelation))
    if creator_of_post is None:
        creator_of_post = {
            obj: creator for (obj, p, creator) in graph.triples((None, SIOC.has_creator, None))
        }
    def has_creator(n):
        return creator_of_post.get(n, None) is not None
    node_ids = filter(has_creator, node_ids)
    if not node_ids:
        return ([], {})
    sources = {link: node for (link, p, node) in graph.triples((None, IDEA.source_idea, None)) if node in node_ids}
    targets = {link: node for (link, p, node) in graph.triples((None, IDEA.target_idea, None)) if node in node_ids}
    # filter incomplete edges (with no usable source or target)
    def complete_edge(edge):
        return sources.get(edge, None) is not None and targets.get(edge, None) is not None
    edge_ids = filter(complete_edge, edge_ids)
    reply_of = defaultdict(list)
    # some edges will act as ideas; if the creator is different from the source.
    pseudo_nodes = []
    for edge in edge_ids:
        creator = creator_of_post.get(edge, None)
        if creator and creator != creator_of_post[sources[edge]]:
            pseudo_nodes.append(edge)
            reply_of[edge].append(targets[edge])
            reply_of[edge].append(sources[edge])
        else:
            reply_of[sources[edge]].append(targets[edge])
    # source_posts = set(reply_of.keys())
    all_posts = node_ids[:]
    all_posts.extend(pseudo_nodes)
    # top_posts = set(all_posts) - source_posts
    # comments = set(all_posts) - top_posts
    return (all_posts, reply_of)


def extract_posts(graph, creator_of_post=None):
    # mapping ideas
    node_ids = list(graph.subjects(RDF.type, SIOC.Post))
    if creator_of_post is None:
        creator_of_post = {
            obj: creator for (obj, p, creator) in graph.triples((None, SIOC.has_creator, None))
        }
    def has_creator(n):
        return creator_of_post.get(n, None) is not None
    node_ids = filter(has_creator, node_ids)
    if not node_ids:
        return ([], {})
    reply_of = {
        post: [reply for (s, p, reply) in graph.triples((post, SIOC.reply_of, None))]
        for post in node_ids
    }
    return (node_ids, reply_of)


def extract_ideas_and_posts(graph, creator_of_post):
    idea_ids, idea_reply = extract_ideas(graph, creator_of_post)
    post_ids, post_reply = extract_posts(graph, creator_of_post)
    idea_reply.update(post_reply)
    if len(idea_ids) and len(post_ids):
        # Note that idea_reply is already a defaultdict(list)
        for (post, p, idea) in graph.triples(
                (None, ASSEMBL.postLinkedToIdea, None)):
            idea_reply[post].append(idea)
    idea_ids.extend(post_ids)
    return idea_ids, idea_reply


def graph_to_network(generated, graph, use_ideas=True, use_posts=True, moderator_test=None):
    creator_of_post = {
        obj: creator for (obj, p, creator) in graph.triples((None, SIOC.has_creator, None))
    }
    assert use_ideas or use_posts
    if use_ideas:
        if use_posts:
            posts, reply_of = extract_ideas_and_posts(graph, creator_of_post)
        else:
            posts, reply_of = extract_ideas(graph, creator_of_post)
    else:
        posts, reply_of = extract_posts(graph, creator_of_post)
    return convert_to_network(generated, graph, posts, creator_of_post, reply_of, moderator_test)
