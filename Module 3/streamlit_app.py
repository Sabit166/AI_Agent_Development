import streamlit as st
import os
from datetime import datetime
import time

# Import your bot (make sure the file is in the same directory)
from context_aware_bot import FAQChatbotAgent

# Configure Streamlit page
st.set_page_config(
    page_title="ML Assistant Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        color: #1565c0;  /* Dark blue text for light blue background */
    }
    .bot-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
        color: #2e7d32;  /* Dark green text for light green background */
    }
    .user-message strong {
        color: #0d47a1;  /* Even darker blue for "You:" label */
    }
    .bot-message strong {
        color: #1b5e20;  /* Even darker green for "ML Expert:" label */
    }
    .timestamp {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .sidebar-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #424242;  /* Dark gray text for sidebar info */
    }
    .sidebar-info h4, .sidebar-info h5 {
        color: #1f77b4;  /* Blue headings in sidebar */
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'bot_initialized' not in st.session_state:
    st.session_state.bot_initialized = False
if 'bot_agent' not in st.session_state:
    st.session_state.bot_agent = None

def initialize_bot():
    """Initialize the bot with error handling"""
    try:
        with st.spinner("🔄 Initializing ML Assistant... This may take a moment."):
            # Check if GitHub token is set
            github_token = st.session_state.get('github_token', '')
            if github_token:
                os.environ['GITHUB_TOKEN'] = github_token
            
            agent = FAQChatbotAgent()
            st.session_state.bot_agent = agent
            st.session_state.bot_initialized = True
            st.success("✅ ML Assistant initialized successfully!")
            return True
    except Exception as e:
        st.error(f"❌ Failed to initialize bot: {str(e)}")
        st.error("💡 Please check your GitHub token and try again.")
        return False

def add_message(role, content, timestamp=None):
    """Add a message to the chat history"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M:%S")
    
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })

def display_chat_message(message):
    """Display a single chat message"""
    role = message["role"]
    content = message["content"]
    timestamp = message["timestamp"]
    
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You:</strong><br>
            {content}
            <div class="timestamp">🕒 {timestamp}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 ML Expert:</strong><br>
            {content}
            <div class="timestamp">🕒 {timestamp}</div>
        </div>
        """, unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # GitHub Token Input
    st.markdown("### 🔑 API Settings")
    github_token = st.text_input(
        "GitHub Token",
        type="password",
        help="Enter your GitHub Personal Access Token for API access",
        value=st.session_state.get('github_token', '')
    )
    
    if github_token:
        st.session_state.github_token = github_token
    
    # Initialize Bot Button
    if st.button("🚀 Initialize Bot", use_container_width=True):
        if github_token:
            initialize_bot()
        else:
            st.warning("⚠️ Please enter your GitHub token first.")
    
    # Bot Status
    st.markdown("### 📊 Bot Status")
    if st.session_state.bot_initialized:
        st.success("🟢 Bot is ready!")
    else:
        st.error("🔴 Bot not initialized")
    
    # Chat Controls
    st.markdown("### 💬 Chat Controls")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Information
    st.markdown("""
    <div class="sidebar-info">
        <h4>📚 About This Bot</h4>
        <p>This AI assistant specializes in Machine Learning concepts from Aurélien Géron's "Hands-On Machine Learning" book.</p>
        
        <h5>Topics covered:</h5>
        <ul>
            <li>🔹 Scikit-Learn</li>
            <li>🔹 Keras & TensorFlow</li>
            <li>🔹 ML Algorithms</li>
            <li>🔹 Model Evaluation</li>
            <li>🔹 Feature Engineering</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Main Content Area
st.markdown('<h1 class="main-header">🤖 Hands-On Machine Learning Assistant</h1>', unsafe_allow_html=True)

# Chat Interface
st.markdown("### 💬 Chat with your ML Expert")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        display_chat_message(message)

# Chat Input - FIXED VERSION
with st.form(key='chat_form', clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask me anything about Machine Learning:",
            placeholder="e.g., What is supervised learning?",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.form_submit_button("📤 Send", use_container_width=True)

# Handle user input - FIXED VERSION
if send_button and user_input.strip():
    if not st.session_state.bot_initialized:
        st.error("❌ Please initialize the bot first using the sidebar.")
    else:
        # Add user message
        add_message("user", user_input)
        
        # Get bot response
        try:
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.bot_agent.context_aware_chat(user_input)
                add_message("bot", response)
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            add_message("bot", error_msg)
        
        # Form automatically clears, so no need for manual clearing
        st.rerun()

# Sample Questions - FIXED VERSION
if not st.session_state.messages:
    st.markdown("### 💡 Try asking these sample questions:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("What is supervised learning?", use_container_width=True):
            if st.session_state.bot_initialized:
                add_message("user", "What is supervised learning?")
                try:
                    response = st.session_state.bot_agent.context_aware_chat("What is supervised learning?")
                    add_message("bot", response)
                except Exception as e:
                    add_message("bot", f"Sorry, I encountered an error: {str(e)}")
                st.rerun()
    
    with col2:
        if st.button("Explain decision trees", use_container_width=True):
            if st.session_state.bot_initialized:
                add_message("user", "Explain decision trees")
                try:
                    response = st.session_state.bot_agent.context_aware_chat("Explain decision trees")
                    add_message("bot", response)
                except Exception as e:
                    add_message("bot", f"Sorry, I encountered an error: {str(e)}")
                st.rerun()
    
    with col3:
        if st.button("How to evaluate ML models?", use_container_width=True):
            if st.session_state.bot_initialized:
                add_message("user", "How to evaluate ML models?")
                try:
                    response = st.session_state.bot_agent.context_aware_chat("How to evaluate ML models?")
                    add_message("bot", response)
                except Exception as e:
                    add_message("bot", f"Sorry, I encountered an error: {str(e)}")
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🚀 Built with Streamlit | 📖 Powered by "Hands-On Machine Learning" by Aurélien Géron</p>
</div>
""", unsafe_allow_html=True)