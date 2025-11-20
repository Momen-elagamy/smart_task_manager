import openai
from django.conf import settings
from tasks.models import Task
from projects.models import Project
from groq import Groq
from .utils import analyze_productivity


openai.api_key = settings.OPENAI_API_KEY
client = Groq(api_key=settings.GROQ_API_KEY)


def get_ai_response(prompt, user=None):
    system_prompt = "You are a helpful AI assistant for a task management app called 'Smart Task Manager'."

    if user:
        projects = Project.objects.filter(owner=user)
        productivity = analyze_productivity(user)

        context_lines = [
            "Here is the current context for the user:",
            f"- User: {user.email}",
            f"- Productivity: {productivity['productivity']}% ({productivity['completed_tasks']}/{productivity['total_tasks']} tasks completed).",
            "\nProjects and Tasks:"
        ]

        if projects.exists():
            for project in projects[:5]:  # Limit to 5 projects for brevity
                context_lines.append(f"  - Project '{project.name}':")
                tasks = Task.objects.filter(project=project).order_by('due_date')
                if tasks.exists():
                    for task in tasks[:5]: # Limit to 5 tasks per project
                        context_lines.append(f"    - Task: '{task.title}' (Status: {task.status}, Due: {task.due_date or 'N/A'})")
                else:
                    context_lines.append("    - No tasks in this project.")
        else:
            context_lines.append("  - The user has no projects yet.")

        system_prompt += "\n\n" + "\n".join(context_lines)

    completion = client.chat.completions.create(
        model=settings.GROQ_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    return completion.choices[0].message.content


def summarize_project(project):
    summary_prompt = f"""
    Please provide a short, motivational summary for the project '{project.name}'.
    Description: {project.description}
    """
    return get_ai_response(summary_prompt, user=project.owner)

def generate_task_from_prompt(user, prompt):
    response = get_ai_response(f"Generate a new task idea for: {prompt}")
    return {"suggested_task": response}
