import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import subprocess
import openai

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to extract audio from video
def extract_audio(input_path, output_path):
    subprocess.run([
        'ffmpeg', '-i', input_path, '-vn', '-acodec', 'mp3', output_path
    ], check=True)

# Route for UI
@app.route('/')
def index():
    return render_template('index.html')

# Route for transcribing
@app.route('/transcribe', methods=['POST'])
def transcribe():
    file = request.files['file']
    language = request.form.get('language', '').strip()
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Convert video to audio if necessary
    audio_path = filepath
    if not filepath.endswith('.mp3'):
        audio_path = filepath + '.mp3'
        extract_audio(filepath, audio_path)

    try:
        # Whisper transcription
        transcription = openai.Audio.transcribe(
            model="whisper-1",
            file=open(audio_path, 'rb'),
            language=language if language else None
        )

        raw_text = transcription['text']

        # GPT-4 review
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": f"Check this transcript for meaningful errors. If everything is fine, reply only: 'Text is OK'. If there are issues, propose an improved version:\n\n{raw_text}"}
            ]
        )

        result = gpt_response['choices'][0]['message']['content']

        return jsonify({
            'original': raw_text,
            'review': result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Start the app (this part is critical for Railway!)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
