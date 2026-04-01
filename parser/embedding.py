def build_embedding_text(node):
    parts = []
    
    if node["type"] == "FUNCTION":
        parts.append(f"function {node['name']}")
        parts.append(node["name"].replace("_", " "))
        parts.append(f"this function is about {node['name'].replace('_', ' ')}")

        if node.get("docstring"):
            parts.append(node["docstring"])

    elif node["type"] == "CLASS":
        parts.append(f"class {node['name']}")
        parts.append(node["name"].replace("_", " "))

        if node.get("docstring"):
            parts.append(node["docstring"])

    elif node["type"] == "MODULE":
        parts.append(f"module {node['name']}")

    # Add first few lines of source as context
    source_preview = "\n".join(
        line for line in node.get("source_code", "").splitlines()[:8]
        if line.strip()
    )

    if source_preview:
        parts.append(source_preview)

    return "\n".join(parts)

def enrich_nodes_with_embeddings(nodes):
    """Add embedding_text field to every node in place."""
    for node in nodes:
        node["embedding_text"] = build_embedding_text(node)
    return nodes