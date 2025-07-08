from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import pipeline
import torch

class WritingAssistantAgent:
    def __init__(self):
        # Use T5 model for text generation
        hf_pipeline = pipeline(
            "text2text-generation",
            model="google/flan-t5-base",
            max_length=512,
            temperature=0.8,
            device=0 if torch.cuda.is_available() else -1
        )
        
        self.llm = HuggingFacePipeline(pipeline=hf_pipeline)
    
    def improve_text(self, text, task="improve"):
        prompts = {
            "improve": "Improve and enhance the following text to make it more professional and clear: {text}",
            "summarize": "Summarize the following text in a concise manner: {text}",
            "expand": "Expand and elaborate on the following text with more details: {text}",
            "correct": "Correct any grammar and spelling errors in the following text: {text}"
        }
        
        prompt = PromptTemplate(
            input_variables=["text"],
            template=prompts.get(task, prompts["improve"])
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(text=text)
        return response
    
    def generate_content(self, topic, content_type="blog"):
        content_prompts = {
            "blog": "Write a engaging blog post about {topic}. Include an introduction, main points, and conclusion.",
            "email": "Write a professional email about {topic}.",
            "summary": "Write a brief summary about {topic}.",
            "outline": "Create a detailed outline for a presentation about {topic}."
        }
        
        prompt = PromptTemplate(
            input_variables=["topic"],
            template=content_prompts.get(content_type, content_prompts["blog"])
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(topic=topic)
        return response

if __name__ == "__main__":
    agent = WritingAssistantAgent()
    text = "AI is good technology."
    print("Original:", text)
    print("Improved:", agent.improve_text(text, "improve"))
    print("Content:", agent.generate_content("artificial intelligence", "blog"))