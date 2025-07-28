import os
import json
import asyncio
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled, Runner   

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


class SkillGap(BaseModel):
    skills: List[str] = Field(description="List of skills the user wants to improve")

class JobRecommender(BaseModel):

class CourseRecommender(BaseModel):
    
class CareerMateAgent(Agent):
    
class UserProfile(BaseModel):
    name: str
    skills: List[str]  = Field(description="List of user skills")
    experience_years: Optional[int] = None
    education: Optional[str] = None

