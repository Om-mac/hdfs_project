from client.client import HDFSClient
from core.logger import log
from core.config import Config
import sys

def main():
    if len(sys.argv) < 2:
        log("Usage: python run_client.py <upload/download/list/delete> <file_path (if required)>", level="error")
        return

    action = sys.argv[1].lower()
    file_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Load config values
    namenode_url = Config.NAMENODE_URL
    block_size = Config.BLOCK_SIZE

    client = HDFSClient(namenode_url, block_size)
    if action == "upload":
        if file_path:
            client.upload_file(file_path)
        else:
            log("❌ Please provide file path for upload", level="error")
    elif action == "download":
        if file_path:
            output_path = input("Enter output path to save the file: ")
            client.download_file(file_path, output_path)
        else:
            log("❌ Please provide file name for download", level="error")
    elif action == "list":
        client.list_files()
    elif action == "delete":
        if file_path:
            client.delete_file(file_path)
        else:
            log("❌ Please provide file name to delete", level="error")
    else:
        log("❌ Unknown action. Use 'upload', 'download', 'list', or 'delete'.", level="error")

if __name__ == "__main__":
    main()