from flask import Flask, request, jsonify
from PineconeAPIHandler import VectorDBProcessor
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app, resources={r"/*": {"origins": "*"}})

# Folder to store uploaded files temporarily
TEMP_FOLDER = 'TempFile'
os.makedirs(TEMP_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = TEMP_FOLDER



@app.route('/api/upload', methods=['POST'])
def upload_file():
    room_code = request.form.get('roomCode')
    file = request.files.get('file')
    if not file:
        return jsonify({"success": False, "message": "No file provided"}), 400
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"message": "Only PDFs are accepted for now"}), 400
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    pinecone_instance = VectorDBProcessor(("b0090664-f099-4b28-8b44-02f1927d5b53","AIzaSyBVCCh_IsrbOpwD9sDd_frc8t1YYt4haXE"))

    try:
        if pinecone_instance.extract_and_embed_pages(file_path):
            os.remove(file_path)
            return jsonify({"success": True, "message": "File embedded successfully"}), 200
        else:
            os.remove(file_path)
            return jsonify({"message": "Failed to embed file"}), 404
    except Exception as e:
        os.remove(file_path)
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
