import networkx as nx
from llm_integration import generate_ai_explanation

def analyze_blast_radius(G, change_intent, changed_node_id):
    if not G.has_node(changed_node_id):
        # Fallback to search inside node names
        matches = [n for n in G.nodes if changed_node_id in n]
        if not matches:
            return {"error": f"Node '{changed_node_id}' not found in codebase graph."}
        changed_node_id = matches[0]
        
    rev_G = G.reverse()
    descendants = nx.descendants(rev_G, changed_node_id)
    impacted = []
    
    impacted.append({
        "id": changed_node_id,
        "type": G.nodes[changed_node_id].get("type", "unknown"),
        "impact_level": "Changed",
        "explanation": f"Modified Component. Intent: {change_intent}"
    })
    
    for node in descendants:
        distance = nx.shortest_path_length(rev_G, source=changed_node_id, target=node)
        impact_level = "Direct" if distance == 1 else "Indirect"
        node_type = G.nodes[node].get("type", "unknown")
        
        category = "Code Impact"
        if "api" in node.lower(): category = "API Contract Risk"
        elif "model" in node.lower() or "dto" in node.lower(): category = "Data Structure Risk"
        elif "test" in node.lower(): category = "Test Breakage"
        
        reasoning = generate_ai_explanation(changed_node_id, node, change_intent, distance, category)
            
        impacted.append({
            "id": node,
            "type": node_type,
            "impact_level": impact_level,
            "category": category,
            "explanation": reasoning
        })
        
    return {
        "changed_node": changed_node_id,
        "total_impacted": len(impacted) - 1,
        "impacts": impacted,
        "subgraph_nodes": [changed_node_id] + list(descendants)
    }
