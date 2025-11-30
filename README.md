# Simple HDFS Implementation in Python

A lightweight, educational implementation of the Hadoop Distributed File System (HDFS) built from scratch in Python. This project demonstrates core distributed storage concepts including metadata management, block-based storage, data replication, and fault tolerance mechanisms.

## 🌟 Features

- **Distributed Block Storage**: Files are automatically split into blocks and distributed across multiple DataNodes
- **Automatic Replication**: Configurable replication factor ensures data durability and availability
- **Fault Detection**: Heartbeat mechanism continuously monitors DataNode health
- **Web Dashboard**: A modern, user-friendly web interface to manage files and monitor cluster health
- **RESTful API**: Clean HTTP-based communication between all components
- **Metadata Management**: Centralized file-to-block mapping with persistent storage
- **Simple CLI**: Easy-to-use command-line interface for file operations
- **Real-time Monitoring**: API endpoints to check cluster status and DataNode health

## 🎯 What is HDFS?

The Hadoop Distributed File System (HDFS) is a distributed file system designed to run on commodity hardware. This implementation captures the essence of HDFS:

- **Master-Slave Architecture**: One NameNode (master) coordinates multiple DataNodes (slaves)
- **Block-Based Storage**: Large files are split into fixed-size blocks for parallel processing
- **Data Replication**: Each block is replicated across multiple nodes to prevent data loss
- **Horizontal Scalability**: Add more DataNodes to increase storage capacity

## 🏗️ Architecture

```
                    ┌─────────────────┐       ┌─────────────────┐
                    │     Client      │       │   Web Dashboard │
                    │  (CLI / API)    │       │   (Port 5005)   │
                    └────────┬────────┘       └────────┬────────┘
                             │                         │
                             └───────────┬─────────────┘
                                         │
                                ┌────────▼────────┐
                                │    NameNode     │
                    │   (Metadata)    │
                    │   Port: 8000    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐        ┌────▼─────┐        ┌────▼─────┐
   │DataNode 1│        │DataNode 2│        │DataNode 3│
   │Port: 5001│        │Port: 5002│        │Port: 5003│
   │(Blocks)  │        │(Blocks)  │        │(Blocks)  │
   └──────────┘        └──────────┘        └──────────┘
```

**Key Components:**

- **NameNode**: Manages file system namespace and controls access to files. Maintains metadata mapping files to blocks and blocks to DataNodes.
- **DataNode**: Stores actual file blocks and serves read/write requests from clients. Sends periodic heartbeats to NameNode.
- **Client**: Provides interface for interacting with the file system (upload, download, list, delete).

## 📁 Project Structure

```
/my_hdfs_project/
├── namenode/              # NameNode logic (metadata management)
│   ├── namenode.py        # Main NameNode class
│   ├── metadata_store.py  # File/block mapping logic
│   └── replication_manager.py # Replication handling
│
├── datanode/              # DataNode logic (block storage)
│   ├── datanode.py        # Main DataNode class
│   ├── storage.py         # Store/retrieve blocks
│   └── heartbeat.py       # Heartbeat logic
│
├── client/                # Client-side interface
│   ├── client.py          # File upload/download interface
│   └── file_splitter.py   # Split and merge file logic
│
├── core/                  # Core utilities
│   ├── config.py          # Configuration settings
│   ├── logger.py          # Custom logging utility
│   └── utils.py           # Miscellaneous utilities
│
├── webui/                 # Web Interface
│   ├── app.py             # Flask application backend
│   └── templates/
│       └── index.html     # Dashboard HTML template
│
├── data/                  # Block storage directories
│   ├── datanode1/
│   ├── datanode2/
│   └── datanode3/
│
├── metadata/              # Metadata storage
│   └── files_metadata.json
│
├── run_namenode.py        # Launch NameNode
├── run_datanode.py        # Launch DataNode
├── run_client.py          # Client interaction script
├── run_webui.py           # Launch Web Dashboard
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Required libraries:
  ```bash
  pip install Flask==3.0.0 requests==2.31.0
  ```

### Running the System

You will need to run each component in a separate terminal window.

**1. Start the NameNode (Master)**
```bash
python3 run_namenode.py
```

**2. Start DataNodes (Slaves)**
Run as many DataNodes as you like by changing the ID and Port.

```bash
# Terminal 2
python3 run_datanode.py --id datanode1 --port 5001 --storage data/datanode1

