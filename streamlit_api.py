import streamlit as st
import json
from app import get_category_from_mistral, get_query_response, get_default_category

# Enable CORS
def enable_cors():
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    for key, value in headers.items():
        st.response_headers[key] = value

# API endpoint for categorizing expenses
def handle_categorize():
    enable_cors()
    
    try:
        # Get the request body
        body = json.loads(st.request.body)
        description = body.get("description", "")
        
        if not description:
            return {"status": "error", "message": "Missing description"}
        
        # Try to get category from Mistral
        try:
            category = get_category_from_mistral(description)
        except Exception as e:
            # Fallback to local categorization if Mistral fails
            category = get_default_category(description)
            st.error(f"Falling back to local categorization: {str(e)}")
        
        # Prepare friendly message
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
        
        return {
            "status": "success",
            "category": category,
            "message": friendly_messages.get(category, f"Categorized as {category}.")
        }
    except Exception as e:
        st.error(f"Error handling categorize: {str(e)}")
        return {"status": "error", "message": str(e)}

# API endpoint for queries
def handle_query():
    enable_cors()
    
    try:
        # Get the request body
        body = json.loads(st.request.body)
        query = body.get("query", "")
        
        if not query:
            return {"status": "error", "message": "Missing query"}
        
        # Get response from Mistral
        response = get_query_response(query)
        
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        st.error(f"Error handling query: {str(e)}")
        return {"status": "error", "message": str(e)}

# Route API requests
def api_router():
    # Get the request path
    path = st.query_params.get("_path", "")
    
    if path == "/categorize" and st.request.method == "POST":
        return handle_categorize()
    elif path == "/query" and st.request.method == "POST":
        return handle_query()
    elif st.request.method == "OPTIONS":
        enable_cors()
        return {"status": "success"}
    elif path == "/":
        enable_cors()
        return {"status": "success", "message": "API is running"}
    else:
        enable_cors()
        return {"status": "error", "message": "Invalid endpoint or method"}

# Main entry point for Streamlit Sharing
if __name__ == "__main__":
    # Check if this is an API request
    if "_path" in st.query_params:
        st.response = api_router()
        st.stop()
    else:
        # Import and run the main app if not an API request
        from app import main
        main()