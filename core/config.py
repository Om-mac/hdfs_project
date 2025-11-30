# core/config.py

class Config:
    # Block size for file chunks (in bytes)
    BLOCK_SIZE =  1024 * 1024  # 1 MB
    
    # Timeout for requests (useful in case network hiccups)
    REQUEST_TIMEOUT = 3  

    # Enable debug logging
    DEBUG = True 

    # Default ports
    NAMENODE_PORT = 8000
    DATANODE_PORT = 5000

    # Heartbeat interval in seconds
    HEARTBEAT_INTERVAL = 5

    # Heartbeat timeout - mark node inactive if no heartbeat in this time
    HEARTBEAT_TIMEOUT = 30

    # Replication factor (number of copies of each block)
    REPLICATION_FACTOR = 2

    # NameNode base URL
    NAMENODE_URL = f"http://127.0.0.1:{NAMENODE_PORT}"

    # Storage paths
    DATA_DIR = "data"
    METADATA_DIR = "metadata"
    METADATA_FILE = f"{METADATA_DIR}/files_metadata.json"