# Terminal 3
python3 run_datanode.py --id datanode2 --port 5002 --storage data/datanode2

# Terminal 4 (Optional)
python3 run_datanode.py --id datanode3 --port 5003 --storage data/datanode3
```

**3. Start the Web Dashboard**
```bash
# Terminal 5
python3 run_webui.py
```

### 🖥️ Accessing the System

**Web Dashboard:**
Open your browser and go to: **[http://127.0.0.1:5005](http://127.0.0.1:5005)**

**Command Line Interface (CLI):**
You can also use the CLI script to interact with the system:

```bash
# Upload a file
python3 run_client.py upload <file_path>

# List files
python3 run_client.py list

# Download a file
python3 run_client.py download <file_name>

# Delete a file
python3 run_client.py delete <file_name>
```

## ⚙️ Configuration

Edit `core/config.py` to customize system behavior:

```python
class Config:
    # Block size for file chunks (1 MB)
    BLOCK_SIZE = 1024 * 1024
    
    # Number of replicas for each block
    REPLICATION_FACTOR = 2
    
    # NameNode configuration
    NAMENODE_PORT = 8000
    NAMENODE_URL = f"http://localhost:{NAMENODE_PORT}"
    
    # DataNode default port
    DATANODE_PORT = 5000
    
    # Heartbeat interval (seconds)
    HEARTBEAT_INTERVAL = 5
    
    # Request timeout (seconds)
    REQUEST_TIMEOUT = 3
    
    # Storage paths
    DATA_DIR = "data"
    METADATA_DIR = "metadata"
    METADATA_FILE = f"{METADATA_DIR}/files_metadata.json"
    
    # Enable debug logging
    DEBUG = True
```

## 📊 How It Works

### Upload Workflow

```
┌────────┐                 ┌──────────┐                ┌──────────┐
│ Client │                 │ NameNode │                │ DataNode │
└───┬────┘                 └────┬─────┘                └────┬─────┘
    │                           │                           │
    │  1. Assign Blocks         │                           │
    ├──────────────────────────>│                           │
    │  POST /assign_blocks      │                           │
    │  {file_name, num_blocks}  │                           │
    │                           │                           │
    │  2. Block Assignments     │                           │
    │<──────────────────────────┤                           │
    │  {block_id, datanodes[]}  │                           │
    │                           │                           │
    │  3. Store Block           │                           │
    ├───────────────────────────┼──────────────────────────>│
    │  POST /store_block        │                           │
    │  {block_id, data}         │                           │
    │                           │                           │
    │  4. Acknowledgment        │                           │
    │<──────────────────────────┼───────────────────────────┤
    │  {status: "success"}      │                           │
    │                           │                           │
    │  (Repeat for replicas)    │                           │
    │                           │                           │
    │                     5. Save Metadata                  │
    │                           │                           │
```

### Download Workflow

```
┌────────┐                 ┌──────────┐                ┌──────────┐
│ Client │                 │ NameNode │                │ DataNode │
└───┬────┘                 └────┬─────┘                └────┬─────┘
    │                           │                           │
    │  1. Get File Blocks       │                           │
    ├──────────────────────────>│                           │
    │  GET /get_file_blocks     │                           │
    │  ?file_name=sample.pdf    │                           │
    │                           │                           │
    │  2. Block Locations       │                           │
    │<──────────────────────────┤                           │
    │  [{block_id, datanodes}]  │                           │
    │                           │                           │
    │  3. Read Block            │                           │
    ├───────────────────────────┼──────────────────────────>│
    │  GET /read_block          │                           │
    │  ?block_id=abc-123        │                           │
    │                           │                           │
    │  4. Block Data            │                           │
    │<──────────────────────────┼───────────────────────────┤
    │  (binary data)            │                           │
    │                           │                           │
    │  (Repeat for all blocks)  │                           │
    │                           │                           │
    │  5. Merge Blocks Locally  │                           │
    │                           │                           │
```

### Heartbeat Mechanism

```
┌──────────┐                 ┌──────────┐
│ DataNode │                 │ NameNode │
└────┬─────┘                 └────┬─────┘
     │                            │
     │  Every 5 seconds           │
     ├───────────────────────────>│
     │  POST /heartbeat           │
     │  {node_id}                 │
     │                            │
     │  Acknowledgment            │
     │<───────────────────────────┤
     │  {status: "alive"}         │
     │                            │
     │  (Continuous loop)         │
     │                            │
     
     If no heartbeat for 30s → DataNode marked INACTIVE
