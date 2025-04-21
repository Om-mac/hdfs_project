import time
import requests
import sys
from core.logger import log


class HeartbeatManager:
    def __init__(self, node_id, namenode_url, interval=5):
        """
        Initialize the HeartbeatManager with node details and interval.
        :param node_id: Unique identifier for the DataNode
        :param namenode_url: URL of the NameNode to send heartbeats to
        :param interval: Time interval (in seconds) between heartbeats
        """
        self.node_id = node_id
        self.namenode_url = namenode_url
        self.interval = interval  # seconds

    def send_heartbeat(self):
        """
        Continuously sends heartbeats to the NameNode at the specified interval.
        """
        while True:
            try:
                # Send a heartbeat message to the NameNode
                response = requests.post(
                    f"{self.namenode_url}/heartbeat",
                    json={"node_id": self.node_id}
                )
                if response.status_code == 200:
                    log(f"💓 Heartbeat sent from DataNode {self.node_id}")
                else:
                    log(f"⚠️ Heartbeat failed with status: {response.status_code}", level="warning")
            except requests.exceptions.RequestException as e:
                # Handle network-related errors
                log(f"❌ Network error while sending heartbeat: {e}", level="error")
            except Exception as e:
                # Handle other types of errors
                log(f"❌ Error sending heartbeat: {e}", level="error")

            # Sleep for the specified interval before sending the next heartbeat
            time.sleep(self.interval)


def main():
    if len(sys.argv) != 2:
        print("Usage: python heartbeat.py <node_id>")
        sys.exit(1)

    node_id = sys.argv[1]
    namenode_url = "http://localhost:5000"  # Ensure this matches your running Flask app!

    hb = HeartbeatManager(node_id, namenode_url)
    hb.send_heartbeat()


if __name__ == "__main__":
    main()