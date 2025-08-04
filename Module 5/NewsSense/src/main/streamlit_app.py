import streamlit as st
import asyncio
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any
import os

import sys

# FIX IMPORT PATHS FIRST
current_dir = os.path.dirname(os.path.abspath(__file__))  # /src/main/
src_dir = os.path.dirname(current_dir)                   # /src/
project_root = os.path.dirname(src_dir)                  # /NewSense-1/

# Add src directory to Python path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# NOW IMPORT YOUR MODULES
try:
    from agent.news_intelligence_agent import news_intelligence_agent
    from models.user_context import UserContext
    from agents import Runner
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()
# Page configuration
st.set_page_config(
    page_title="News Intelligence Assistant",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #2196F3;
    }
    .chat-message.assistant {
        background-color: #f0f0f0;
        border-left: 5px solid #4CAF50;
    }
    .chat-message .content {
        display: flex;
        margin-top: 0.5rem;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .message {
        flex: 1;
        color: #000000;
    }
    .timestamp {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history and user context
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "user_context" not in st.session_state:
    st.session_state.user_context = UserContext(
        user_id=str(uuid.uuid4())
    )

if "processing_message" not in st.session_state:
    st.session_state.processing_message = None

# Function to format agent responses based on output type
def format_agent_response(output):
    # Check if output is a Pydantic model and convert to dict
    if hasattr(output, "model_dump"):
        output = output.model_dump()

    if isinstance(output, dict):
        # Example: handle news summary or intelligence outputs
        if "headline" in output and "summary" in output:
            html = f"""
            <h3>{output.get('headline', 'News')}</h3>
            <p>{output.get('summary', '')}</p>
            """
            if "source" in output:
                html += f"<p><strong>Source:</strong> {output.get('source')}</p>"
            if "published_at" in output:
                html += f"<p><strong>Published:</strong> {output.get('published_at')}</p>"
            return html

        # Example: handle list of articles
        if "articles" in output and isinstance(output["articles"], list):
            html = "<h3>Top News Articles</h3><ul>"
            for article in output["articles"]:
                title = article.get("headline", "Untitled")
                url = article.get("url", "#")
                html += f'<li><a href="{url}" target="_blank">{title}</a></li>'
            html += "</ul>"
            return html

        # Example: handle insights or analytics
        if "insights" in output:
            html = "<h3>Insights</h3><ul>"
            for insight in output["insights"]:
                html += f"<li>{insight}</li>"
            html += "</ul>"
            return html

    # Default: return as string
    return str(output)

# Function to handle user input
def handle_user_message(user_input: str):
    # Add user message to chat history immediately
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })

    # Set the message for processing in the next rerun
    st.session_state.processing_message = user_input



# Main chat interface
st.title("📰 News Intelligence Assistant")
st.caption("Ask me about travel destinations, flight options, hotel recommendations, and more!")

# Display chat messages
for message in st.session_state.chat_history:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed={st.session_state.user_context.user_id}" class="avatar" />
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/bottts/svg?seed=travel-agent" class="avatar" />
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# User input
user_input = st.chat_input("Ask about travel plans...")
if user_input:
    handle_user_message(user_input)
    st.rerun()

# Process message if needed
if st.session_state.processing_message:
    user_input = st.session_state.processing_message
    st.session_state.processing_message = None
    
    # Process the message asynchronously
    with st.spinner("Thinking..."):
        try:
            # Prepare input for the agent using chat history
            if len(st.session_state.chat_history) > 1:
                # Convert chat history to input list format for the agent
                input_list = []
                for msg in st.session_state.chat_history:
                    input_list.append({"role": msg["role"], "content": msg["content"]})
            else:
                # First message
                input_list = user_input
            
            # Run the agent with the input
            result = asyncio.run(Runner.run(
                news_intelligence_agent, 
                input_list, 
                context=st.session_state.user_context
            ))
            
            # Format the response based on output type
            response_content = format_agent_response(result.final_output)
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
            
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
        
        # Force a rerun to display the AI response
        st.rerun()

# Footer
st.divider()
st.caption("Powered by OpenAI Agents SDK | Built with Streamlit")