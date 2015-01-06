import sys
from os import path
from os.path import exists, abspath
import requests
import logging
import cStringIO as StringIO

import rdflib
from rdflib import Graph, URIRef, RDF, ConjunctiveGraph, RDFS
from rdflib.namespace import NamespaceManager, Namespace

from FuXi.Horn.HornRules import HornFromN3
from FuXi.Rete.Util import generateTokenSet
from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Rete.Network import ReteNetwork

from simplejson import load, dump
from pyld import jsonld

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

SiocPost = URIRef(u'http://rdfs.org/sioc/ns#Post')
CatalystPost = URIRef(u'http://purl.org/catalyst/core#Post')
UserAccount = URIRef(u'http://rdfs.org/sioc/ns#UserAccount')
Created = URIRef(u'http://purl.org/dc/terms/created')
HasCreator = URIRef(u'http://rdfs.org/sioc/ns#has_creator')
ReplyOf = URIRef(u'http://rdfs.org/sioc/ns#reply_of')
CatalystIdea = URIRef(u'http://purl.org/catalyst/core#Idea')
GenericIdeaNode = URIRef(u'http://purl.org/catalyst/idea#GenericIdeaNode')
InclusionRelation = URIRef(u'http://purl.org/catalyst/idea#InclusionRelation')
Excerpt = URIRef(u'http://purl.org/catalyst/core#Excerpt')
ExpressesIdea = URIRef(u'http://purl.org/catalyst/core#expressesIdea')
HasTarget = URIRef(u'http://www.openannotation.org/ns/hasTarget')
HasSource = URIRef(u'http://www.openannotation.org/ns/hasSource')
HasBody = URIRef(u'http://www.openannotation.org/ns/hasBody')

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
            prefix = "@prefix rdfs: <%s>.\n" % (RDFS, )
            rules = [
                "{?A rdfs:subClassOf ?B. ?S a ?A} => {?S a ?B}.",
                "{?P @has rdfs:domain ?C. ?S ?P ?O} => {?S a ?C}.",
                "{?P @has rdfs:range ?C. ?S ?P ?O} => {?O a ?C}.",
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


def apply_catalyst_napespace_manager(graph):
    # setup the RDF graph to be parsed
    npm = NamespaceManager(Graph())
    npm.bind("owl", "http://www.w3.org/2002/07/owl#")
    npm.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    npm.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    npm.bind("xsd", "http://www.w3.org/2001/XMLSchema#")
    npm.bind("trig", "http://www.w3.org/2004/03/trix/rdfg-1/")
    npm.bind("foaf", "http://xmlns.com/foaf/0.1/")
    npm.bind("dcterms", "http://purl.org/dc/terms/")
    npm.bind("sioc", "http://rdfs.org/sioc/ns#")
    npm.bind("oa", "http://www.openannotation.org/ns/")
    npm.bind("idea", "http://purl.org/catalyst/idea#")
    npm.bind("ibis", "http://purl.org/catalyst/ibis#")
    npm.bind("assembl", "http://purl.org/assembl/core#")
    npm.bind("catalyst", "http://purl.org/catalyst/core#")
    npm.bind("version", "http://purl.org/catalyst/version#")
    npm.bind("vote", "http://purl.org/catalyst/vote#")
    npm.bind("eg_site", "http://www.assembl.net/")
    npm.bind("eg_d1", "http://www.assembl.net/discussion/1/")
    npm.bind("kmieg", "http://maptesting.kmi.open.ac.uk/api/")
    npm.bind("kmiegnodes", "http://maptesting.kmi.open.ac.uk/api/nodes/")
    graph.namespace_manager=npm
    for c in graph.contexts():
        c.namespace_manager=npm
    
def catalyst_graph_for(file):
    if file.startswith('/'):
        file = 'file://'+file
    logging.info("InferenceStore catalyst_graph_for started")
        
    quads = jsonld.to_rdf(file, {'format': 'application/nquads'})
    logging.info("InferenceStore JSON-LD loaded")

    g = ConjunctiveGraph()
    apply_catalyst_napespace_manager(g)
    g.parse(data=quads, format='nquads')
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
