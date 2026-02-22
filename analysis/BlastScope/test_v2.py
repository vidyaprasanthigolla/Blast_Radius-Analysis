import json
from parser import parse_directory
from graph_builder import build_graph
from analyzer import analyze_blast_radius

nodes, edges = parse_directory("sample_repo")
G = build_graph(nodes, edges)
result = analyze_blast_radius(G, "Adding 'status' enum to InvoiceDTO", "sample_repo.models.InvoiceDTO")

print("TEST SUCCESS V2")
print(json.dumps(result, indent=2))
