import streamlit as st
import requests
import os
from dotenv import load_dotenv
import json

# Page configuration
st.set_page_config(
    page_title="SmartSpend - Expense Categorization Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables from .env file if it exists
load_dotenv()

# Get API key from environment variable or Streamlit secrets
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

# Try to get from Streamlit secrets if not in environment
if not MISTRAL_API_KEY and hasattr(st, "secrets"):
    MISTRAL_API_KEY = st.secrets.get("MISTRAL_API_KEY")

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

# Custom CSS for dark mode and styling
def apply_custom_css():
    st.markdown("""
    <style>
    /* General styling */
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Card styling */
    .card {
        background-color: #283142;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        max-width: 80%;
        display: flex;
        align-items: flex-start;
    }
    
    .user-message {
        background-color: #4C72B0;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 0;
    }
    
    .bot-message {
        background-color: #283142;
        border-bottom-left-radius: 0;
    }
    
    /* Category tag styling */
    .category-tag {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 8px;
        font-size: 14px;
        margin-left: 5px;
        font-weight: 500;
    }
    
    .tag-food { background-color: rgba(76, 175, 80, 0.2); color: #4CAF50; }
    .tag-transportation { background-color: rgba(33, 150, 243, 0.2); color: #2196F3; }
    .tag-housing { background-color: rgba(156, 39, 176, 0.2); color: #9C27B0; }
    .tag-utilities { background-color: rgba(255, 152, 0, 0.2); color: #FF9800; }
    .tag-entertainment { background-color: rgba(233, 30, 99, 0.2); color: #E91E63; }
    .tag-shopping { background-color: rgba(0, 188, 212, 0.2); color: #00BCD4; }
    .tag-health { background-color: rgba(244, 67, 54, 0.2); color: #F44336; }
    .tag-education { background-color: rgba(121, 85, 72, 0.2); color: #795548; }
    .tag-travel { background-color: rgba(255, 87, 34, 0.2); color: #FF5722; }
    .tag-other { background-color: rgba(158, 158, 158, 0.2); color: #9E9E9E; }
    
    /* History list styling */
    .history-item {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .history-item:hover {
        background-color: #283142;
    }
    
    /* Example chips */
    .chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0;
    }
    
    .chip {
        background-color: #283142;
        padding: 8px 12px;
        border-radius: 16px;
        font-size: 14px;
        cursor: pointer;
        transition: background-color 0.2s, transform 0.2s;
    }
    
    .chip:hover {
        background-color: #384152;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state if not already initialized
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def main():
    apply_custom_css()

    # Sidebar
    with st.sidebar:
        st.title("💰 SmartSpend")
        st.markdown("AI-powered expense categorization")
        
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
    
    tab1, tab2 = st.tabs(["💬 Expense Categorization", "❓ Finance Questions"])
    
    # Tab 1: Expense Categorization
    with tab1:
        st.markdown("### Categorize Your Expense")
        
        # Example chips
        st.markdown("""
        <div class="chip-container">
            <div class="chip" onclick="
                document.getElementById('expense-desc').value = 'Dinner at an Italian restaurant';
                document.getElementById('categorize-btn').click();
            ">Dinner at restaurant</div>
            <div class="chip" onclick="
                document.getElementById('expense-desc').value = 'Monthly Netflix subscription';
                document.getElementById('categorize-btn').click();
            ">Netflix subscription</div>
            <div class="chip" onclick="
                document.getElementById('expense-desc').value = 'Uber ride to airport';
                document.getElementById('categorize-btn').click();
            ">Uber ride</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Input form
        with st.form(key="expense_form"):
            expense_desc = st.text_input("Enter expense description:", 
                                         placeholder="e.g., Uber ride to airport, Grocery shopping at Walmart...",
                                         key="expense-desc", 
                                         label_visibility="collapsed")
            submit_expense = st.form_submit_button("Categorize", use_container_width=True, type="primary",
                                                  key="categorize-btn")
        
        # Process categorization
        if submit_expense and expense_desc:
            # Add user message to chat history
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            
            # Categorize
            category = get_category_from_mistral(expense_desc)
            
            # Add to chat history
            st.session_state.chat_history.append({
                "question": expense_desc,
                "answer": category,
                "type": "categorization"
            })
            
            # Display chat
            for chat in st.session_state.chat_history:
                if "question" in chat:
                    # User message
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div>You: {chat["question"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Bot message
                    if chat["type"] == "categorization":
                        category = chat["answer"]
                        st.markdown(f"""
                        <div class="chat-message bot-message">
                            <div>Bot: I've categorized this as: <span class="category-tag tag-{category}">{category}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-message bot-message">
                            <div>Bot: {chat["answer"]}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.caption("Examples: \"Coffee at Starbucks\", \"Amazon Prime subscription\", \"Electricity bill\"")
    
    # Tab 2: Finance Questions
    with tab2:
        st.markdown("### Ask a Finance Question")
        
        # Example chips
        st.markdown("""
        <div class="chip-container">
            <div class="chip" onclick="
                document.getElementById('query-input').value = 'How should I budget for travel?';
                document.getElementById('query-btn').click();
            ">How to budget for travel?</div>
            <div class="chip" onclick="
                document.getElementById('query-input').value = 'What is the 50/30/20 rule?';
                document.getElementById('query-btn').click();
            ">50/30/20 budget rule</div>
            <div class="chip" onclick="
                document.getElementById('query-input').value = 'Tips for reducing monthly expenses';
                document.getElementById('query-btn').click();
            ">Tips to reduce expenses</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Input form
        with st.form(key="query_form"):
            query = st.text_input("Ask anything about expenses or categories...", 
                                  placeholder="e.g., How do I budget for travel?",
                                  key="query-input", 
                                  label_visibility="collapsed")
            submit_query = st.form_submit_button("Ask", use_container_width=True, type="primary", 
                                              key="query-btn")
        
        # Process query
        if submit_query and query:
            # Get response
            response = get_query_response(query)
            
            # Add to chat history
            st.session_state.chat_history.append({
                "question": query,
                "answer": response,
                "type": "query"
            })
            
            # Display chat
            for chat in st.session_state.chat_history:
                if "question" in chat:
                    # User message
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div>You: {chat["question"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Bot message
                    if chat["type"] == "categorization":
                        category = chat["answer"]
                        st.markdown(f"""
                        <div class="chat-message bot-message">
                            <div>Bot: I've categorized this as: <span class="category-tag tag-{category}">{category}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-message bot-message">
                            <div>Bot: {chat["answer"]}</div>
                        </div>
                        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()