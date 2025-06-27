from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import spacy
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load LegalBERT
tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained("nlpaueb/legal-bert-base-uncased")

# --- Helper Functions ---

def extract_clauses(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 0]

def classify_risk(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    prediction = torch.argmax(logits, dim=1).item()
    return prediction % 4  # Simplify to 4 categories for pixel display

def gpt_summary(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a legal assistant that simplifies complex documents."},
                {"role": "user", "content": f"Summarize this legal text in plain language:\n\n{text}"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return "Summary not available (API error)."

# --- API Endpoint ---

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    text = data.get("text", "")

    clauses = extract_clauses(text)
    risks = [classify_risk(clause) for clause in clauses]
    summary = gpt_summary(text)

    return jsonify({
        "summary": summary,
        "clauses": clauses,
        "risks": risks
    })

# --- Run App ---

if __name__ == '__main__':
    app.run(debug=True)
