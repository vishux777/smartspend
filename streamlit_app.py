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

# Initialize theme in session state if not already initialized
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Apply custom theme CSS
if st.session_state.theme == 'dark':
    st.markdown("""
    <style>
    /* MAIN BACKGROUND - Rich deep blue gradient with improved readability */
    .stApp {
        background: linear-gradient(140deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* TEXT ELEMENTS - High contrast for better readability */
    p, div, span, label, li, td, th {
        color: rgba(255, 255, 255, 0.95) !important;
        font-weight: 400 !important;
    }
    
    /* HEADINGS - Bold, clear hierarchy with subtle glow */
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 0px 2px 3px rgba(0, 0, 0, 0.3);
        letter-spacing: 0.5px;
    }
    
    h2, h3 {
        color: #f8fafc !important;
        font-weight: 600 !important;
        text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    h4, h5, h6 {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }
    
    /* LINKS - Vibrant and clearly visible */
    a {
        color: #38bdf8 !important;
        text-decoration: none !important;
        font-weight: 500 !important;
    }
    
    a:hover {
        color: #0ea5e9 !important;
        text-decoration: underline !important;
    }
    
    /* INPUTS - Enhanced contrast with glowing focus state */
    .stTextInput > div > div > input {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        font-size: 16px !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.3) !important;
        background-color: #0f172a !important;
    }
    
    /* BUTTONS - Bold gradient with enhanced hover effect */
    .stButton > button {
        background: linear-gradient(to right, #0284c7, #38bdf8) !important;
        color: white !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 12px -1px rgba(0, 0, 0, 0.25), 0 3px 6px -1px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-2px) !important;
        background: linear-gradient(to right, #0369a1, #0284c7) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.2), 0 1px 2px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* SIDEBAR - Deep rich background with subtle border */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(148, 163, 184, 0.2) !important;
    }
    
    /* Sidebar heading for better contrast */
    [data-testid="stSidebar"] h1 {
        color: #38bdf8 !important;
    }
    
    /* Horizontal rule in sidebar */
    [data-testid="stSidebar"] hr {
        border-color: rgba(148, 163, 184, 0.2) !important;
        margin: 24px 0 !important;
    }
    
    /* ALERT BOXES - Enhanced visibility with clear borders */
    div.stAlert > div {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
    }
    
    /* Better scrollbars for dark mode */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    /* Category tags with vibrant color coding */
    .category-tag {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        margin-right: 6px;
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    /* Tab styling for dark mode */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
        background-color: #1e293b !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b !important;
        color: white !important;
        border-radius: 4px 4px 0 0 !important;
        margin-right: 2px !important;
        padding: 10px 16px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
    }
    
    /* Form styling for dark mode */
    [data-testid="stForm"] {
        background-color: #1e293b !important;
        padding: 20px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
    }
    </style>
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
    
    # Food and Dining
    if any(keyword in desc for keyword in ["restaurant", "cafe", "coffee", "dinner", "lunch", "breakfast", "meal", "pizza", "burger", "food", "grocery", "groceries", "supermarket"]):
        return "food"
    
    # Transportation
    if any(keyword in desc for keyword in ["uber", "lyft", "taxi", "car", "gas", "fuel", "bus", "train", "subway", "metro", "transportation", "flight", "airline", "toll"]):
        return "transportation"
    
    # Housing
    if any(keyword in desc for keyword in ["rent", "mortgage", "apartment", "house", "housing", "property", "real estate", "condo", "maintenance", "repair", "furniture"]):
        return "housing"
    
    # Utilities
    if any(keyword in desc for keyword in ["electricity", "water", "gas", "internet", "wifi", "phone", "bill", "utility", "utilities", "cable", "subscription"]):
        return "utilities"
    
    # Entertainment
    if any(keyword in desc for keyword in ["movie", "theater", "concert", "show", "netflix", "spotify", "music", "game", "entertainment", "party", "event", "streaming", "subscription"]):
        return "entertainment"
    
    # Shopping
    if any(keyword in desc for keyword in ["clothing", "clothes", "shirt", "pants", "shoe", "amazon", "online shopping", "mall", "store", "purchase", "retail", "shopping"]):
        return "shopping"
    
    # Travel
    if any(keyword in desc for keyword in ["hotel", "airbnb", "vacation", "travel", "trip", "flight", "booking", "resort", "tourism"]):
        return "travel"
    
    # Health
    if any(keyword in desc for keyword in ["doctor", "medical", "medicine", "healthcare", "pharmacy", "prescription", "hospital", "dental", "gym", "fitness", "health"]):
        return "health"
    
    # Education
    if any(keyword in desc for keyword in ["tuition", "school", "college", "university", "class", "course", "book", "education", "tutorial", "learning", "training"]):
        return "education"
    
    # Default to "other" if no category matches
    return "other"

def toggle_theme():
    """Toggle between light and dark mode."""
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'
    # Rerun the app with the new theme
    st.experimental_rerun()

def main():
    # Initialize chat history if it doesn't exist
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar with application controls
    with st.sidebar:
        st.title("💰 SmartSpend")
        st.markdown("AI-powered expense categorization")
        
        # Theme toggle button in the same position
        current_theme = st.session_state.theme
        icon = "🌙" if current_theme == 'light' else "☀️"
        theme_label = "Switch to Dark Mode" if current_theme == 'light' else "Switch to Light Mode"
        
        # Custom styled button with clearer purpose
        if st.button(f"{icon} {theme_label}", key="theme_toggle", use_container_width=True):
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
        st.caption("© 2025 SmartSpend \n | Created By: Vishwas 12306388 | Vikram Singh 12324502 | Debaparkash Jena 12316470")

    # Main Content
    st.title("SmartSpend Assistant")
    st.markdown("AI-powered expense categorization to simplify your financial tracking")
    
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