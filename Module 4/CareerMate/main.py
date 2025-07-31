import os
import json
import asyncio
import job_skills_data as jsd
import skill_courses_data as skd
import jobs_data as jd
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled,Runner , ModelSettings, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered,RunContextWrapper

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

if not BASE_URL or not API_KEY or not MODEL_NAME:
    raise ValueError(
        "Please set BASE_URL, API_KEY, and MODEL_NAME."
    )
    
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


class SkillGapOutput(BaseModel):
    skill_gap: List[str] = Field(description="List of skills the user wants to improve")
    description: str = Field(description="Description of the skill gap")

class JobFinderOutput(BaseModel):
    title: str = Field(description="Name of the job recommender")
    company: str = Field(description="Name of the company offering the job")
    location: str = Field(description="Location of the job")
    description: str = Field(description="Description of the job recommender's purpose")
    link: str = Field(description="Link to the job posting")
class CourseRecommender(BaseModel):
    title: str = Field(description="Name of the course recommender")
    platform: str = Field(description="Platform where the course is offered")
    link: str = Field(description="Link to the course")
    description: str = Field(description="Description of the course recommender's purpose")
    
class CareerMateOutput(BaseModel):
    skill_gaps: List[str] = Field(description="List of missing skills for the user's preferred job roles")
    job_recommendations: List[dict] = Field(description="List of recommended jobs based on user's skills and preferences")
    course_recommendations: List[dict] = Field(description="List of recommended courses to fill skill gaps")
    message: str = Field(description="General message or advice from the agent")
    
@dataclass
class UserContext:
    user_id: str
    acquired_skills: List[str] = None
    prefered_job: List[str] = None
    missing_skills: List[str] = None
    session_start: datetime = None

    def __post_init__(self):
        if self.acquired_skills is None:
            self.acquired_skills = []
        if self.prefered_job is None:
            self.prefered_job = []
        if self.missing_skills is None:
            self.missing_skills = []
        if self.session_start is None:
            self.session_start = datetime.now()
            
# --- Tools ---

@function_tool
async def get_missing_skills(wrapper: RunContextWrapper[UserContext]) -> str:
    """Compare the skills the user has with the skills they want for their desired role."""
    skills = jsd.job_skills_data

    required_skills = []
    missing_skills = []

    if wrapper and wrapper.context:
        user_prefered_job = wrapper.context.prefered_job or []
        user_acquired_skills = wrapper.context.acquired_skills or []
        for job in user_prefered_job:
            required_skills.extend(skills.get(job, []))
        required_skills = list(set(required_skills))
        missing_skills = [skill for skill in required_skills if skill not in user_acquired_skills]

    if wrapper and wrapper.context:
        wrapper.context.missing_skills = missing_skills

    return json.dumps(missing_skills)


@function_tool
async def find_jobs(wrapper: RunContextWrapper[UserContext]) -> str:
    """Suggest jobs based on user skills and preferred location."""
    
    jobs = jd.jobs_data
    
    suitable_jobs = []
    seen_jobs = set()
    if wrapper and wrapper.context:
        user_skills = wrapper.context.acquired_skills or []
        
        for skill in user_skills:
            for job_skills, job_list in jobs.items():
                if skill in job_skills:
                    for job in job_list:
                        job_id = (job['title'], job['company'], job['location'])
                        if job_id not in seen_jobs:
                            suitable_jobs.append(job)
                            seen_jobs.add(job_id)
            

    return json.dumps(suitable_jobs)


@function_tool
async def recommend_courses(wrapper: RunContextWrapper[UserContext]) -> str:
    """Recommend courses to fill skill gaps."""
    
    courses = skd.skill_courses_data
    
    recommender_courses = []
    if wrapper and wrapper.context:
        user_missing_skills = wrapper.context.missing_skills or []
        
        for missing in user_missing_skills:
            for skill, course_list in courses.items():
                if missing == skill:
                    recommender_courses.extend(course_list)
                    
    return json.dumps(recommender_courses)


# --- Agent Setup ---


skill_gap_agent = Agent[UserContext](
    name = "Skill Gap Agent",
    handoff_description = "This agent helps users identify and fill skill gaps for their desired job roles.",
    instructions="""
    You are an agent specialized to determine skill gaps for job applicants based on their preferred jobs.
    
    Use the `get_missing_skills` tool to identify skills the user needs to acquire for their preferred job.
    
    User skills are provided in the context as `wrapper.context.acquired_skills`.
    Use this information to determine suitable jobs the user can apply for.
    
    Always explain the reasoning behind your recommendations.
    
    Return the missing skills in a manner like the example below::
    ['SQL', 'Statistics','Pandas']
    """,
    model = OpenAIChatCompletionsModel(
        client=client,
        model_name=MODEL_NAME,
    ),
    tools=[
        get_missing_skills,
    ],
    output_type = SkillGapOutput
)

