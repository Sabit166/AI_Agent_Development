from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import pipeline
import torch

class CodeReviewAgent:
    def __init__(self):
        # Use CodeT5 for code-related tasks
        hf_pipeline = pipeline(
            "text2text-generation",
            model="Salesforce/codet5-base",
            max_length=1024,
            temperature=0.3,
            device=0 if torch.cuda.is_available() else -1
        )
        
        self.llm = HuggingFacePipeline(pipeline=hf_pipeline)
    
    def review_code(self, code, language="python"):
        prompt = PromptTemplate(
            input_variables=["code", "language"],
            template="""
            Review the following {language} code and provide feedback on:
            1. Code quality and best practices
            2. Potential bugs or issues
            3. Performance improvements
            4. Readability suggestions
            
            Code:
            {code}
            
            Review:
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(code=code, language=language)
        return response
    
    def explain_code(self, code):
        prompt = PromptTemplate(
            input_variables=["code"],
            template="""
            Explain what the following code does in simple terms:
            
            {code}
            
            Explanation:
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(code=code)
        return response

if __name__ == "__main__":
    agent = CodeReviewAgent()
    sample_code = """
def calculate_area(radius):
    area = 3.14 * radius * radius
    return area
    """
    print("Code Review:")
    print(agent.review_code(sample_code))
    print("\nCode Explanation:")
    print(agent.explain_code(sample_code))