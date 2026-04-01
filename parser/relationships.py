from tree_sitter import Parser
import tree_sitter_python as tspython
from tree_sitter import Language

PY_LANGUAGE = Language(tspython.language())

def normalise_id(rel_path):
    return rel_path.replace("\\", "/")

def extract_edges(file_info, nodes, source_bytes):
    source = source_bytes.decode("utf-8", errors="replace")
    parser_local = Parser(PY_LANGUAGE)
    tree = parser_local.parse(source_bytes)
    edges = []
    module_id = f"module::{normalise_id(file_info['rel_path'])}"
    
    def walk(node, parent_class=None):
        if node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")

            class_id = f"class::{normalise_id(file_info['rel_path'])}::{name}"
            edges.append({"type": "CONTAINS", "from": module_id, "to": class_id})

            for child in node.children:
                walk(child, parent_class=name)

        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")

            parent = node.parent
            grandparent = parent.parent if parent else None

            # ✅ Only allow:
            # - top-level functions
            # - class methods
            is_top_level = parent and parent.type == "module"
            is_class_method = grandparent and grandparent.type == "class_definition"

            if is_top_level or is_class_method:
                fn_id = f"fn::{normalise_id(file_info['rel_path'])}::{name}"

                if parent_class:
                    class_id = f"class::{normalise_id(file_info['rel_path'])}::{parent_class}"
                    edges.append({"type": "DEFINES_METHOD", "from": class_id, "to": fn_id})
                else:
                    edges.append({"type": "CONTAINS", "from": module_id, "to": fn_id})

            for child in node.children:
                walk(child, parent_class=parent_class)

        elif node.type == "import_from_statement":
            mod_node = node.child_by_field_name("module_name")
            if mod_node:
                imported_mod = source[mod_node.start_byte:mod_node.end_byte]
                as_path = imported_mod.lstrip(".").replace(".", "/") + ".py"
                edges.append({"type": "IMPORTS", "from": module_id, "to": f"module::{as_path}"})

        else:
            for child in node.children:
                walk(child, parent_class=parent_class)
    
    walk(tree.root_node)
    return edges