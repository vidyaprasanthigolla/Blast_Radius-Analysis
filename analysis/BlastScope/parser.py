import ast
import os

class CodeVisitor(ast.NodeVisitor):
    def __init__(self, module_name):
        self.module_name = module_name
        self.nodes = [] # {id, type, label}
        self.edges = [] # {source, target, type}
        
        self.current_parent = module_name
        self.imports = {}

    def add_node(self, node_id, n_type, label):
        self.nodes.append({"id": node_id, "type": n_type, "label": label})
        
    def add_edge(self, source, target, rel_type):
        self.edges.append({"source": source, "target": target, "type": rel_type})

    def visit_Import(self, node):
        for alias in node.names:
            self.imports[alias.asname or alias.name] = alias.name
            self.add_node(alias.name, "module", alias.name)
            self.add_edge(self.module_name, alias.name, "imports")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        mod = node.module or ""
        # Resolve explicit relative imports
        if node.level > 0:
            parts = self.module_name.split('.')
            if len(parts) >= node.level:
                base = '.'.join(parts[:-node.level])
                mod = f"{base}.{mod}" if mod else base

        if mod:
            self.add_node(mod, "module", mod)
            self.add_edge(self.module_name, mod, "imports")
            
        for alias in node.names:
            full_name = f"{mod}.{alias.name}" if mod else alias.name
            self.imports[alias.asname or alias.name] = full_name
            self.add_node(full_name, "component", alias.name)
            self.add_edge(self.module_name, full_name, "imports")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        class_id = f"{self.module_name}.{node.name}"
        self.add_node(class_id, "class", node.name)
        self.add_edge(self.current_parent, class_id, "contains")
        
        old_parent = self.current_parent
        self.current_parent = class_id
        self.generic_visit(node)
        self.current_parent = old_parent

    def visit_FunctionDef(self, node):
        func_id = f"{self.current_parent}.{node.name}"
        self.add_node(func_id, "function", node.name)
        self.add_edge(self.current_parent, func_id, "contains")
        
        old_parent = self.current_parent
        self.current_parent = func_id
        self.generic_visit(node)
        self.current_parent = old_parent

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            target = node.func.id
            if target in self.imports:
                target = self.imports[target]
            self.add_edge(self.current_parent, target, "calls")
        elif isinstance(node.func, ast.Attribute):
            target = node.func.attr
            self.add_edge(self.current_parent, target, "calls")
        self.generic_visit(node)


def parse_directory(directory_path):
    all_nodes = []
    all_edges = []
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory_path)
                module_name = dir_to_module(rel_path)
                
                all_nodes.append({"id": module_name, "type": "module", "label": module_name})
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read(), filename=filepath)
                        visitor = CodeVisitor(module_name)
                        visitor.visit(tree)
                        all_nodes.extend(visitor.nodes)
                        all_edges.extend(visitor.edges)
                    except SyntaxError:
                        pass
                        
    # Deduplicate nodes by ID
    unique_nodes = {n['id']: n for n in all_nodes}.values()
    return list(unique_nodes), all_edges

def dir_to_module(rel_path):
    # e.g., sample_repo\models.py -> sample_repo.models
    return rel_path.replace(os.sep, '.')[:-3]
