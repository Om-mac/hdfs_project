from flask import Flask, request, jsonify
from namenode.namenode import NameNode
from core.logger import log
from core.config import Config
import time

app = Flask(__name__)
namenode = NameNode()

@app.route("/heartbeat_status", methods=["GET"])
def heartbeat_status():
    now = time.time()
    status_dict = {}

    for node_id, info in namenode.datanodes.items():
        last_heartbeat = info.get("last_heartbeat", 0)
        status = "active" if now - last_heartbeat < Config.HEARTBEAT_TIMEOUT else "inactive"

        status_dict[node_id] = {
            "status": status,
            "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_heartbeat)) if last_heartbeat else "N/A"
        }

    return jsonify(status_dict)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    node_id = data.get("node_id")
    ip = data.get("ip")
    port = data.get("port")

    if node_id and ip and port:
        log(f"📥 Registering DataNode: {node_id} at {ip}:{port}")
        namenode.datanodes[node_id] = {
            "ip": ip,
            "port": port,
            "status": "active",
            "last_heartbeat": time.time()
        }
        return jsonify({"status": "registered"}), 200
    return jsonify({"error": "Missing required fields"}), 400


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.get_json()
    node_id = data.get("node_id")

    if node_id:
        if node_id in namenode.datanodes:
            namenode.datanodes[node_id]["status"] = "active"
            namenode.datanodes[node_id]["last_heartbeat"] = time.time()
            log(f"💓 Heartbeat received from DataNode {node_id}")
            return jsonify({"status": "alive"}), 200
        else:
            log(f"⚠️ Unknown DataNode {node_id} tried to send heartbeat", level="warning")
            return jsonify({"error": "Unknown DataNode"}), 404
    return jsonify({"error": "Missing node_id"}), 400


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
        log(f"❌ Error assigning blocks: {e}", level="error")
        return jsonify({"error": str(e)}), 500


@app.route("/get_file_blocks", methods=["GET"])
def get_file_blocks():
    file_name = request.args.get("file_name")
    if not file_name:
        return jsonify({"error": "Missing file_name"}), 400

    blocks = namenode.get_file_blocks(file_name)
    if not blocks:
        return jsonify({"error": "File not found"}), 404

    return jsonify({"blocks": blocks}), 200


@app.route("/files", methods=["GET"])
def list_files():
    try:
        files = namenode.list_files()
        if not files:
            log("📁 No files stored in HDFS.")
        else:
            log(f"📂 Files in HDFS: {files}")

        return jsonify(files), 200
    except Exception as e:
        log(f"❌ Error listing files: {e}", level="error")
        return jsonify({"error": str(e)}), 500


@app.route("/delete_file", methods=["POST"])
def delete_file():
    data = request.get_json()
    file_name = data.get("file_name")
    if not file_name:
        return jsonify({"error": "Missing file_name"}), 400

    try:
        namenode.remove_file(file_name)
        return jsonify({"message": f"File '{file_name}' deleted"}), 200
    except Exception as e:
        log(f"❌ Error deleting file: {e}", level="error")
        return jsonify({"error": str(e)}), 500


@app.route("/metadata", methods=["GET"])
def get_metadata():
    try:
        return jsonify(namenode.metadata.metadata), 200
    except Exception as e:
        log(f"❌ Error fetching metadata: {e}", level="error")
        return jsonify({"error": str(e)}), 500


@app.route("/datanodes", methods=["GET"])
def get_datanodes():
    try:
        return jsonify(namenode.datanodes), 200
    except Exception as e:
        log(f"❌ Error fetching datanodes: {e}", level="error")
        return jsonify({"error": str(e)}), 500


@app.route("/file_blocks", methods=["GET"])
def get_file_blocks_api():
    file_name = request.args.get("file_name")
    if not file_name:
        log("Missing file_name", level="error")
        return jsonify({"error": "Missing file_name"}), 400
    try:
        blocks = namenode.get_file_blocks(file_name)
        return jsonify(blocks), 200
    except Exception as e:
        log(f"❌ Error fetching file blocks: {e}", level="error")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    log("✅ NameNode is live and running.")
    app.run(host="0.0.0.0", port=Config.NAMENODE_PORT)