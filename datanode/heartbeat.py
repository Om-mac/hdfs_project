# datanode/heartbeat.py

import time
import requests
import sys
from core.logger import log


class HeartbeatManager:
    def __init__(self, node_id, namenode_url, interval=5):
        self.node_id = node_id
        self.namenode_url = namenode_url
        self.interval = interval  # seconds

    def send_heartbeat(self):
        while True:
            try:
                response = requests.post(
                    f"{self.namenode_url}/heartbeat",
                    json={"node_id": self.node_id}
                )
                if response.status_code == 200:
                    log(f"💓 Heartbeat sent from DataNode {self.node_id}")
                else:
                    log(f"⚠️ Heartbeat failed with status: {response.status_code}", level="warning")
            except Exception as e:
                log(f"❌ Error sending heartbeat: {e}", level="error")
            time.sleep(self.interval)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python heartbeat.py <node_id>")
        sys.exit(1)

    node_id = sys.argv[1]
    namenode_url = "http://localhost:5000"  # ✅ Make sure this matches your running Flask app!

    hb = HeartbeatManager(node_id, namenode_url)
    hb.send_heartbeat()