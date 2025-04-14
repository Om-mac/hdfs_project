import argparse
import threading
from flask import Flask, request, jsonify
from datanode.datanode import DataNode
from core.logger import log

app = Flask(__name__)
data_node = None  # Global instance


@app.route('/store_block', methods=['POST'])
def store_block():
    block_id = request.form.get('block_id')
    file = request.files.get('data')

    if not block_id or not file:
        return jsonify({"error": "Missing 'block_id' or 'data'"}), 400

    data = file.read()
    data_node.store_block(block_id, data)
    return jsonify({"status": "success"}), 200


@app.route('/read_block', methods=['GET'])
def read_block():
    block_id = request.args.get("block_id")
    if not block_id:
        return jsonify({"error": "Missing 'block_id'"}), 400

    data = data_node.read_block(block_id)
    if data:
        return data, 200
    else:
        return jsonify({"error": "Block not found"}), 404


@app.route('/delete_block', methods=['DELETE'])
def delete_block():
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
    parser.add_argument('--port', type=int, default=5001, help="Port to run DataNode on")
    parser.add_argument('--storage', required=True, help="Path to storage directory")
    args = parser.parse_args()

    node_id = args.id
    port = args.port
    storage_path = args.storage
    namenode_url = "http://127.0.0.1:8000"  # Make sure this matches NameNode's actual URL

    data_node = DataNode(node_id, namenode_url, storage_path, ip="127.0.0.1", port=port)

    # Start heartbeat in a background thread
    heartbeat_thread = threading.Thread(target=data_node.start_heartbeat)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()

    # Run the API
    run_flask("0.0.0.0", port)


if __name__ == "__main__":
    main()