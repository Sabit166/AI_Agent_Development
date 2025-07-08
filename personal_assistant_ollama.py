from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from datetime import datetime
import json

class PersonalAssistantAgent:
    def __init__(self):
        self.llm = Ollama(model="llama2:7b")
        self.user_context = {
            "name": "User",
            "preferences": [],
            "recent_tasks": []
        }
    
    def schedule_task(self, task, date_time):
        prompt = PromptTemplate(
            input_variables=["task", "date_time", "current_time"],
            template="""
            You are a personal assistant. Help schedule the following task:
            
            Task: {task}
            Requested Time: {date_time}
            Current Time: {current_time}
            
            Provide a professional response confirming the scheduling and any relevant reminders or suggestions.
            
            Response:
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(
            task=task, 
            date_time=date_time, 
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        
        # Store task
        self.user_context["recent_tasks"].append({
            "task": task,
            "scheduled_time": date_time,
            "created_at": datetime.now().isoformat()
        })
        
        return response
    
    def daily_briefing(self):
        prompt = PromptTemplate(
            input_variables=["tasks", "date"],
            template="""
            Create a daily briefing for today ({date}) including:
            
            Scheduled Tasks:
            {tasks}
            
            Provide a motivational morning briefing with task priorities and time management tips.
            
            Briefing:
            """
        )
        
        tasks = "\n".join([f"- {task['task']} at {task['scheduled_time']}" 
                          for task in self.user_context["recent_tasks"]])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(
            tasks=tasks if tasks else "No tasks scheduled",
            date=datetime.now().strftime("%Y-%m-%d")
        )
        return response
    
    def answer_general_question(self, question):
        prompt = PromptTemplate(
            input_variables=["question"],
            template="""
            You are a helpful personal assistant. Answer the following question in a friendly and informative way:
            
            Question: {question}
            
            Answer:
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(question=question)
        return response

if __name__ == "__main__":
    assistant = PersonalAssistantAgent()
    print("Scheduling task:")
    print(assistant.schedule_task("Team meeting", "2025-07-09 14:00"))
    print("\nDaily briefing:")
    print(assistant.daily_briefing())