```

## 🔑 Key Features Explained

### 1. Block-Based Storage

Files are split into fixed-size blocks (1MB by default). This enables:
- **Parallel Processing**: Multiple blocks can be read/written simultaneously
- **Efficient Storage**: Partial reads don't require loading entire files
- **Scalability**: Large files can be distributed across many nodes

**Example:**
```
sample.pdf (2.5 MB)
    ↓
Block 1: 1.0 MB → DataNode1, DataNode2
Block 2: 1.0 MB → DataNode1, DataNode2  
Block 3: 0.5 MB → DataNode1, DataNode2
```

### 2. Replication for Fault Tolerance

Each block is stored on multiple DataNodes (default: 2 replicas):
- **Data Durability**: Files survive DataNode failures
- **Read Performance**: Can read from any replica
- **Automatic Failover**: If one replica is unavailable, use another

### 3. Metadata Management

NameNode maintains a mapping of files to blocks and blocks to DataNodes:

**Metadata Structure** (`metadata/files_metadata.json`):
```json
{
  "sample.pdf": [
    {
      "block_id": "a3f2e9d1-4b5c-6789-0abc-def123456789",
      "datanodes": [
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5002"
      ]
    },
    {
      "block_id": "b8d4c2a7-9e1f-3456-7890-abcdef012345",
      "datanodes": [
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5002"
      ]
    }
  ]
}
```

### 4. Heartbeat & Fault Detection

- DataNodes send heartbeat every **5 seconds**
- NameNode marks DataNode as **inactive** after **30 seconds** of silence
- Inactive DataNodes are excluded from new block assignments
- System can detect and adapt to node failures

## 🛠️ Advanced Usage

### Monitor Cluster Health

Check which DataNodes are active:

```bash
curl http://localhost:8000/heartbeat_status
```

**Response:**
```json
{
  "datanode1": {
    "status": "active",
    "last_heartbeat": "2025-11-08 10:40:15"
  },
  "datanode2": {
    "status": "active",
    "last_heartbeat": "2025-11-08 10:40:16"
  }
}
```

### View All DataNodes

```bash
curl http://localhost:8000/datanodes
```

### Inspect Metadata

```bash
curl http://localhost:8000/metadata
```

### Check File Block Distribution

```bash
curl "http://localhost:8000/get_file_blocks?file_name=sample.pdf"
```

## 🐛 Troubleshooting

### DataNode Won't Register

**Symptoms:** DataNode starts but can't connect to NameNode

**Solutions:**
- Ensure NameNode is running first
- Verify NameNode is accessible at `http://127.0.0.1:8000`
- Check firewall rules allow port 8000
- Look for errors in DataNode logs

### Upload Fails

**Symptoms:** Upload command returns error or hangs

**Solutions:**
- Verify at least one DataNode is active: `curl http://localhost:8000/datanodes`
- Check disk space in DataNode storage directories
- Ensure `data/` directories exist or can be created
- Review NameNode logs for block assignment errors

### Download Corrupted or Incomplete

**Symptoms:** Downloaded file differs from original

**Solutions:**
- Verify block integrity using checksums (shasum/md5sum)
- Check DataNode availability: `curl http://localhost:8000/heartbeat_status`
- Ensure all blocks exist on at least one DataNode
- Try downloading again (may fetch from different replicas)

### "Block not found" Errors

**Symptoms:** Download fails with 404 errors

**Causes:**
- Metadata exists but blocks were deleted from DataNode storage
- DataNode was restarted and storage path changed
- Block file was manually removed from disk

**Solutions:**
- Verify block files exist in DataNode storage directory
- Check DataNode logs for storage errors
- Re-upload the file if blocks are lost

### Heartbeat Issues

**Symptoms:** DataNodes marked inactive despite running

**Solutions:**
- Check network connectivity between DataNode and NameNode
- Verify heartbeat thread is running (look for 💓 in logs)
- Ensure `HEARTBEAT_INTERVAL` (5s) < `HEARTBEAT_TIMEOUT` (30s)
- Check system clock synchronization

### Port Already in Use

**Symptoms:** "Address already in use" error

