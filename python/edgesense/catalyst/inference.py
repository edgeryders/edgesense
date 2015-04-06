import sys
from os import path
from os.path import exists, abspath
import requests
import logging
import cStringIO as StringIO

import rdflib
from rdflib import Graph, URIRef, RDF, ConjunctiveGraph, RDFS, OWL
from rdflib.namespace import NamespaceManager, Namespace

from FuXi.Horn.HornRules import HornFromN3
from FuXi.Rete.Util import generateTokenSet
from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Rete.Network import ReteNetwork

from simplejson import load, dump
from pyld import jsonld
from .namespaces import *

ONTOLOGY_ROOT = path.abspath(path.join(path.dirname(__file__), 'ontology'))

# Ontology loading
CATALYST_RULES = [
    "rdf-schema.ttl", #
    "owl.ttl",
    "dcterms.ttl", #
    "foaf.ttl",
    "sioc.ttl",
    "sioc_arg.ttl", #
    "swan-sioc.ttl", #
    "openannotation.ttl", #
    "catalyst_core.ttl",
    "catalyst_aif.ttl",
    "catalyst_ibis.ttl",
    # "catalyst_ibis_extra.ttl",
    "catalyst_idea.ttl",
    # "catalyst_idea_extra.ttl",
    "catalyst_vote.ttl",
    "assembl_core.ttl",
    "version.ttl",
]

SiocPost = SIOC.Post
UserAccount = SIOC.UserAccount
HasCreator = SIOC.has_creator
ReplyOf = SIOC.reply_of

CatalystPost = CATALYST.Post
CatalystIdea = CATALYST.Idea
Excerpt = CATALYST.Excerpt
ExpressesIdea = CATALYST.expressesIdea

Created = DCTERMS.created

GenericIdeaNode = IDEA.GenericIdeaNode
InclusionRelation = IDEA.InclusionRelation
DirectedIdeaRelation = IDEA.DirectedIdeaRelation

HasTarget = OA.hasTarget
HasSource = OA.hasSource
HasBody = OA.hasBody

class InferenceStore(object):
    def __init__(self, ontology_root=ONTOLOGY_ROOT):
        self.ontology_root = ontology_root
        
    def as_file(self, fname):
        uri = path.join(self.ontology_root, fname) 
        logging.info("InferenceStore %(s)s"%{'s':uri})
        if uri.startswith('http'):
            r = requests.get(uri)
            assert r.ok
            return r.content
        elif uri.startswith('/' or uri.startswith('file:')):
            if uri.startswith('file:'):
                uri = uri[5:]
            while uri.startswith('//'):
                uri = uri[1:]
            assert exists(uri)
            return open(uri)
        else:
            raise ValueError

    def add_ontologies(self, rules=CATALYST_RULES):
        for r in rules:
            self.add_ontology(self.as_file(r))
            
    def add_ontology(self, source, format='turtle'):
        pass
        
    def get_inference(self, graph):
        return graph


class FuXiInferenceStore(InferenceStore):

    _instance = None

    def __init__(self, ontology_root=ONTOLOGY_ROOT, use_rdfs=False, use_owl=False):
        super(FuXiInferenceStore, self).__init__(ontology_root)
        (self.rule_store, self.rule_graph, self.network) = SetupRuleStore(
            makeNetwork=True)
        self.ontology = Graph()
        rulesets = []
        if use_rdfs:
            rulesets.append('rdfs-rules.n3')
        else:
            # minimum ruleset: only subclassing.
            prefix = "@prefix rdfs: <%s>.\n@prefix owl: <%s>.\n" % (RDFS, OWL)
            rules = [
                "{?P @has owl:inverseOf ?I. ?S ?P ?O} => {?O ?I ?S}.",
                "{?P @has rdfs:domain ?C. ?S ?P ?O} => {?S a ?C}.",
                "{?P @has rdfs:range ?C. ?S ?P ?O} => {?O a ?C}.",
                "{?A rdfs:subClassOf ?B. ?S a ?A} => {?S a ?B}.",
                "{?A owl:subClassOf ?B. ?S a ?A} => {?S a ?B}.",
                "{?P @has rdfs:subPropertyOf ?R. ?S ?P ?O} => {?S ?R ?O}.",
                "{?P @has owl:subPropertyOf ?R. ?S ?P ?O} => {?S ?R ?O}.",
            ]
            for rule in HornFromN3(StringIO.StringIO(prefix+"\n".join(rules))):
                self.network.buildNetworkFromClause(rule)
        if use_owl:
            # Does not work yet
            rulesets.append('owl-rules.n3')
        for ruleset in rulesets:
            for rule in HornFromN3(self.as_file(ruleset)):
                self.network.buildNetworkFromClause(rule)

    def add_ontology(self, source, format='turtle'):
        self.ontology.parse(source, format=format)

    def get_inference(self, graph):
        network = self.network
        network.reset()
        network.feedFactsToAdd(generateTokenSet(self.ontology))
        logging.info("InferenceStore ontology loaded")
        network.feedFactsToAdd(generateTokenSet(graph))
        return network.inferredFacts

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            store = FuXiInferenceStore()
            store.add_ontologies()
            cls._instance = store
            logging.info("InferenceStore engine setup")
        return cls._instance


def catalyst_graph_for(file):
    if file.startswith('/'):
        file = 'file://'+file
    logging.info("InferenceStore catalyst_graph_for started")
        
    # quads = jsonld.to_rdf(file, {'format': 'application/nquads'})
    logging.info("InferenceStore JSON-LD loaded")

    g = ConjunctiveGraph()
    g.namespace_manager = namespace_manager
    # g.parse(data=quads, format='nquads')
    g.load(file, format="json-ld")
    logging.info("InferenceStore base graph loaded")

    f = FuXiInferenceStore.get_instance()

    # get the inference engine
    cl = f.get_inference(g)
    logging.info("InferenceStore inference graph loaded")

    union_g = rdflib.ConjunctiveGraph()

    for s,p,o in g.triples( (None, None, None) ):
       union_g.add( (s,p,o) )

    for s,p,o in cl.triples( (None, None, None) ):
       union_g.add( (s,p,o) )

    logging.info("InferenceStore union graph prepared")

    return union_g
