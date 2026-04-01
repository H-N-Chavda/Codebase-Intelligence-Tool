import os

SKIP_DIRS = {"__pycache__", ".git", "venv", ".venv", "node_modules", "test", "tests"}

def discover_files(root_dir):
    py_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename.endswith(".py"):
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir)
                py_files.append({"path": full_path, "rel_path": rel_path})
    return py_files