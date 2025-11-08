import os
from core.logger import log


class BlockStorage:
    def __init__(self, storage_path):
        self.storage_path = storage_path

        os.makedirs(self.storage_path, exist_ok=True)
        log(f"✅ Block storage initialized at {self.storage_path}")

    def _get_block_path(self, block_id):
        """
        Helper method to construct the file path for the given block ID.
        """
        return os.path.join(self.storage_path, f"{block_id}.block")

    def save_block(self, block_id, data):
        """
        Save a block to disk.
        """
        try:
            block_path = self._get_block_path(block_id)
            with open(block_path, 'wb') as f:
                f.write(data)
            log(f"✅ Block {block_id} saved to disk at {block_path}.")
        except Exception as e:
            log(f"❌ Error saving block {block_id}: {e}", level="error")

    def read_block(self, block_id):
        """
        Read a block from disk.
        """
        try:
            block_path = self._get_block_path(block_id)
            if not os.path.exists(block_path):
                log(f"⚠️ Block {block_id} not found at {block_path}.", level="warning")
                return None
            with open(block_path, 'rb') as f:
                data = f.read()
            log(f"✅ Block {block_id} read from disk.")
            return data
        except Exception as e:
            log(f"❌ Error reading block {block_id}: {e}", level="error")
            return None

    def delete_block(self, block_id):
        """
        Delete a block from disk.
        """
        try:
            block_path = self._get_block_path(block_id)
            if os.path.exists(block_path):
                os.remove(block_path)
                log(f"✅ Block {block_id} deleted from {block_path}.")
            else:
                log(f"⚠️ Block {block_id} does not exist at {block_path}.", level="warning")
        except Exception as e:
            log(f"❌ Error deleting block {block_id}: {e}", level="error")