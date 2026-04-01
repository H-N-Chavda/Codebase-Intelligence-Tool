import jedi

def build_symbol_table(nodes):
    """Map fully-qualified names to node IDs for fast lookup."""
    table = {}
    for node in nodes:
        key = f"{node['file']}::{node['name']}"
        table[key] = node["id"]
    return table


def resolve_cross_file_calls(edges, nodes, root_dir):
    """
    Use Jedi to resolve which module a called function actually lives in,
    then update CALLS edges to point at the correct node ID.
    """
    # Build a quick lookup: file -> list of function nodes in that file
    file_to_nodes = {}
    for node in nodes:
        file_to_nodes.setdefault(node["file"], []).append(node)

    resolved_edges = []
    for edge in edges:
        if edge["type"] != "CALLS":
            resolved_edges.append(edge)
            continue

        # Try to resolve using Jedi — best-effort, fall through on failure
        try:
            # edge["from"] looks like fn::blog/models.py::save
            parts = edge["from"].split("::")
            if len(parts) < 2:
                resolved_edges.append(edge)
                continue

            rel_path = parts[1]
            full_path = f"{root_dir}/{rel_path}"

            script = jedi.Script(path=full_path)
            # Jedi resolution is line-based; this is a lightweight pass
            # For a full implementation, track call line numbers in Step 4
            resolved_edges.append(edge)  # placeholder — Jedi call goes here

        except Exception:
            resolved_edges.append(edge)  # graceful fallback

    return resolved_edges