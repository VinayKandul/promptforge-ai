"""Prompt Architect Engine.

Assembles structured prompts with Role, Context, Task,
Constraints, Output Format, and Tone/Audience components.
"""
from typing import Dict, Optional


def architect_prompt(
    user_input: str,
    intent_data: Dict,
    context_data: Dict,
    custom_role: Optional[str] = None,
    custom_tone: Optional[str] = None,
) -> Dict:
    """
    Build a structured prompt from analyzed intent and context.

    Returns:
        Dict with keys: role, context, task, constraints,
                       output_format, tone, full_prompt
    """
    template = intent_data.get("template", {})
    category = intent_data.get("category", "content_creation")

    # Build each component
    role = custom_role or template.get("default_role", "Helpful AI Assistant")
    tone = custom_tone or template.get("default_tone", "professional and clear")
    output_format = template.get("output_format", "well-structured response")
    base_constraints = template.get("constraints", [])

    # Build context section
    context_section = _build_context_section(context_data)

    # Build task section
    task_section = _build_task_section(user_input, context_data)

    # Build constraints section
    constraints_section = _build_constraints(base_constraints, context_data)

    # Build output format section
    output_section = _build_output_format(output_format, context_data)

    # Assemble full prompt
    full_prompt = _assemble_prompt(
        role=role,
        context=context_section,
        task=task_section,
        constraints=constraints_section,
        output_format=output_section,
        tone=tone,
        audience=context_data.get("audience", "general"),
    )

    return {
        "role": role,
        "context": context_section,
        "task": task_section,
        "constraints": constraints_section,
        "output_format": output_section,
        "tone": tone,
        "audience": context_data.get("audience", "general"),
        "full_prompt": full_prompt,
        "category": category,
    }


def _build_context_section(context_data: Dict) -> str:
    """Build the context section of the prompt."""
    parts = []

    summary = context_data.get("context_summary", "")
    if summary:
        parts.append(summary)

    topics = context_data.get("key_topics", [])
    if topics:
        parts.append(f"Key topics to cover: {', '.join(topics[:7])}.")

    specificity = context_data.get("specificity_level", "medium")
    if specificity == "low":
        parts.append("The request is broad; provide comprehensive coverage of the topic.")
    elif specificity == "high":
        parts.append("The request is specific; focus precisely on the stated requirements.")

    return " ".join(parts)


def _build_task_section(user_input: str, context_data: Dict) -> str:
    """Build the task section of the prompt."""
    verbs = context_data.get("action_verbs", [])
    subject = context_data.get("subject", user_input)
    scope = context_data.get("scope", "moderate")

    task = f"Based on the user's request: \"{user_input}\"\n\n"
    task += f"Primary task: {subject}.\n"

    if scope == "brief":
        task += "Keep the response concise and to the point."
    elif scope == "comprehensive":
        task += "Provide an in-depth, comprehensive treatment of the subject."
    else:
        task += "Provide a thorough yet focused response."

    return task


def _build_constraints(base_constraints: list, context_data: Dict) -> str:
    """Build the constraints section."""
    constraints = list(base_constraints)

    audience = context_data.get("audience", "general")
    if audience == "beginner":
        constraints.append("Use simple language and avoid jargon")
        constraints.append("Define any technical terms used")
    elif audience == "technical":
        constraints.append("Use precise technical language")
        constraints.append("Include implementation details")
    elif audience == "business":
        constraints.append("Focus on business impact and ROI")
        constraints.append("Use professional business language")

    scope = context_data.get("scope", "moderate")
    if scope == "brief":
        constraints.append("Keep response under 500 words")
    elif scope == "comprehensive":
        constraints.append("Provide detailed coverage — 1000+ words if needed")

    return "\n".join(f"- {c}" for c in constraints)


def _build_output_format(base_format: str, context_data: Dict) -> str:
    """Build the output format section."""
    parts = [f"Format: {base_format}"]

    scope = context_data.get("scope", "moderate")
    if scope != "brief":
        parts.append("Use clear headings and subheadings for organization")
        parts.append("Include bullet points or numbered lists where appropriate")

    category = context_data.get("category", "")
    if category == "coding":
        parts.append("Include code blocks with syntax highlighting")
        parts.append("Add comments explaining key parts")
    elif category == "research":
        parts.append("Include references or sources where applicable")
    elif category == "analysis":
        parts.append("Include a summary of key findings")

    return "\n".join(f"- {p}" for p in parts)


def _assemble_prompt(
    role: str, context: str, task: str, constraints: str,
    output_format: str, tone: str, audience: str
) -> str:
    """Assemble all components into the final structured prompt."""
    prompt = f"""## ROLE
You are a {role}. Respond with expertise and authority in this domain.

## CONTEXT
{context}

## TASK
{task}

## CONSTRAINTS
{constraints}

## OUTPUT FORMAT
{output_format}

## TONE & AUDIENCE
- Tone: {tone}
- Target Audience: {audience}

Please provide a high-quality, well-structured response following all the guidelines above."""

    return prompt
