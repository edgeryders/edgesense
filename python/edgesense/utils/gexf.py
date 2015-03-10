from datetime import datetime
import itertools
import networkx as nx
from networkx.utils import open_file, make_str
try:
    from xml.etree.cElementTree import Element, ElementTree, tostring
except ImportError:
    try:
        from xml.etree.ElementTree import Element, ElementTree, tostring
    except ImportError:
        pass

from networkx.readwrite.gexf import GEXFWriter

@open_file(1,mode='wb')
def save_gexf(graph, filename):
    # copy the graph to make it
    G = graph.copy()
    
    # cleanup and prepare the graph
    for node in G.nodes():
        prepare_gefx_attributes(G.node[node])
    
    for node in G.nodes_iter():
        for neighbour in G[node].keys():
            for edge_attrs in G[node][neighbour].values():
                prepare_gefx_attributes(edge_attrs)
    
    # write the graph to the file
    writer = GEXFExporter(mode='static')
    writer.add_graph(G)
    writer.adjust_format()
    writer.write(filename)
    
def prepare_gefx_attributes(dict):
    for k, v in dict.items():
        if v == None:
            # Cleanup the attributes with None value
            del dict[k]
        elif k == 'ts' or k == 'created_ts':
            # Add start attribute
            dict['start'] = datetime.fromtimestamp(v).isoformat()

class GEXFExporter(GEXFWriter):
    def adjust_format(self):
        self.graph_element.set('timeformat', 'string')
        for a in self.graph_element.findall("attributes"):
            a.set('timeformat', 'string')
                
    def add_nodes(self, G, graph_element):
        nodes_element = Element('nodes')
        for node,data in G.nodes_iter(data=True):
            node_data=data.copy()
            node_id = make_str(node_data.pop('id', node))
            kw={'id':node_id}
            label = make_str(node_data.pop('label', node))
            kw['label']=label
            try:
                pid=node_data.pop('pid')
                kw['pid'] = make_str(pid)
            except KeyError:
                pass
            
            # Adds the start / end from the node data
            try:
                start=node_data.pop('start')
                kw['start'] = make_str(start)
            except KeyError:
                pass
            try:
                end=node_data.pop('end')
                kw['end'] = make_str(end)
            except KeyError:
                pass
            
            # add node element with attributes
            node_element = Element("node", **kw)
            
            # add node element and attr subelements
            default=G.graph.get('node_default',{})
            node_data=self.add_parents(node_element, node_data)
            if self.version=='1.1':
                node_data=self.add_slices(node_element, node_data)
            else:
                node_data=self.add_spells(node_element, node_data)
            node_data=self.add_viz(node_element,node_data)
            node_data=self.add_attributes("node", node_element,
                                          node_data, default)
            nodes_element.append(node_element)
        
        graph_element.append(nodes_element)
    
    def add_edges(self, G, graph_element):
        def edge_key_data(G):
            # helper function to unify multigraph and graph edge iterator
            if G.is_multigraph():
                for u,v,key,data in G.edges_iter(data=True,keys=True):
                    edge_data=data.copy()
                    edge_data.update(key=key)
                    edge_id=edge_data.pop('id',None)
                    if edge_id is None:
                        edge_id=next(self.edge_id)
                    yield u,v,edge_id,edge_data
            else:
                for u,v,data in G.edges_iter(data=True):
                    edge_data=data.copy()
                    edge_id=edge_data.pop('id',None)
                    if edge_id is None:
                        edge_id=next(self.edge_id)
                    yield u,v,edge_id,edge_data
        
        edges_element = Element('edges')
        for u,v,key,edge_data in edge_key_data(G):
            kw={'id':make_str(key)}
            try:
                edge_weight=edge_data.pop('weight')
                kw['weight']=make_str(edge_weight)
            except KeyError:
                pass
            try:
                edge_type=edge_data.pop('type')
                kw['type']=make_str(edge_type)
            except KeyError:
                pass
            
            # Adds the start / end from the node data
            try:
                start=edge_data.pop('start')
                kw['start'] = make_str(start)
            except KeyError:
                pass
            try:
                end=edge_data.pop('end')
                kw['end'] = make_str(end)
            except KeyError:
                pass
            
            source_id = make_str(G.node[u].get('id', u))
            target_id = make_str(G.node[v].get('id', v))
            edge_element = Element("edge",
                                   source=source_id,target=target_id,
                                   **kw)
            default=G.graph.get('edge_default',{})
            edge_data=self.add_viz(edge_element,edge_data)
            edge_data=self.add_attributes("edge", edge_element,
                                          edge_data, default)
            edges_element.append(edge_element)
        graph_element.append(edges_element)

