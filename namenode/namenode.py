import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import json
from flask import Flask, request, jsonify
from namenode.metadata_store import MetadataStore
from namenode.replication_manager import ReplicationManager
from core.config import Config
from core.logger import log

metadata_store = MetadataStore(Config.METADATA_FILE)
replication_manager = ReplicationManager(metadata_store)

class NameNode:
    def __init__(self, metadata_file="metadata/files_metadata.json", replication_factor=2, port=8000):
        self.metadata = MetadataStore(metadata_file)
        self.replication_manager = ReplicationManager(self.metadata)
        self.replication_factor = replication_factor
        self.datanodes = {}
        self.port = port
        log(f"NameNode initialized on port {self.port}.")

    def register_datanode(self, node_id, ip, port):
        self.datanodes[node_id] = {
            "ip": ip,
            "port": port,
            "status": "active"
        }
        log(f"✅ DataNode {node_id} registered at {ip}:{port}")

    import time  # ensure time is imported at the top

    def receive_heartbeat(self, node_id):
     if node_id in self.datanodes:
        self.datanodes[node_id]['status'] = 'active'
        self.datanodes[node_id]['last_heartbeat'] = time.time()  # ✅ Save current time
        log(f"💓 Heartbeat received from DataNode {node_id}")
     else:
        log(f"⚠️ Unknown DataNode {node_id} tried to send heartbeat", level="warning")

    def allocate_blocks(self, file_name, file_size, block_size):
        num_blocks = (file_size + block_size - 1) // block_size
        block_info = self.replication_manager.assign_blocks(
            file_name, num_blocks, self.replication_factor, self.datanodes)
        self.metadata.save_metadata()
        return block_info

    def get_file_blocks(self, file_name):
        return self.metadata.get_file_blocks(file_name)

    def list_files(self):
        return self.metadata.list_all_files()

    def remove_file(self, file_name):
        self.metadata.remove_file(file_name)
        self.metadata.save_metadata()
        log(f"🗑️ File '{file_name}' removed from metadata.")

    def get_active_datanodes(self):
        return {
            node_id: info
            for node_id, info in self.datanodes.items()
            if info['status'] == 'active'
        }

    def start(self):
        from time import sleep
        from core.logger import log
        log("✅ NameNode is live and running.")
        while True:
            sleep(10)
            log("💤 Waiting for heartbeat or client request...")
    def list_files(self):
     """
     Return a list of all file names in the system.
     """
     return list(self.metadata.metadata.keys())


# === Flask Server Setup ===
app = Flask(__name__)
namenode = NameNode()

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    node_id = data.get("node_id")
    ip = data.get("ip")
    port = data.get("port")
    if node_id and ip and port:
        namenode.register_datanode(node_id, ip, port)
        return jsonify({"status": "registered"}), 200
    else:
        return jsonify({"error": "Missing required fields"}), 400

@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.json
    node_id = data.get("node_id")
    if node_id:
        namenode.receive_heartbeat(node_id)
        return jsonify({"status": "alive"}), 200
    else:
        return jsonify({"error": "Missing node_id"}), 400

@app.route("/allocate_blocks", methods=["POST"])
def allocate_blocks():
    data = request.json
    file_name = data.get("file_name")
    file_size = data.get("file_size")
    block_size = data.get("block_size")
    if not file_name or not file_size or not block_size:
        log("Missing file_name, file_size, or block_size", level="error")
        return jsonify({"error": "Missing file_name, file_size, or block_size"}), 400
    try:
        block_info = namenode.allocate_blocks(file_name, file_size, block_size)
        log(f"Allocated blocks for file '{file_name}'")
        return jsonify(block_info), 200
    except Exception as e:
        log(f"Error allocating blocks: {e}", level="error")
        return jsonify({"error": str(e)}), 500

@app.route("/files", methods=["GET"])
def list_files():
    files = namenode.list_files()
    return jsonify(files), 200

@app.route("/file_blocks", methods=["GET"])
def get_file_blocks_api():
    file_name = request.args.get("file_name")
    if not file_name:
        log("Missing file_name", level="error")
        return jsonify({"error": "Missing file_name"}), 400
    blocks = namenode.get_file_blocks(file_name)
    return jsonify(blocks), 200

@app.route("/assign_blocks", methods=["POST"])
def assign_blocks():
    data = request.get_json()
    file_name = data.get("file_name")
    num_blocks = data.get("num_blocks")

    if not file_name or not num_blocks:
        return jsonify({"error": "Missing file_name or num_blocks"}), 400

    log(f"📦 Assigning {num_blocks} blocks for '{file_name}'")

    try:
        active_datanodes = namenode.get_active_datanodes()

        # Add 'host' and 'port' keys to match expected input by ReplicationManager
        for node_id, info in active_datanodes.items():
            info["host"] = info["ip"]

        block_info = namenode.replication_manager.assign_blocks(
            file_name=file_name,
            num_blocks=num_blocks,
            replication_factor=namenode.replication_factor,
            datanodes=active_datanodes
        )
        namenode.metadata.save_metadata()
        return jsonify({"blocks": block_info}), 200
    except Exception as e:
        log(f"Error assigning blocks: {e}", level="error")
        return jsonify({"error": str(e)}), 500

@app.route("/get_file_blocks", methods=["GET"])
def get_file_blocks_route():
    file_name = request.args.get("file_name")
    if not file_name:
        return jsonify({"error": "Missing file_name"}), 400

    blocks = namenode.get_file_blocks(file_name)
    if not blocks:
        return jsonify({"error": "File not found"}), 404

    return jsonify({"blocks": blocks}), 200

if __name__ == "__main__":
    log("🚀 Starting NameNode HTTP server on http://localhost:8000 ...")
    app.run(host="0.0.0.0", port=8000)