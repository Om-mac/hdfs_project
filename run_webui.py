import sys
import os

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from webui.app import app

if __name__ == "__main__":
    print("🚀 Starting HDFS Web Dashboard at http://127.0.0.1:5005")
    app.run(host="0.0.0.0", port=5005, debug=True)
