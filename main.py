import os
import requests
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Create Flask application
app = Flask(__name__, static_folder="static")

# Get API key from environment variable
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

def get_category_from_mistral(description):
    """Calls Mistral AI API to categorize an expense description."""
    
    if not MISTRAL_API_KEY:
        print("Mistral API key not found. Using local categorization.")
        return get_default_category(description)
    
    try:
        MISTRAL_ENDPOINT = "https://api.mistral.ai/v1/chat/completions"
        HEADERS = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistral-tiny",
            "messages": [
                {"role": "system", "content": "You are an expense categorization assistant. Categorize expenses into one of these categories: food, transportation, housing, utilities, entertainment, shopping, travel, health, education, or other. Reply with just the category name in lowercase."},
                {"role": "user", "content": f"Categorize this expense: {description}"}
            ],
            "temperature": 0.3
        }
        response = requests.post(MISTRAL_ENDPOINT, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()

        response_data = response.json()
        if "choices" in response_data and response_data["choices"]:
            category = response_data["choices"][0].get("message", {}).get("content", "other").strip().lower()
            common_categories = ["food", "transportation", "housing", "utilities", "entertainment", 
                               "shopping", "travel", "health", "education", "other"]
            for c in common_categories:
                if c in category:
                    return c
            return "other"
        print("No valid response from API. Using local categorization.")
        return get_default_category(description)
    except Exception as e:
        print(f"Error with API: {str(e)}. Using local categorization.")
        return get_default_category(description)

def get_query_response(query):
    """Handles general queries via Mistral API."""
    
    if not MISTRAL_API_KEY:
        return "I'm currently in offline mode. For financial advice, please make sure you're tracking your expenses regularly and categorizing them properly to understand your spending patterns."
    
    try:
        MISTRAL_ENDPOINT = "https://api.mistral.ai/v1/chat/completions"
        HEADERS = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistral-tiny",
            "messages": [
                {"role": "system", "content": "You are an expense management assistant. Provide helpful, concise responses about expense categories, finance management, and budgeting."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        response = requests.post(MISTRAL_ENDPOINT, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()

        response_data = response.json()
        if "choices" in response_data and response_data["choices"]:
            return response_data["choices"][0].get("message", {}).get("content", "").strip()
        return "I couldn't process your query. Please try again."
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return "I'm having trouble connecting to my knowledge base. Please try again later."

def get_default_category(description):
    """Local fallback categorization when API is unavailable."""
    desc = description.lower()
    if "restaurant" in desc or "food" in desc or "dinner" in desc or "lunch" in desc or "breakfast" in desc or "coffee" in desc:
        return "food"
    elif "uber" in desc or "taxi" in desc or "bus" in desc or "train" in desc or "gas" in desc or "car" in desc:
        return "transportation"
    elif "rent" in desc or "mortgage" in desc or "home" in desc:
        return "housing"
    elif "electricity" in desc or "water" in desc or "bill" in desc or "internet" in desc or "phone" in desc:
        return "utilities"
    elif "movie" in desc or "netflix" in desc or "spotify" in desc or "concert" in desc or "game" in desc:
        return "entertainment"
    elif "amazon" in desc or "mall" in desc or "store" in desc or "buy" in desc or "purchase" in desc:
        return "shopping"
    elif "doctor" in desc or "medicine" in desc or "hospital" in desc or "health" in desc:
        return "health"
    elif "course" in desc or "book" in desc or "tuition" in desc or "class" in desc or "school" in desc:
        return "education"
    elif "hotel" in desc or "flight" in desc or "vacation" in desc or "trip" in desc or "travel" in desc:
        return "travel" 
    else:
        return "other"

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/categorize', methods=['POST'])
def api_categorize():
    data = request.get_json()
    
    if not data or 'description' not in data:
        return jsonify({'error': 'No expense description provided'}), 400
        
    description = data['description']
    category = get_category_from_mistral(description)
    
    return jsonify({
        'category': category,
        'description': description
    })

@app.route('/api/query', methods=['POST'])
def api_query():
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided'}), 400
        
    query = data['query']
    response = get_query_response(query)
    
    return jsonify({
        'response': response,
        'query': query
    })

@app.route('/api/status', methods=['GET'])
def api_status():
    has_api_key = bool(MISTRAL_API_KEY)
    
    return jsonify({
        'status': 'online',
        'api_available': has_api_key
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)