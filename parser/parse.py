import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def normalise_id(rel_path):
    return rel_path.replace("\\", "/")

def get_docstring(node, source):
    for child in node.children:
        if child.type == "block":
            for stmt in child.children:
                if stmt.type == "expression_statement":
                    for s in stmt.children:
                        if s.type == "string":
                            return source[s.start_byte:s.end_byte].strip('"""').strip("'''").strip()
    return ""

def extract_nodes(file_info, source_bytes):
    source = source_bytes.decode("utf-8", errors="replace")
    tree = parser.parse(source_bytes)
    nodes = []
    module_id = f"module::{normalise_id(file_info['rel_path'])}"
    
    nodes.append({
        "id": module_id,
        "type": "MODULE",
        "name": file_info['rel_path'].replace("\\", ".").replace("/", ".").removesuffix(".py"),
        "file": file_info['rel_path'],
        "line_start": 1,
        "line_end": source.count("\n") + 1,
        "docstring": "",
        "source_code": source,
        "embedding_text": source[:300],
    })
    
    def walk(node):
        # CLASS
        if node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")

                nodes.append({
                    "id": f"class::{normalise_id(file_info['rel_path'])}::{name}",
                    "type": "CLASS",
                    "name": name,
                    "file": normalise_id(file_info['rel_path']),
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "docstring": get_docstring(node, source),
                    "source_code": source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace"),
                    "embedding_text": f"class {name}\n{get_docstring(node, source)}",
                })

        # FUNCTION
        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                parent = node.parent

                # Skip nested functions (like your internal walk)
                if parent and parent.type == "block" and parent.parent and parent.parent.type == "function_definition":
                    return
                nodes.append({
                    "id": f"fn::{normalise_id(file_info['rel_path'])}::{name}",
                    "type": "FUNCTION",
                    "name": name,
                    "file": normalise_id(file_info['rel_path']),
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "docstring": get_docstring(node, source),
                    "source_code": source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace"),
                    "embedding_text": f"function {name}\n{get_docstring(node, source)}",
                })

        # ALWAYS traverse children
        for i in range(node.child_count):
            child = node.child(i)
            if child is not None:
                walk(child)

    walk(tree.root_node)
    
    # Remove duplicate nodes by ID
    unique = {}
    for n in nodes:
        unique[n["id"]] = n

    return list(unique.values())