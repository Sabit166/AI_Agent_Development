# --- Imports and Setup ---
import os
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
#from langchain_core.messages import HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter



class SessionHistoryManager:
    def __init__(self):
        self.store = {}

    def get_history(self, session_id: str) -> ChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

class FAQChatbotAgent:
    def __init__(self):
        # 1. Set up API connections first
        os.environ['GITHUB_TOKEN'] = ""
        token = os.environ['GITHUB_TOKEN']
        endpoint = "https://models.github.ai/inference"
        self.model = "openai/gpt-4.1-nano"
        
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable not set. Please provide a valid token.")
        
        self.llm = ChatOpenAI(
            base_url=endpoint,
            api_key=token,
            model=self.model,
            temperature=0.1
        )
        
        self.embedder = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
        self.history_manager = SessionHistoryManager()
        
        # 2. Load and process PDF with error handling
        try:
            self.docs = self.text_splitter()
            print(f"Processing {len(self.docs)} document chunks...")
            
            # FIXED: Limit the number of documents for initial testing
            limited_docs = self.docs[:50]  # Start with first 50 chunks
            print(f"Using {len(limited_docs)} chunks for vector store")
            
            vector_store = FAISS.from_documents(limited_docs, self.embedder)
            self.retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            print("✅ Vector store created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating vector store: {e}")
            print("🔧 Trying with cleaned and limited data...")
            
            # Fallback: Use basic text approach with heavy filtering
            try:
                clean_docs = self.create_fallback_docs()
                vector_store = FAISS.from_documents(clean_docs, self.embedder)
                self.retriever = vector_store.as_retriever(search_kwargs={"k": 3})
                print("✅ Fallback vector store created successfully!")
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {fallback_error}")
                raise fallback_error

    def create_fallback_docs(self):
        """Create a small set of clean documents as fallback."""
        from langchain.schema import Document
        
        # Load just first few pages
        file_path = (
            r"C:\Users\sabit\OneDrive\Desktop\AI AGENT DEVELOPMENT\context_aware_bot"
            r"\2-Aurelien-Geron-Hands-On-Machine-Learning-with-Scikit-Learn-Keras-and-Tensorflow_"
            r"-Concepts-Tools-and-Techniques-to-Build-Intelligent-Systems-OReilly-Media-2019.pdf"
        )
        loader = PyPDFLoader(file_path)
        pages = loader.load()[:5]  # Just first 5 pages
        
        clean_docs = []
        for i, page in enumerate(pages):
            if page.page_content and len(page.page_content.strip()) > 100:
                # Clean and limit the text
                clean_text = page.page_content.strip()[:2000]  # Limit to 2000 chars
                clean_text = ' '.join(clean_text.split())  # Normalize whitespace
                
                doc = Document(
                    page_content=clean_text,
                    metadata={"page": i+1, "source": "pdf"}
                )
                clean_docs.append(doc)
        
        return clean_docs

    def text_splitter(self):
        """Split the loaded PDF pages into manageable chunks."""
        # 2. Load PDF data first
        file_path = (
            r"C:\Users\sabit\OneDrive\Desktop\AI AGENT DEVELOPMENT\context_aware_bot"
            r"\2-Aurelien-Geron-Hands-On-Machine-Learning-with-Scikit-Learn-Keras-and-Tensorflow_"
            r"-Concepts-Tools-and-Techniques-to-Build-Intelligent-Systems-OReilly-Media-2019.pdf"
        )
        self.loader = PyPDFLoader(file_path)
        
        # FIXED: Load only first 20 pages to avoid memory/tokenizer issues
        all_pages = self.loader.load()
        self.pages = all_pages[:20]  # Limit to first 20 pages
        print(f"Number of pages loaded (limited): {len(self.pages)}")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Smaller chunks
            chunk_overlap=80,
            separators=["\n\n", "\n", ". ", "! ", "? ", " "]
        )
        
        chunks = text_splitter.split_documents(self.pages)
        print(f"Number of document chunks: {len(chunks)}")

        # Filter out very short or problematic chunks
        filtered_chunks = []
        for chunk in chunks:
            if (chunk.page_content and 
                len(chunk.page_content.strip()) > 50 and
                len(chunk.page_content) < 2000):
                filtered_chunks.append(chunk)
        
        print(f"Number of filtered chunks: {len(filtered_chunks)}")
        return filtered_chunks

    
    
    def context_aware_chat(self, question):
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, contextualize_q_prompt
        )
        
        qa_prompt_with_memory = ChatPromptTemplate.from_messages([
            ("system", """I'm your AI assistant specializing in Machine Learning, trained on Aurélien Géron's comprehensive "Hands-On Machine Learning" book. 

I can help you with:
🔹 Core ML concepts (supervised, unsupervised, reinforcement learning)
🔹 Scikit-Learn implementation details and best practices
🔹 Deep learning with Keras and TensorFlow
🔹 Feature engineering and data preprocessing techniques
🔹 Model evaluation, validation, and hyperparameter tuning
🔹 Real-world ML project workflows and tips

Based on the book content below, I'll provide clear, practical answers with examples when possible.

Book Context: {context}

I'll keep my responses concise yet informative, and I'll let you know if a topic isn't covered in the available sections."""),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        
        qa_chain_with_memory = create_stuff_documents_chain(self.llm, qa_prompt_with_memory)
        conversational_rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain_with_memory)
        
        conversational_chain_with_history = RunnableWithMessageHistory(
        conversational_rag_chain,
        self.history_manager.get_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
        )
        
        res = conversational_chain_with_history.invoke(
            {"input": question},
            config={"configurable": {"session_id": "user123"}}
        )
        return res['answer']
    

if __name__ == "__main__":
    try:
        agent = FAQChatbotAgent()
        
        print("🤖 Hands-On Machine Learning Assistant is ready!")
        print("📚 Ask me anything about ML concepts from Aurélien Géron's book")
        print("💡 Topics: Scikit-Learn, Keras, TensorFlow, ML algorithms, and more!")
        print("📝 Type 'exit' to quit\n")
        
        while True:
            print("-----------------------------------")
            question = input("👤 You: ")
            if question.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
                
            try:
                # FIXED: Remove session_id parameter
                answer = agent.context_aware_chat(question)
                print(f"🤖 ML Expert: {answer}\n")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print("🔄 Please try again with a different question.\n")
                
    except Exception as init_error:
        print(f"❌ Failed to initialize agent: {init_error}")
        print("💡 Try reducing the PDF size or check your dependencies.")