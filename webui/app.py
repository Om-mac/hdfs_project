from flask import Flask, render_template, request, jsonify
from core.config import Config  # Import the Config class
import os

app = Flask(__name__)

# Access the configuration values from Config class
BLOCK_SIZE = Config.BLOCK_SIZE
PORT = Config.NAMENODE_PORT  # or choose any other relevant port

# Route for the main dashboard
@app.route('/')
def dashboard():
    # Placeholder for the metadata (you can replace it with actual data from the NameNode)
    data = {
        'total_blocks': 0,
        'total_files': 0,
        'datanodes': 2,
        'storage_used': 0,
    }
    return render_template('dashboard.html', data=data)

# API to retrieve metadata about files and blocks
@app.route('/metadata')
def metadata():
    # Here, you can retrieve actual metadata from your NameNode class or a stored file
    metadata = {}
    try:
        with open('../metadata/files_metadata.json', 'r') as file:
            metadata = file.read()
    except FileNotFoundError:
        metadata = {"error": "Metadata file not found!"}
    return jsonify(metadata)

# API to upload files (just a placeholder example)
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        # Handle file storage or further processing here
        file.save(os.path.join('uploads', file.filename))
        return f'File {file.filename} uploaded successfully!', 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4098)