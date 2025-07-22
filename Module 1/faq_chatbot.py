#from langchain_community.llms import Ollama
from openai import OpenAI  # Import OpenAI client for GitHub Models
#from langchain_community.chat_models import OllamaChat
#from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
import os
import faq_data

class FAQChatbotAgent:
    def __init__(self):
        
        os.environ['GITHUB_TOKEN'] = "code"
        token = os.environ['GITHUB_TOKEN']
        endpoint = "https://models.github.ai/inference"
        self.model = "openai/gpt-4.1-nano"
        
        self.client = OpenAI(
        base_url = endpoint,
        api_key = token
)
        
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  # Use a suitable embedding model
        # Define the FAQ data as a dictionary
        self.faq_data = faq_data.data  # Import the FAQ data from the provided module

        #create vector store from FAQ data
        self.vector_store = self.create_vector_store()
    
    def create_vector_store(self):
        """Create a vector store from the FAQ data."""
        documents = []
        for key, value in self.faq_data.items():
            doc = Document(
                page_content=f"{key}: {value}",
                metadata={"category": key}
            )
            documents.append(doc)
            
        text_splitter = CharacterTextSplitter(
            chunk_size = 500,
            chunk_overlap = 50,
            separator = "\n"
        )
        
        chunks = text_splitter.split_documents(documents)
        
        vector_store = FAISS.from_documents(chunks, self.embeddings)
        return vector_store
    
    # Function to answer FAQ questions based on the knowledge base
        
    def answer_faq(self, question, k=3):
        relevant_docs = self.vector_store.similarity_search(question, k=k)
        knowledge = "\n".join([doc.page_content for doc in relevant_docs])
        
        message = [
            {
                "role": "system", 
                "content": f"Based on this knowledge: {knowledge}\n\nAnswer as an institutional FAQ chatbot. "
            },
            {
                "role": "user", 
                "content": question
            }
        ]
        
        # Use OpenAI client instead of LangChain
        response = self.client.chat.completions.create(
            model=self.model,
            messages=message,
            temperature=0.1
        )
        
        return response.choices[0].message.content

if __name__ == "__main__":
    agent = FAQChatbotAgent()
    
    while True:
        question = input("Ask a question (or type 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        answer = agent.answer_faq(question)
        print(answer) # Print the answer to the user's questionint(answer)