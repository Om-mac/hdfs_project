import os
from core.logger import log


class FileSplitter:
    def __init__(self, block_size):
        self.block_size = block_size

    def split_file(self, file_path):
        """Splits the file into chunks of block_size and returns a list of bytes."""
        blocks = []
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.block_size)
                    if not chunk:
                        break
                    blocks.append(chunk)
            log(f"Split '{file_path}' into {len(blocks)} blocks.")
        except Exception as e:
            log(f"Error splitting file: {e}", level="error")
        return blocks

    def merge_blocks(self, blocks, output_path):
        """Merges list of bytes into a single file at output_path."""
        try:
            with open(output_path, 'wb') as f:
                for block in blocks:
                    f.write(block)
            log(f"Merged {len(blocks)} blocks into '{output_path}'")
        except Exception as e:
            log(f"Error merging blocks: {e}", level="error")