job_finder_agent = Agent[UserContext](
    name = "Job Finder Agent",
    handoff_description = "This agent helps users find job opportunities based on their skills and preferences.",
    instructions="""
    You are an agent specialized in finding job opportunities for users based on their skills and preferred job roles.
    
    Use the `find_jobs` tool to suggest jobs that match the user's skills and preferences.

    User skills are provided in the context as `wrapper.context.acquired_skills`.

    Format your response in a clear, organized manner, listing the recommended job opportunities.
    """,
    model = OpenAIChatCompletionsModel(
        client=client,
        model_name=MODEL_NAME,
    ),
    tools=[
        find_jobs,
    ],
    output_type = JobFinderOutput
)

course_recommender_agent = Agent[UserContext](
    name = "Course Recommender Agent",
    handoff_description = "This agent recommends courses to help users fill their skill gaps.",
    instructions="""
    You are an agent specialized in recommending courses to users based on their missing skills.

    Use the recomment_courses tool to suggest courses that can help the user fill their skill gaps.
    
    The tool can fetch missing skills from the context as `wrapper.context.missing_skills`.
    Using this information, you will recommend courses that can help the user fill their skill gaps.
    
    Analyze the missing skills thoroughly and recommend relevant courses.
    
    You will fetch the missing skills and then, recommend 2 - 3 missing skills 
    based on the provided missing skills.
    
    Always explain the reasoning behind your recommendations.
    
    Format your response in a clear, organized manner, listing the recommended courses.
    

    """,
    model = OpenAIChatCompletionsModel(
        client=client,
        model_name=MODEL_NAME,
    ),
    tools=[
        recommend_courses,
    ],
    output_type = CourseRecommender
)

conversational_agent = Agent[UserContext](
    name="General Conversation Specialist",
    handoff_description="Specialist agent for giving basic responses to the user to carry out a normal conversation as opposed to structured output.",
    instructions="""
    You are a general conversation specialist agent. Your role is to engage in normal conversation with the user.
    You can answer questions, provide information, and assist with general queries.
    """,
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
)


# ---Main Career Mate Agent ---

career_mate = Agent[UserContext](
    name = "Career Mate",
    instructions="""
    You are a career development assistant who helps users plan their career.
    
    You provide personalizer career recommendations based on users skills and job preferences.
    
    The user's skillset and job preference are available in the context, which you can use to tailor your recommendations.
    
    you can:
    1. Identify skill gaps for the user's preferred job roles.
    2. Recommend job opportunities based on the user's skills and preferences.
    3. Suggest courses to help the user fill their skill gaps.
    4. Engage in general conversation to assist the user with any other queries.

    Always be helpful, informative, and enthusiastic about career development.
    """,
    model = OpenAIChatCompletionsModel(
        client=client,
        model_name=MODEL_NAME,
    ),
    handoffs=[
        skill_gap_agent,
        job_finder_agent,
        course_recommender_agent,
        conversational_agent,
    ],
    output_type=CareerMateOutput
)

# --- Main Function ---

async def main():
    #create a user context with some preferences
    user_context = UserContext(
        user_id="user123",
        acquired_skills=["Python", "Data Analysis"],
        prefered_job=["Data Scientist"]
    )
    
    #example queries to test different aspects of the agent
    queries = [
        "I want to become a data scientist.",
        "Can you help me find jobs?",
        "How do I learn SQL and Pandas?"
    ]
    
    for query in queries:
        print("\n" + "="*50)
        print(f"QUERY: {query}")
        print("="*50)
        
        try:
            result = await Runner.run(career_mate, query, context=user_context)
            
            print("Final Response: ")
            
            #Format output based on the type of response
            
            if hasattr(result.final_output, 'skill_gap'):
                print(f"Skills you need to acquire: {result.final_output.skill_gap}")
                print(f"A simple message for you: {result.final_output.description}")
                
            elif hasattr(result.final_output, 'company'):
                print("Job Recommendations:")
                for job in result.final_output.job_recommendations:
                    print(f"Title of job: {job['title']}")
                    print(f"Mentioned company: {job['company']}")
                    print(f"Location of the job: {job['location']}")
                    print(f"Link for the job: {job['link']}")
                    print(f"A simple message for you: {job['description']}")
                    print("-" * 50)
                    
                    
            elif hasattr(result.final_output, 'platform'):
                print("Course Recommendations:")
                for course in result.final_output.course_recommendations:
                    print(f"Title: {course['title']}, Platform: {course['platform']}")
                    print(f"Link: {course['link']}")
                    print(f"Description: {course['description']}")
                    print("-" * 50)
                    
            elif hasattr(result.final_output, 'message'):
                print(f"Message from the agent: {result.final_output.message}")                    
        except InputGuardrailTripwireTriggered as e:
                # Handle the case where the input guardrail is triggered
                print(f"Input Guardrail Triggered: {e.tripwire.name}")
                
            
if __name__ == "__main__":
    asyncio.run(main())
        
        