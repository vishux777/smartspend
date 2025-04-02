import streamlit as st
import requests
import os
import json

# Page configuration
st.set_page_config(
    page_title="SmartSpend - Expense Categorization Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for theme toggle and styles
st.markdown("""
<style>
    /* Base styles */
    .stApp {
        transition: background-color 0.3s ease;
    }
    
    /* Theme toggle switch */
    .theme-switch-container {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .theme-switch {
        position: relative;
        display: inline-block;
        width: 60px;
        height: 34px;
    }
    
    .theme-switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: .4s;
        border-radius: 34px;
    }
    
    .slider:before {
        position: absolute;
        content: "";
        height: 26px;
        width: 26px;
        left: 4px;
        bottom: 4px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }
    
    input:checked + .slider {
        background-color: #2196F3;
    }
    
    input:checked + .slider:before {
        transform: translateX(26px);
    }
    
    .theme-label {
        margin-left: 10px;
        font-weight: bold;
    }
    
    /* Dark theme specific styles */
    .dark-theme {
        background-color: #262730;
        color: #ffffff;
    }
    
    .dark-theme .stTextInput > div > div > input {
        background-color: #3b3b3b;
        color: white;
    }
    
    .dark-theme .stButton>button {
        background-color: #4e4e4e;
        color: white;
    }
</style>

<script>
    // Theme toggle functionality
    document.addEventListener('DOMContentLoaded', function() {
        const themeSwitch = document.getElementById('themeSwitch');
        const savedTheme = localStorage.getItem('theme');
        
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            if (themeSwitch) themeSwitch.checked = true;
        }
        
        if (themeSwitch) {
            themeSwitch.addEventListener('change', function() {
                if (this.checked) {
                    document.body.classList.add('dark-theme');
                    localStorage.setItem('theme', 'dark');
                } else {
                    document.body.classList.remove('dark-theme');
                    localStorage.setItem('theme', 'light');
                }
            });
        }
    });
</script>

<div class="theme-switch-container">
    <label class="theme-switch">
        <input type="checkbox" id="themeSwitch">
        <span class="slider"></span>
    </label>
    <span class="theme-label">🌙 Dark Mode</span>
</div>
""", unsafe_allow_html=True)

# Get API key from environment variable or Streamlit secrets
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")

# Try to get from Streamlit secrets if not in environment
if not MISTRAL_API_KEY and hasattr(st, "secrets"):
    MISTRAL_API_KEY = st.secrets.get("MISTRAL_API_KEY", "")

def get_category_from_mistral(description):
    """Calls Mistral AI API to categorize an expense description."""
    
    if not MISTRAL_API_KEY:
        st.warning("Mistral API key not found. Using local categorization.")
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
        st.warning("No valid response from API. Using local categorization.")
        return get_default_category(description)
    except Exception as e:
        st.error(f"Error with API: {str(e)}. Using local categorization.")
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
        st.error(f"Error processing query: {str(e)}")
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

# Initialize session state if not already initialized
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Alternative theme toggle using Streamlit's native components
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    # Force a rerun to apply theme changes
    st.experimental_rerun()

def main():
    # Sidebar
    with st.sidebar:
        st.title("💰 SmartSpend")
        st.markdown("AI-powered expense categorization")
        
        # Native theme toggle
        current_theme = st.session_state.theme
        theme_icon = "🌙" if current_theme == 'light' else "☀️"
        theme_text = "Dark Mode" if current_theme == 'light' else "Light Mode"
        
        if st.button(f"{theme_icon} Switch to {theme_text}", key="theme_toggle", use_container_width=True):
            toggle_theme()
        
        st.markdown("---")
        
        # New chat button
        if st.button("🔄 New Chat", key="new_chat", use_container_width=True):
            st.session_state.chat_history = []
            st.experimental_rerun()
        
        # Chat history
        if st.session_state.chat_history:
            st.markdown("### Chat History")
            for i, chat in enumerate(st.session_state.chat_history):
                if "question" in chat:
                    question_preview = chat["question"][:20] + "..." if len(chat["question"]) > 20 else chat["question"]
                    if st.button(f"🗨️ {question_preview}", key=f"history_{i}", use_container_width=True):
                        # Display the selected chat
                        pass
        else:
            st.info("No chat history yet.")
        
        st.markdown("---")
        
        # API status
        if MISTRAL_API_KEY:
            st.success("✅ AI API connected")
        else:
            st.warning("⚠️ Using offline mode")
        
        st.markdown("---")
        
        # About
        st.markdown("### About")
        st.markdown("SmartSpend helps you categorize expenses and manage your finances better.")
        
        # Credits
        st.markdown("---")
        st.caption("© 2025 SmartSpend")

    # Main Content
    st.title("SmartSpend Assistant")
    st.markdown("AI-powered expense categorization to simplify your financial tracking")
    
    # Apply theme-based styles
    if st.session_state.theme == 'dark':
        st.markdown("""
        <style>
        .stApp {
            background-color: #262730;
            color: white;
        }
        .stTextInput, .stSelectbox {
            background-color: #3b3b3b;
        }
        .stButton>button {
            background-color: #4e4e4e;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["💬 Expense Categorization", "❓ Finance Questions"])
    
    # Tab 1: Expense Categorization
    with tab1:
        st.markdown("### Categorize Your Expense")
        
        # Input form with explicit submit button
        with st.form(key="expense_form"):
            expense_desc = st.text_input("Enter expense description:", 
                                         placeholder="e.g., Uber ride to airport, Grocery shopping at Walmart...",
                                         key="expense-desc")
            
            # Important: This fixed submit button should resolve the error
            submit_expense = st.form_submit_button("Categorize", use_container_width=True)
        
        # Example chips outside the form
        st.markdown("### Examples:")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Dinner at restaurant", use_container_width=True):
                expense_desc = "Dinner at an Italian restaurant"
                # Submit form programmatically not supported directly
                
        with col2:
            if st.button("Netflix subscription", use_container_width=True):
                expense_desc = "Monthly Netflix subscription"
                # Submit form programmatically not supported directly
                
        with col3:
            if st.button("Uber ride", use_container_width=True):
                expense_desc = "Uber ride to airport"
                # Submit form programmatically not supported directly
        
        # Process categorization
        if submit_expense and expense_desc:
            # Categorize
            category = get_category_from_mistral(expense_desc)
            
            # Display result
            st.success(f"Expense: {expense_desc}")
            st.info(f"Category: {category}")
            
            # Add to history
            st.session_state.chat_history.append({
                "question": expense_desc,
                "answer": category,
                "type": "categorization"
            })
    
    # Tab 2: Finance Questions
    with tab2:
        st.markdown("### Ask a Finance Question")
        
        # Input form with explicit submit button
        with st.form(key="query_form"):
            query = st.text_input("Ask anything about expenses or categories...", 
                                  placeholder="e.g., How do I budget for travel?",
                                  key="query-input")
            
            # Important: This fixed submit button should resolve the error
            submit_query = st.form_submit_button("Ask", use_container_width=True)
        
        # Example buttons outside the form
        st.markdown("### Examples:")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("How to budget for travel?", use_container_width=True):
                query = "How should I budget for travel?"
                # Submit form programmatically not supported directly
                
        with col2:
            if st.button("50/30/20 budget rule", use_container_width=True):
                query = "What is the 50/30/20 rule?"
                # Submit form programmatically not supported directly
                
        with col3:
            if st.button("Tips to reduce expenses", use_container_width=True):
                query = "Tips for reducing monthly expenses"
                # Submit form programmatically not supported directly
        
        # Process query
        if submit_query and query:
            # Get response
            response = get_query_response(query)
            
            # Display result
            st.success(f"Question: {query}")
            st.info(f"Answer: {response}")
            
            # Add to history
            st.session_state.chat_history.append({
                "question": query,
                "answer": response,
                "type": "query"
            })

if __name__ == "__main__":
    main()