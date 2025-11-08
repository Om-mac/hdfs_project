import sys
import os
import time
import json
from flask import Flask, request, jsonify

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from namenode.metadata_store import MetadataStore
from namenode.replication_manager import ReplicationManager
from core.config import Config
from core.logger import log

HEARTBEAT_TIMEOUT = 30  # seconds

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
            "status": "active",
            "last_heartbeat": time.time()
        }
        log(f"✅ DataNode {node_id} registered at {ip}:{port}")

    def receive_heartbeat(self, node_id):
        if node_id in self.datanodes:
            self.datanodes[node_id]['status'] = 'active'
            self.datanodes[node_id]['last_heartbeat'] = time.time()
            log(f"💓 Heartbeat received from DataNode {node_id}")
        else:
            log(f"⚠️ Unknown DataNode {node_id} tried to send heartbeat", level="warning")

    def cleanup_datanodes(self):
        current_time = time.time()
        for node_id, info in self.datanodes.items():
            if current_time - info.get("last_heartbeat", 0) > HEARTBEAT_TIMEOUT:
                info["status"] = "inactive"
                log(f"⛔ DataNode {node_id} marked as inactive due to missed heartbeat")

    def allocate_blocks(self, file_name, file_size, block_size):
        try:
            file_size = int(file_size)
            block_size = int(block_size)
        except ValueError:
            raise ValueError("file_size and block_size must be integers")

        num_blocks = (file_size + block_size - 1) // block_size
        block_info = self.replication_manager.assign_blocks(
            file_name, num_blocks, self.replication_factor, self.get_active_datanodes())
        self.metadata.save_metadata()
        return block_info

    def get_file_blocks(self, file_name):
        return self.metadata.get_file_blocks(file_name)

    def list_files(self):
        return list(self.metadata.metadata.keys())

    def remove_file(self, file_name):
        self.metadata.remove_file(file_name)
        self.metadata.save_metadata()
        log(f"🗑️ File '{file_name}' removed from metadata.")

    def get_active_datanodes(self):
        self.cleanup_datanodes()
        return {
            node_id: {
                **info,
                "host": info["ip"]  # Compatibility with replication manager
            }
            for node_id, info in self.datanodes.items()
            if info.get('status') == 'active'
        }


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
    return jsonify({"error": "Missing required fields"}), 400

@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.json
    node_id = data.get("node_id")
    if node_id:
        namenode.receive_heartbeat(node_id)
        return jsonify({"status": "alive"}), 200
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
        log(f"📦 Allocated blocks for file '{file_name}'")
        return jsonify({"blocks": block_info}), 200
    except Exception as e:
        log(f"❌ Error allocating blocks: {e}", level="error")
        return jsonify({"error": str(e)}), 500

@app.route("/files", methods=["GET"])
def list_files():
    files = namenode.list_files()
    return jsonify(files), 200

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