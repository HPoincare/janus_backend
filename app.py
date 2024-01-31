from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from flask_cors import CORS
import soundfile as sf
import librosa
import os

app = Flask(__name__)
CORS(app)
client = MongoClient('mongodb+srv://janus_dev:no_longer_temp_name@janus.8bvovej.mongodb.net/?retryWrites=true&w=majority')
db = client.mydatabase


@app.route('/')
def home():
    # Return the HTML form for file upload
    # return 'Hello World'
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio' in request.files:
        audio_file = request.files['audio']
        filename = secure_filename(audio_file.filename)
        file_path = os.path.join('/tmp', filename)
        audio_file.save(file_path)

        # Load audio file with librosa
        y, sr = librosa.load(file_path, sr=None)

        # Get BPM (tempo)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        # Get other audio features if desired
        # Example: Extracting Spectral Centroid
        # spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)

        # Insert analysis results into MongoDB
        result_id = db.analysis_results.insert_one({
            'filename': filename,
            'bpm': tempo,
            # 'spectral_centroid': spectral_centroid.tolist(), # If you want to store other features
        }).inserted_id

        # Clean up the temporary file
        os.remove(file_path)

        return jsonify({'message': 'File uploaded and analyzed', 'id': str(result_id)})

    return jsonify({'message': 'No audio file uploaded'})

if __name__ == '__main__':
    app.run(debug=False)



#   <h1>Altneratively, upload your own mp3 file for analysis</h1>
#               <form action="/upload" method="POST" enctype="multipart/form-data">
#                   <input type="file" name="audio">
#                   <input type="submit" value="Upload">
#               </form>
