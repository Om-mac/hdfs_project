

"""
NameNode Package
----------------
This package handles metadata operations such as:
- File to block mapping
- Block replication info
- Coordination with DataNodes
"""

from .namenode import NameNode
from .metadata_store import MetadataStore
from .replication_manager import ReplicationManager