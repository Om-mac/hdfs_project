

import uuid
import json
import os


def generate_id():
    """Generates a unique ID (used for blocks, nodes, etc.)."""
    return str(uuid.uuid4())


def read_json(filepath):
    """Reads and returns JSON data from a file."""
    if not os.path.exists(filepath):
        return {}

    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def write_json(filepath, data):
    """Writes JSON data to a file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)