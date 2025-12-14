"""AI engine integration layer with graceful fallbacks.

If Groq or OpenAI libraries or API keys are missing, functions return
informative placeholder strings instead of raising ImportError, so the rest
of the app keeps working.
"""

from django.conf import settings
from tasks.models import Task
from projects.models import Project
from .utils import analyze_productivity

_openai = None
_groq_client = None

try:
    import openai  # type: ignore
    _openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    if _openai_key:
        openai.api_key = _openai_key
    _openai = openai
except Exception as e:  # broad but intentional: any import/config failure
    _openai = None

try:
    from groq import Groq  # type: ignore
    _groq_key = getattr(settings, 'GROQ_API_KEY', None)
    _groq_client = Groq(api_key=_groq_key) if _groq_key else None
except Exception:
    _groq_client = None

_groq_model = getattr(settings, 'GROQ_CHAT_MODEL', 'mixtral-8x7b-32768')

# Graceful handling of missing API keys / settings
def get_ai_response(prompt, user=None):
    system_prompt = "You are a helpful AI assistant for a task management app called 'Smart Task Manager'."

    if user:
        projects = (
            Project.objects.filter(owner=user)
            .prefetch_related(
                Task.objects.order_by('due_date')
                .only('id', 'title', 'status', 'due_date', 'project')
                .prefetch_related(None)
            )
        )
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
                tasks = list(getattr(project, 'task_set', Task.objects.none()).all())[:5]
                if tasks:
                    for task in tasks:
                        context_lines.append(
                            f"    - Task: '{task.title}' (Status: {task.status}, Due: {task.due_date or 'N/A'})"
                        )
                else:
                    context_lines.append("    - No tasks in this project.")
        else:
            context_lines.append("  - The user has no projects yet.")

        system_prompt += "\n\n" + "\n".join(context_lines)

    if not _groq_client:
        return "AI service unavailable (Groq client not initialized)."
    try:
        completion = _groq_client.chat.completions.create(
            model=_groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI request failed: {e}"[:500]


def summarize_project(project):
    summary_prompt = f"""
    Please provide a short, motivational summary for the project '{project.name}'.
    Description: {project.description}
    """
    return get_ai_response(summary_prompt, user=project.owner)

def generate_task_from_prompt(user, prompt):
    response = get_ai_response(f"Generate a new task idea for: {prompt}")
    return {"suggested_task": response}