**Solutions:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
python3 run_namenode.py  # Edit config.py first
```

## 📚 Implementation Details

### Block Storage

Blocks are stored as individual files with `.block` extension:

```
data/datanode1/
├── a3f2e9d1-4b5c-6789-0abc-def123456789.block
├── b8d4c2a7-9e1f-3456-7890-abcdef012345.block
└── c9a7f3e2-1d4b-5678-9abc-def012345678.block
```

### API Endpoints

**NameNode (Port 8000):**
- `POST /register` - DataNode registration
- `POST /heartbeat` - Receive heartbeat
- `POST /assign_blocks` - Assign blocks for upload
- `GET /get_file_blocks` - Get block locations for download
- `GET /files` - List all files
- `POST /delete_file` - Delete file metadata
- `GET /heartbeat_status` - DataNode health status
- `GET /datanodes` - List all DataNodes
- `GET /metadata` - View all metadata

**DataNode (Ports 5001, 5002, ...):**
- `POST /store_block` - Store a block
- `GET /read_block` - Retrieve a block
- `DELETE /delete_block` - Delete a block

## 🎓 Learning Objectives

This project is perfect for understanding:

✅ **Distributed Systems Design**
- Master-slave architecture patterns
- Consensus and coordination between nodes
- Handling partial failures

✅ **Storage Systems**
- Block-based vs file-based storage
- Replication strategies
- Metadata vs data separation

✅ **Network Programming**
- RESTful API design with Flask
- HTTP client programming with requests
- Multi-threaded network services

✅ **Fault Tolerance**
- Heartbeat mechanisms
- Failure detection
- Data redundancy strategies

✅ **Python Engineering**
- Clean code architecture
- JSON serialization
- Binary file I/O
- Threading and concurrency

## 💡 Possible Enhancements

Want to take this project further? Here are some ideas:

**Core Functionality:**
- [ ] Implement actual block deletion from DataNodes (garbage collection)
- [ ] Add round-robin or random block placement for load balancing
- [ ] Support variable replication factor per file
- [ ] Implement block re-replication when DataNodes fail

**Reliability & Performance:**
- [ ] Add NameNode High Availability (HA) with secondary NameNode
- [ ] Implement checksums for data integrity verification
- [ ] Add data compression before storing blocks
- [ ] Support for larger-than-memory files with streaming

**Security:**
- [ ] Add authentication (user login)
- [ ] Implement authorization (file permissions)
- [ ] Enable encryption for data at rest
- [ ] Add TLS/SSL for data in transit

**User Experience:**
- [ ] Build the Web UI dashboard (Flask + HTML/CSS/JS)
- [ ] Add progress bars for uploads/downloads
- [ ] Implement file versioning
- [ ] Support for directories/folders

**Testing & Monitoring:**
- [ ] Add comprehensive unit tests
- [ ] Create integration test suite
- [ ] Add performance metrics and logging
- [ ] Implement DataNode capacity monitoring

## 🔒 Security Considerations

> **⚠️ Important:** This is an educational implementation. For production use, you MUST add:
> - User authentication and authorization
> - Encrypted data transmission (HTTPS/TLS)
> - Access control lists (ACLs) for files
> - Secure RPC communication between nodes
> - Input validation and sanitization
> - Rate limiting and DoS protection

## 🚧 Known Limitations

This implementation is simplified for educational purposes:

- **No Authentication**: Anyone can access the system
- **Single NameNode**: No high availability (NameNode is single point of failure)
- **Simple Block Placement**: Always uses first N DataNodes (no load balancing)
- **No Garbage Collection**: Deleted file blocks remain on DataNodes
- **No Data Integrity Checks**: Missing checksums for corruption detection
- **No Rack Awareness**: Doesn't consider network topology for replica placement
- **Limited Error Recovery**: Basic error handling without sophisticated retry logic
- **No Compression/Encryption**: Data stored as-is without optimization

## 📖 References & Further Reading

- [Apache Hadoop HDFS Architecture Guide](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
- [The Google File System (GFS) Paper](https://research.google/pubs/pub51/)
- [Designing Data-Intensive Applications](https://dataintensive.net/) by Martin Kleppmann
- [Distributed Systems: Principles and Paradigms](https://www.distributed-systems.net/) by Andrew S. Tanenbaum

## 🤝 Contributing

This is an educational project, but contributions are welcome! Feel free to:

- 🐛 Report bugs or issues
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests
- ⭐ Star the repository if you find it helpful!

## 📄 License

This project is for educational purposes. Feel free to use, modify, and distribute as needed.

---

**Built with ❤️ to demystify distributed file systems**

*Perfect for computer science students, system design interviews, and anyone curious about how HDFS works under the hood!*

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->
