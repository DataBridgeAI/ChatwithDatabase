import os

EXCLUDE_DIRS = {'venv', '.git', 'node_modules', '__pycache__', '.mypy_cache', '.pytest_cache', 'dist', 'build'}
EXCLUDE_FILES = {'.DS_Store'}

def print_tree(path='.', prefix=''):
    entries = sorted(os.listdir(path))
    entries = [e for e in entries if e not in EXCLUDE_DIRS and e not in EXCLUDE_FILES]
    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = '└── ' if i == len(entries) - 1 else '├── '
        print(prefix + connector + entry)
        if os.path.isdir(full_path):
            extension = '    ' if i == len(entries) - 1 else '│   '
            print_tree(full_path, prefix + extension)

# Run the script from your project root
print_tree()
