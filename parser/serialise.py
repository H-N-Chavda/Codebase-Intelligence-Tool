import json

def save_output(nodes, edges, output_dir="output"):
    import os
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/nodes.json", "w") as f:
        json.dump(nodes, f, indent=2)
    with open(f"{output_dir}/edges.json", "w") as f:
        json.dump(edges, f, indent=2)
    print(f"Saved {len(nodes)} nodes and {len(edges)} edges.")