import sys
from parser.discover import discover_files
from parser.parse import extract_nodes
from parser.relationships import extract_edges
from parser.resolve import resolve_cross_file_calls
from parser.embedding import enrich_nodes_with_embeddings

def run(root_dir):
    all_nodes, all_edges = [], []
    files = discover_files(root_dir)

    print(f"\nFound {len(files)} Python files\n")

    for file_info in files:
        try:
            with open(file_info["path"], "rb") as f:
                source_bytes = f.read()

            nodes = extract_nodes(file_info, source_bytes)
            edges = extract_edges(file_info, nodes, source_bytes)

            all_nodes.extend(nodes)
            all_edges.extend(edges)

        except Exception as e:
            print(f"Error parsing {file_info['path']}: {e}")

    all_edges = resolve_cross_file_calls(all_edges, all_nodes, root_dir)
    all_nodes = enrich_nodes_with_embeddings(all_nodes)

    print("\nSUMMARY")
    print(f"Total Nodes: {len(all_nodes)}")
    print(f"Total Edges: {len(all_edges)}")

    modules = [n for n in all_nodes if n["type"] == "MODULE"]
    classes = [n for n in all_nodes if n["type"] == "CLASS"]
    functions = [n for n in all_nodes if n["type"] == "FUNCTION"]

    print(f"\nModules ({len(modules)}):")
    for m in modules:
        print(f"  - {m['name']}")

    print(f"\nClasses ({len(classes)}):")
    for c in classes:
        print(f"  - {c['name']}")

    print(f"\nFunctions ({len(functions)}):")
    for f in functions:
        print(f"  - {f['name']}")

    print("\nFunctions per module:")
    for m in modules:
        mod_id = f"module::{m['file'].replace('\\', '/')}"
        funcs = [
            e["to"] for e in all_edges
            if e["type"] == "CONTAINS" and e["from"] == mod_id
        ]

        print(f"\n{m['name']}:")
        for f in funcs:
            print(f"  - {f.split('::')[-1]}")

    print("\nSample Relationships:")
    for e in all_edges[:10]:
        print(f"  {e['type']}: {e['from']} -> {e['to']}")

    print("\nDone.\n")


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    run(root)