# core/config.py

class Config:
    # Block size for file chunks (in bytes)
    BLOCK_SIZE = 64 * 1024  # 1 MB

    # Default ports
    NAMENODE_PORT = 8000
    DATANODE_PORT = 5000

    # Heartbeat interval in seconds
    HEARTBEAT_INTERVAL = 5

    # Replication factor (number of copies of each block)
    REPLICATION_FACTOR = 2

    # NameNode base URL
    NAMENODE_URL = f"http://localhost:{NAMENODE_PORT}"

    # Storage paths
    DATA_DIR = "data"
    METADATA_DIR = "metadata"
    METADATA_FILE = f"{METADATA_DIR}/files_metadata.json"