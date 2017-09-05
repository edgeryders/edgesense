import sys
from os import path
from os.path import exists, abspath
import requests
import logging
import cStringIO as StringIO
from abc import abstractmethod

import rdflib
from rdflib import Graph, URIRef, RDF, ConjunctiveGraph, RDFS, OWL
from rdflib.namespace import NamespaceManager, Namespace

from simplejson import load, dump
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

    def get_graph(self):
        return Graph()

    def clear_graph(self):
        graph = self.ontology
        if isinstance(graph, ConjunctiveGraph):
            ctxs = list(self.ontology.contexts())
            for ctx in ctxs:
                self.ontology.remove_context()
        else:
            triples = list(graph.triples((None, None, None)))
            for triple in triples:
                graph.remove(triple)
        assert not len(graph)

    @abstractmethod
    def load_ontology(self, reload=False):
        self.ontology = self.get_graph()
        if reload:
            self.clear_graph()
        if not len(self.ontology):
            self.add_ontologies()

    def as_file(self, uri):
        if uri[0] != '/' and ':' not in uri:
            uri = self.ontology_root + "/" + uri
        if uri.startswith('http'):
            r = requests.get(uri)
            assert r.ok
            return r.content
        elif uri.startswith('/' or uri.startswith('file:')):
            if uri.startswith('file:'):
                uri = uri[5:]
            while uri.startswith('//'):
                uri = uri[1:]
            assert exists(uri), uri + " does not exist"
            return open(uri)
        else:
            raise ValueError

    def add_ontologies(self, rules=CATALYST_RULES):
        for r in rules:
            self.add_ontology(self.as_file(r))

    def add_ontology(self, source, format='turtle'):
        self.ontology.parse(source, format=format)

    def getSubClasses(self, cls):
        return self.ontology.transitive_subjects(RDFS.subClassOf, cls)

    def getSuperClasses(self, cls):
        return self.ontology.transitive_objects(cls, RDFS.subClassOf)

    def getSubProperties(self, cls):
        return self.ontology.transitive_subjects(RDFS.subPropertyOf, cls)

    def getSuperProperties(self, cls):
        return self.ontology.transitive_objects(cls, RDFS.subPropertyOf)

    @abstractmethod
    def get_inference(self, graph):
        return graph


class SimpleInferenceStore(InferenceStore):
    """A simple inference engine that adds class closures"""
    def add_ontologies(self, rules=CATALYST_RULES):
        super(SimpleInferenceStore, self).add_ontologies(rules)
        self.enrichOntology()

    @staticmethod
    def addTransitiveClosure(graph, property):
        roots = set(graph.subjects(
            property, None))
        for r in roots:
            for o in list(graph.transitive_objects(r, property)):
                t = (r, property, o)
                if t not in graph:
                    graph.add(t)

    @staticmethod
    def addInstanceStatements(graph, root_class, sub_property):
        class_classes = set(graph.transitive_subjects(sub_property, root_class))
        class_classes.remove(root_class)
        classes = set()
        for class_class in class_classes:
            superclasses = set(graph.transitive_objects(class_class, sub_property))
            superclasses.remove(class_class)
            instances = graph.subjects(RDF.type, class_class)
            for instance in instances:
                for superclass in superclasses:
                    t = (instance, RDF.type, superclass)
                    if t not in graph:
                        graph.add(t)

    def enrichOntology(self):
        graph = self.ontology
        self.addTransitiveClosure(graph, RDFS.subPropertyOf)
        self.addTransitiveClosure(graph, RDFS.subClassOf)
        self.addInstanceStatements(graph, RDFS.Class, RDFS.subClassOf)
        self.addInstanceStatements(graph, RDF.Property, RDFS.subPropertyOf)

    def add_inheritance(self, graph, root_class, sub_property):
        changes = False
        classes = self.ontology.subjects(RDF.type, root_class)
        for cls in classes:
            superclasses = set(self.ontology.transitive_objects(cls, sub_property))
            superclasses.remove(cls)
            for instance in graph.subjects(RDF.type, cls):
                for sup_cls in superclasses:
                    t = (instance, RDF.type, sup_cls)
                    if t not in graph:
                        changes = True
                        graph.add(t)
        return changes

    def add_inverses(self, graph):
        changes = False
        for (p1, _, p2) in self.ontology.triples(
                (None, OWL.inverseOf, None)):
            for (s, p, o) in graph.triples((None, p1, None)):
                t = (o, p2, s)
                if t not in graph:
                    graph.add(t)
                    changes = True
            for (s, p, o) in graph.triples((None, p2, None)):
                t = (o, p1, s)
                if t not in graph:
                    graph.add(t)
                    changes = True
        return changes

    def get_inference(self, graph):
        first = changes = True
        while first or changes:
            if first or changes:
                # {?P @has owl:inverseOf ?I. ?S ?P ?O} => {?O ?I ?S}.
                changes = self.add_inverses(graph)
            if first or changes:
                # {?P @has rdfs:subPropertyOf ?R. ?S ?P ?O} => {?S ?R ?O}.
                # {?P @has owl:subPropertyOf ?R. ?S ?P ?O} => {?S ?R ?O}.
                changes = self.add_inheritance(graph, RDF.Property, RDFS.subPropertyOf)
            first = False
            # loop because inheritance could add inverses.
        # {?P @has rdfs:domain ?C. ?S ?P ?O} => {?S a ?C}.
        for (p, _, c) in self.ontology.triples((None, RDFS.domain, None)):
            rs = {s for (s, _, o) in graph.triples((None, p, None))}
            for r in rs:
                t = (r, RDF.type, c)
                if t not in graph:
                    graph.add(t)
        # {?P @has rdfs:range ?C. ?S ?P ?O} => {?O a ?C}.
        for (p, _, c) in self.ontology.triples((None, RDFS.range, None)):
            rs = {o for (s, _, o) in graph.triples((None, p, None))}
            for r in rs:
                t = (r, RDF.type, c)
                if t not in graph:
                    graph.add(t)
        self.add_inheritance(graph, RDFS.Class, RDFS.subClassOf)


STORE = None


def get_inference_store():
    global STORE
    if STORE is None:
        STORE = SimpleInferenceStore()
        STORE.load_ontology()
    return STORE

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

    # get the inference engine
    get_inference_store().get_inference(g)
    logging.info("InferenceStore inference graph loaded")

    return g
