from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

class FAQChatbotAgent:
    def __init__(self):
        # Load Hugging Face model for conversational AI
        model_name = "microsoft/DialoGPT-medium"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Create pipeline
        hf_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=200,
            temperature=0.7,
            device=0 if torch.cuda.is_available() else -1
        )
        
        self.llm = HuggingFacePipeline(pipeline=hf_pipeline)
        
        # FAQ knowledge base
        self.faq_data = {
            "hours": "We are open Monday-Friday 9AM-6PM, Saturday 10AM-4PM",
            "location": "We are located at 123 Main Street, Downtown",
            "contact": "You can reach us at (555) 123-4567 or email@company.com",
            "returns": "We accept returns within 30 days with receipt",
            "shipping": "Standard shipping takes 3-5 business days, express 1-2 days"
        }
    
    def answer_faq(self, question):
        # Create prompt template
        prompt = PromptTemplate(
            input_variables=["question", "knowledge"],
            template="""
            You are a helpful customer service agent. Answer the customer's question based on the knowledge provided.
            
            Knowledge Base: {knowledge}
            Customer Question: {question}
            
            Provide a helpful and friendly response. If the information isn't in the knowledge base, politely say you'll need to transfer them to a human agent.
            
            Answer:
            """
        )
        
        knowledge = "\n".join([f"{k}: {v}" for k, v in self.faq_data.items()])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(question=question, knowledge=knowledge)
        return response

if __name__ == "__main__":
    agent = FAQChatbotAgent()
    print(agent.answer_faq("What are your business hours?"))