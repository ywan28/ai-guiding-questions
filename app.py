from flask import Flask, request, jsonify, render_template
import openai
import fitz  # PyMuPDF

app = Flask(__name__)

# Replace with your actual OpenAI API key
openai.api_key = "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"

# Map slider values to complexity descriptions
complexity_labels = [
    "straightforward",
    "basic",
    "amateur",
    "moderate",
    "advanced",
    "sophisticated"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_questions():
    data = request.get_json()
    user_text = data.get('text', '')
    num_questions = int(data.get('numQuestions', 5))
    complexity_index = int(data.get('complexityLevel', 2))

    # Clamp values just in case
    num_questions = max(1, min(num_questions, 10))
    complexity_label = complexity_labels[min(max(complexity_index, 0), 5)]

    prompt = f"""You are an assistant that creates {complexity_label} guiding questions 
to help someone explore or reflect on a piece of writing.

Generate {num_questions} thoughtful, well-phrased questions based on the following text:

Text:
{user_text}

Questions:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        questions = response['choices'][0]['message']['content'].strip()
        return jsonify({'questions': questions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return jsonify({'text': text.strip()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
