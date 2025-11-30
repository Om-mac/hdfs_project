import os
import sys
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
import requests

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from client.client import HDFSClient
from core.config import Config
from core.logger import log

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flashing messages

# Use absolute paths for upload/download folders to avoid CWD/root_path mismatch issues
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'webui_uploads')
app.config['DOWNLOAD_FOLDER'] = os.path.join(BASE_DIR, 'webui_downloads')

# Ensure temp directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

# Initialize HDFS Client
hdfs_client = HDFSClient(Config.NAMENODE_URL, Config.BLOCK_SIZE)

@app.route('/')
def index():
    files = []
    try:
        # Fetch file list directly from NameNode API
        response = requests.get(f"{Config.NAMENODE_URL}/files")
        if response.status_code == 200:
            file_list = response.json()
            # Transform list of strings to objects if necessary, or just pass them
            # The NameNode returns a list of filenames or objects? 
            # Let's check namenode.py: return jsonify(files) -> files = namenode.list_files()
            # namenode.list_files() returns list of filenames (strings) or dicts?
            # Let's assume it returns a list of filenames for now, but better to check.
            # Actually, let's fetch metadata to get size and block count.
            
            meta_response = requests.get(f"{Config.NAMENODE_URL}/metadata")
            if meta_response.status_code == 200:
                metadata = meta_response.json()
                # Convert metadata dict to list for template
                for fname, blocks in metadata.items():
                    # Metadata structure is {filename: [block_list]}
                    # We don't have file size in metadata, so we'll just show block count
                    files.append({
                        "name": fname,
                        "size": f"{len(blocks) * Config.BLOCK_SIZE} (approx)",
                        "blocks": blocks
                    })
            else:
                flash("Could not fetch metadata from NameNode", "warning")
        else:
            flash("Could not connect to NameNode", "danger")
    except Exception as e:
        flash(f"Error connecting to HDFS: {e}", "danger")

    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('index'))

    if file:
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)

        try:
            # Use HDFS Client to upload
            hdfs_client.upload_file(temp_path)
            flash(f"Successfully uploaded '{filename}'", "success")
        except Exception as e:
            flash(f"Upload failed: {e}", "danger")
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    temp_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    
    try:
        # Use HDFS Client to download to temp folder
        # We need to modify client or just use it. 
        # client.download_file(filename, output_path)
        
        # Check if file exists in HDFS first (optional, client handles it)
        
        hdfs_client.download_file(filename, temp_path)
        
        if os.path.exists(temp_path):
            return send_file(temp_path, as_attachment=True)
        else:
            flash("Download failed: File not created", "danger")
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f"Download error: {e}", "danger")
        return redirect(url_for('index'))
    # Note: Temp download files are not automatically cleaned up here immediately after send_file
    # In a production app, use a background task or stream the response. 
    # For this demo, we'll leave it or try to cleanup.

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    try:
        hdfs_client.delete_file(filename)
        flash(f"Deleted '{filename}'", "success")
    except Exception as e:
        flash(f"Delete failed: {e}", "danger")
    
    return redirect(url_for('index'))

@app.route('/status')
def status():
    try:
        response = requests.get(f"{Config.NAMENODE_URL}/heartbeat_status")
        return jsonify(response.json())
    except:
        return jsonify({})

if __name__ == '__main__':
    app.run(debug=True, port=5005)
