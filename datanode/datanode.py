import argparse
import threading
import requests
from flask import Flask, request, jsonify
from time import sleep
from core.logger import log
from datanode.storage import BlockStorage
from datanode.heartbeat import HeartbeatManager

app = Flask(__name__)
data_node = None 
class DataNode:
    def __init__(self, datanode_id, namenode_url, storage_path, ip="127.0.0.1", port=5001):
        self.datanode_id = datanode_id
        self.namenode_url = namenode_url
        self.storage = BlockStorage(storage_path)
        self.heartbeat_manager = HeartbeatManager(self.datanode_id, self.namenode_url)
        self.ip = ip
        self.port = port

        self._register_with_namenode()

    def _register_with_namenode(self):
        try:
            response = requests.post(
                f"{self.namenode_url}/register",
                json={
                    "node_id": self.datanode_id,
                    "ip": self.ip,
                    "port": self.port
                }
            )
            if response.status_code == 200:
                log(f"✅ Registered with NameNode as {self.datanode_id}")
            else:
                log(f"❌ Failed to register with NameNode. Status code: {response.status_code}", level="error")
        except Exception as e:
            log(f"❌ Error registering with NameNode: {e}", level="error")

    def start_heartbeat(self):
        thread = threading.Thread(target=self.heartbeat_manager.send_heartbeat, daemon=True)
        thread.start()
        log("🫀 Heartbeat thread started.")

    def store_block(self, block_id, data):
        self.storage.save_block(block_id, data)
        log(f"📦 Block {block_id} stored successfully.")

    def read_block(self, block_id):
        return self.storage.read_block(block_id)

    def delete_block(self, block_id):
        self.storage.delete_block(block_id)
        log(f"🗑️ Block {block_id} deleted.")


@app.route('/store_block', methods=['POST'])
def store_block_api():
    block_id = request.form.get('block_id')
    file = request.files.get('data')

    if not block_id or not file:
        return jsonify({"error": "Missing 'block_id' or 'data'"}), 400

    data = file.read()
    data_node.store_block(block_id, data)
    return jsonify({"status": "success"}), 200


@app.route('/read_block', methods=['GET'])
def read_block_api():
    block_id = request.args.get("block_id")
    if not block_id:
        return jsonify({"error": "Missing 'block_id'"}), 400

    data = data_node.read_block(block_id)
    if data:
        return data, 200
    else:
        return jsonify({"error": "Block not found"}), 404


@app.route('/delete_block', methods=['DELETE'])
def delete_block_api():
    block_id = request.args.get("block_id")
    if not block_id:
        return jsonify({"error": "Missing 'block_id'"}), 400

    data_node.delete_block(block_id)
    return jsonify({"status": f"Block {block_id} deleted."}), 200


def run_flask(ip, port):
    log(f"🚀 Starting DataNode API at http://{ip}:{port}")
    app.run(host=ip, port=port)


def main():
    global data_node

    parser = argparse.ArgumentParser()
    parser.add_argument('--id', required=True, help="DataNode ID (e.g., 127.0.0.1:5001)")
    parser.add_argument('--port', type=int, default=5001, help="Port to run DataNode on")  # ✅ Include this!
    parser.add_argument('--storage', required=True, help="Path to storage directory")
    args = parser.parse_args()

    node_id = args.id
    port = args.port
    storage_path = args.storage
    namenode_url = "http://127.0.0.1:8000"

    data_node = DataNode(node_id, namenode_url, storage_path, ip="127.0.0.1", port=port)
    data_node.start_heartbeat()
    run_flask("0.0.0.0", port)