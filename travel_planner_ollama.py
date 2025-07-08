from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class TravelPlannerAgent:
    def __init__(self):
        self.llm = Ollama(model="mistral:7b")
        self.destinations_db = {
            "paris": {
                "attractions": ["Eiffel Tower", "Louvre", "Notre Dame"],
                "budget": "$$-$$$",
                "best_time": "April-June, September-October"
            },
            "tokyo": {
                "attractions": ["Tokyo Tower", "Senso-ji Temple", "Shibuya Crossing"],
                "budget": "$$$",
                "best_time": "March-May, September-November"
            }
        }
    
    def create_itinerary(self, destination, days, budget, interests):
        prompt = PromptTemplate(
            input_variables=["destination", "days", "budget", "interests"],
            template="""
            Create a detailed travel itinerary for:
            
            Destination: {destination}
            Duration: {days} days
            Budget: {budget}
            Interests: {interests}
            
            Include:
            - Daily schedule with activities
            - Recommended restaurants
            - Transportation tips
            - Budget breakdown
            - Packing suggestions
            
            Itinerary:
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(
            destination=destination,
            days=days,
            budget=budget,
            interests=interests
        )
        return response
    
    def get_travel_tips(self, destination):
        prompt = PromptTemplate(
            input_variables=["destination"],
            template="""
            Provide helpful travel tips for visiting {destination}:
            
            Include:
            - Cultural etiquette
            - Safety tips
            - Local customs
            - Currency and payment methods
            - Language basics
            - What to avoid
            
            Travel Tips:
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(destination=destination)
        return response
    
    def estimate_budget(self, destination, days, travelers, style):
        prompt = PromptTemplate(
            input_variables=["destination", "days", "travelers", "style"],
            template="""
            Estimate travel budget for:
            
            Destination: {destination}
            Duration: {days} days
            Number of travelers: {travelers}
            Travel style: {style} (budget/mid-range/luxury)
            
            Provide breakdown for:
            - Accommodation
            - Food and dining
            - Transportation
            - Activities and attractions
            - Miscellaneous expenses
            - Total estimated cost
            
            Budget Estimate:
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(
            destination=destination,
            days=days,
            travelers=travelers,
            style=style
        )
        return response

if __name__ == "__main__":
    agent = TravelPlannerAgent()
    print("Creating itinerary:")
    print(agent.create_itinerary("Paris", "5", "mid-range", "art, history, food"))
    print("\nTravel tips:")
    print(agent.get_travel_tips("Japan"))