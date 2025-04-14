# namenode/metadata_store.py

import os
import json
from core.logger import log


class MetadataStore:
    def __init__(self, metadata_file):
        self.metadata_file = metadata_file
        self.files = {}  # Structure: {filename: [ {block_id, datanodes: [node_ids]} ]}
        self._load_metadata()

    def _load_metadata(self):
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r") as f:
                    self.files = json.load(f)
                    log("Metadata loaded successfully.")
            except json.JSONDecodeError:
                log("Metadata file is corrupted. Starting with empty metadata.", level="warning")
                self.files = {}
        else:
            os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
            self._save_metadata()

    def _save_metadata(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self.files, f, indent=4)
            log("Metadata saved.")

    def save_metadata(self):
        self._save_metadata()

    def add_file_blocks(self, file_name, block_list):
        self.files[file_name] = block_list
        log(f"Added metadata for file: {file_name}")

    def get_file_blocks(self, file_name):
        return self.files.get(file_name, [])

    def list_all_files(self):
        return list(self.files.keys())

    def remove_file(self, file_name):
        if file_name in self.files:
            del self.files[file_name]
            log(f"File '{file_name}' metadata removed.")
        else:
            log(f"File '{file_name}' not found in metadata.", level="warning")