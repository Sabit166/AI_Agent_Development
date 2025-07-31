# CareerMate: Multi-Agent Career Development Assistant

CareerMate is an AI-powered multi-agent system designed to help users plan and advance their careers. It leverages multiple specialized agents, each with a distinct role, to provide personalized recommendations for skill development, job opportunities, and learning resources.

---

## Agents Overview

### 1. **Skill Gap Agent**
**Function:**  
Identifies the gap between the user's current skills and the skills required for their preferred job roles.

**How it works:**  
- Analyzes the user's acquired skills and preferred job(s).
- Uses the `get_missing_skills` tool to determine which skills the user still needs to acquire.
- Returns a list of missing skills and a description of the skill gap.

---

### 2. **Job Finder Agent**
**Function:**  
Recommends job opportunities that match the user's skills and preferences.

**How it works:**  
- Uses the user's acquired skills and job preferences from the context.
- Calls the `find_jobs` tool to search for jobs where the user's skills are a good fit.
- Returns a list of job recommendations, including job title, company, location, description, and application link.

---

### 3. **Course Recommender Agent**
**Function:**  
Suggests relevant courses to help the user fill their skill gaps.

**How it works:**  
- Accesses the user's missing skills from the context.
- Uses the `recommend_courses` tool to find courses that teach the missing skills.
- Returns a list of recommended courses, including course title, platform, link, and description.

---

### 4. **Conversational Agent**
**Function:**  
Handles general career-related queries and provides conversational support.

**How it works:**  
- Engages in open-ended conversation with the user.
- Answers questions, provides advice, and helps with any career-related concerns not covered by the other agents.

---

### 5. **Career Mate (Main Agent)**
**Function:**  
Acts as the orchestrator, coordinating the specialized agents to deliver a comprehensive career planning experience.

**How it works:**  
- Receives user queries and context.
- Determines which specialized agent(s) to hand off the task to, based on the user's needs.
- Aggregates and formats the outputs from the sub-agents.
- Returns a structured response including skill gaps, job recommendations, course suggestions, and a summary message.

---

## How It Works

1. **User provides their skills and career preferences.**
2. **Career Mate** analyzes the request and delegates tasks to the appropriate agents.
3. **Skill Gap Agent** identifies missing skills.
4. **Job Finder Agent** suggests matching job opportunities.
5. **Course Recommender Agent** recommends courses to fill skill gaps.
6. **Conversational Agent** answers general questions.
7. **Career Mate** combines all results and presents a personalized career development plan.

---

## Example Output Structure

```json
{
  "skill_gaps": ["SQL", "Statistics", "Pandas"],
  "job_recommendations": [
    {
      "title": "Data Scientist",
      "company": "Google",
      "location": "Mountain View, CA",
      "description": "Build predictive models and analyze large datasets to generate business insights.",
      "link": "https://careers.google.com/jobs/results/123456789/"
    }
  ],
  "course_recommendations": [
    {
      "title": "SQL for Data Science",
      "platform": "Coursera",
      "link": "https://coursera.org/sql-for-data-science",
      "description": "Learn SQL basics for data analysis."
    }
  ],
  "message": "Based on your current skills and preferred job, here are your skill gaps, job opportunities, and recommended courses to help you advance your career!"
}
```

---

## Getting Started

1. Clone the repository.
2. Install dependencies from `requirements.txt`.
3. Set up your `.env` file with API keys and configuration.
4. Run the main script to interact with CareerMate.

---

**CareerMate** helps you take the next step in your career with AI-powered, personalized guidance!