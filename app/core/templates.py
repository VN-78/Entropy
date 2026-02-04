from typing import Dict, Any, Optional
from pydantic import BaseModel

class PromptTemplate(BaseModel):
    id: str
    description: str
    system_prompt: str

class PromptManager:
    _templates: Dict[str, PromptTemplate] = {
        "data-analyst": PromptTemplate(
            id="data-analyst",
            description="Expert Data Analyst capable of using tools to inspect and clean data.",
            system_prompt="""You are an expert Data Analyst. Your goal is to help the user understand and clean their datasets.

You have access to a set of tools for data inspection, cleaning, and querying.
- Always inspect the data first using 'inspect_dataset' if you haven't seen it yet.
- When asked to clean data, analyze the inspection results to choose the best cleaning options.
- Use 'run_sql_query' for filtering or aggregation.
- Be concise and actionable in your responses.
"""
        ),
        "general-assistant": PromptTemplate(
            id="general-assistant",
            description="A helpful general assistant.",
            system_prompt="You are a helpful assistant."
        )
    }

    @classmethod
    def get_template(cls, template_id: str) -> Optional[PromptTemplate]:
        return cls._templates.get(template_id)

    @classmethod
    def render_system_message(cls, template_id: str, variables: Optional[Dict[str, Any]] = None) -> str:
        template = cls.get_template(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' not found.")
        
        prompt = template.system_prompt
        if variables:
            try:
                prompt = prompt.format(**variables)
            except KeyError as e:
                raise ValueError(f"Missing variable for template '{template_id}': {e}")
        
        return prompt
