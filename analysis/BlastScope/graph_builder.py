import networkx as nx

def build_graph(nodes, edges):
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node['id'], type=node.get('type', 'unknown'), label=node.get('label', node['id']))
        
    for edge in edges:
        source = edge['source']
        target = edge['target']
        rel_type = edge['type']
        
        if not G.has_node(target):
            G.add_node(target, type='external', label=target)
        if not G.has_node(source):
            G.add_node(source, type='external', label=source)
            
        G.add_edge(source, target, type=rel_type)
    return G

def get_graph_data(G):
    elements = []
    for node, data in G.nodes(data=True):
        elements.append({
            "data": {
                "id": node,
                "label": data.get("label", node),
                "type": data.get("type", "unknown")
            }
        })
    for u, v, data in G.edges(data=True):
        elements.append({
            "data": {
                "source": u,
                "target": v,
                "label": data.get("type", "")
            }
        })
    return elements
