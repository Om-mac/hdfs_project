import uuid

class ReplicationManager:
    def __init__(self, metadata_store):
        self.metadata_store = metadata_store

    def assign_blocks(self, file_name, num_blocks, replication_factor, datanodes):
        block_list = []

        for _ in range(int(num_blocks)):
            block_id = str(uuid.uuid4())

            # Pick first 'replication_factor' datanodes
            chosen = list(datanodes.items())[:replication_factor]
            replicas = [f"http://{info['host']}:{info['port']}" for node_id, info in chosen]

            block_list.append({
                "block_id": block_id,
                "datanodes": replicas
            })

        self.metadata_store.add_file_blocks(file_name, block_list)
        return block_list