import os
import requests
from core.logger import log
from client.file_splitter import FileSplitter

class HDFSClient:
    def __init__(self, namenode_url, block_size):
        self.namenode_url = namenode_url
        self.block_size = block_size
        self.splitter = FileSplitter(block_size)

    def upload_file(self, file_path):
        if not os.path.exists(file_path):
            log(f"❌ File '{file_path}' does not exist!", level="error")
            return

        file_name = os.path.basename(file_path)
        blocks = self.splitter.split_file(file_path)
        num_blocks = len(blocks)

        log(f"📤 Uploading '{file_name}' in {num_blocks} blocks.")

        try:
            log("📨 Requesting block assignment from NameNode...", level="info")
            response = requests.post(
                f"{self.namenode_url}/assign_blocks",
                json={"file_name": file_name, "num_blocks": num_blocks}
            )

            if response.status_code != 200:
                log(f"❌ Failed to assign blocks. Status Code: {response.status_code}, Response: {response.text}", level="error")
                return

            block_assignments = response.json().get("blocks", [])

            for block_data, assignment in zip(blocks, block_assignments):
                block_id = assignment.get("block_id")
                datanodes = assignment.get("datanodes", [])

                if not block_id or not datanodes:
                    log(f"❌ Invalid assignment: {assignment}", level="error")
                    continue

                for datanode_url in datanodes:
                    self._send_block_to_datanode(datanode_url, block_id, block_data)

        except Exception as e:
            log(f"❌ Upload failed: {e}", level="error")

    def _send_block_to_datanode(self, datanode_url, block_id, data):
        try:
            url = f"{datanode_url}/store_block"
            response = requests.post(
                url,
                files={"data": data},
                data={"block_id": block_id}
            )

            if response.status_code == 200:
                log(f"✅ Block {block_id} sent to DataNode at {datanode_url}")
            else:
                log(f"⚠️ Failed to send block {block_id} to {datanode_url}. Status: {response.status_code}", level="warning")
        except Exception as e:
            log(f"❌ Error sending block to DataNode {datanode_url}: {e}", level="error")

    def download_file(self, file_name, output_path):
        try:
            response = requests.get(f"{self.namenode_url}/get_file_blocks?file_name={file_name}")
            if response.status_code != 200:
                log("❌ Failed to get file block info.", level="error")
                return

            block_info = response.json().get("blocks", [])
            block_data = []

            for block in block_info:
                block_id = block.get("block_id")
                datanodes = block.get("datanodes", [])

                if not block_id or not datanodes:
                    log(f"⚠️ Incomplete block info: {block}", level="warning")
                    continue

                for node_url in datanodes:
                    data = self._get_block_from_datanode(node_url, block_id)
                    if data:
                        block_data.append(data)
                        break  # Stop after first successful replica

            self.splitter.merge_blocks(block_data, output_path)
            log(f"✅ Downloaded file saved to '{output_path}'")

        except Exception as e:
            log(f"❌ Download failed: {e}", level="error")

    def _get_block_from_datanode(self, datanode_url, block_id):
        try:
            url = f"{datanode_url}/read_block?block_id={block_id}"
            response = requests.get(url)
            if response.status_code == 200:
                log(f"📥 Fetched block {block_id} from {datanode_url}")
                return response.content
            else:
                log(f"⚠️ Failed to get block {block_id} from {datanode_url}", level="warning")
                return None
        except Exception as e:
            log(f"❌ Error fetching block from {datanode_url}: {e}", level="error")
            return None

    def delete_file(self, file_name):
        try:
            response = requests.post(f"{self.namenode_url}/delete_file", json={"file_name": file_name})
            if response.status_code == 200:
                log(response.json()["message"])
            else:
                log(f"❌ Error deleting file: {response.text}", level="error")
        except Exception as e:
            log(f"❌ Exception during file deletion: {e}", level="error")

    def list_files(self):
        try:
            response = requests.get(f"{self.namenode_url}/files")
            if response.status_code == 200:
                files = response.json()
                if not files:
                    log("📁 No files stored in HDFS yet.")
                else:
                    log("📂 Files stored in HDFS:")
                    for file_name in files:
                        print(" -", file_name)
            else:
                log("❌ Could not retrieve file list", level="error")
        except Exception as e:
            log(f"❌ Exception fetching file list: {e}", level="error")