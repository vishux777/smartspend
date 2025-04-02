import streamlit as st
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables from .env file if it exists
load_dotenv()

# Get API key from environment variable or Streamlit secrets
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

# Try to get from Streamlit secrets if not in environment
if not MISTRAL_API_KEY and hasattr(st, "secrets"):
    MISTRAL_API_KEY = st.secrets.get("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    st.error("MISTRAL_API_KEY not set. Please set it in environment variables or Streamlit secrets.")
    st.stop()

MISTRAL_ENDPOINT = "https://api.mistral.ai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

def get_category_from_mistral(description):
    """Calls Mistral AI API to categorize an expense description."""
    try:
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
        st.write("No valid choices in response:", response_data)
        return "other"
    except requests.exceptions.Timeout:
        st.error("Request to Mistral API timed out.")
        return "other"
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error: {e.response.status_code}")
        return "other"
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "other"

def get_query_response(query):
    """Handles general queries via Mistral API."""
    try:
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
        st.error(f"Error processing query: {e}")
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

# Main Streamlit UI
def main():
    st.title("SmartSpend - Expense Categorization API")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Test App", "API Info", "Web App"])
    
    with tab1:
        st.header("Categorize an Expense")
        description = st.text_input("Enter expense description (e.g., 'Dinner at restaurant')")
        if st.button("Categorize"):
            if description.strip():
                category = get_category_from_mistral(description)
                friendly_messages = {
                    "food": "This looks like a food expense.",
                    "transportation": "This is categorized as transportation.",
                    "housing": "This is a housing-related expense.",
                    "utilities": "This falls under utilities.",
                    "entertainment": "This is categorized as entertainment.",
                    "shopping": "This appears to be a shopping expense.",
                    "travel": "This is a travel expense.",
                    "health": "This is a health-related expense.",
                    "education": "This is an education expense.",
                    "other": "This doesn't fit our standard categories."
                }
                st.success(f"Category: {category}")
                st.write(friendly_messages.get(category, f"Categorized as {category}."))
            else:
                st.error("Please enter a description.")

        st.header("Ask a Finance Question")
        query = st.text_input("Enter your question (e.g., 'How do I budget for travel?')")
        if st.button("Ask"):
            if query.strip():
                response = get_query_response(query)
                st.write("Answer:", response)
            else:
                st.error("Please enter a question.")
    
    with tab2:
        st.header("API Endpoints")
        st.markdown("""
        This Streamlit app serves the following API endpoints:
        
        - `/categorize` - POST endpoint for categorizing expenses
          - Request body: `{"description": "Your expense description"}`
          - Returns: `{"category": "category_name", "message": "friendly message"}`
        
        - `/query` - POST endpoint for finance questions
          - Request body: `{"query": "Your finance question"}`
          - Returns: `{"response": "AI response to query"}`
        """)
    
    with tab3:
        st.header("Web Application")
        st.markdown("""
        Visit our web application for a more interactive experience:
        
        [SmartSpend Web App](https://github.com/yourusername/smartspend)
        
        The web application offers:
        - A user-friendly interface for expense categorization
        - Dark/Light mode
        - Chat history
        - Interactive UI with real-time feedback
        """)
        
        st.subheader("Instructions for deploying with GitHub")
        st.markdown("""
        1. Fork the repository on GitHub
        2. Add your MISTRAL_API_KEY in Streamlit secrets or environment variables
        3. Connect your GitHub repository to Streamlit Cloud
        4. Deploy and use the app!
        """)
        
    # Footer
    st.markdown("---")
    st.write("Powered by Mistral AI and Streamlit")

# Run the Streamlit application
if __name__ == "__main__":
    main()