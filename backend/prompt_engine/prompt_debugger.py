"""Prompt Debugger Module.

Analyzes existing prompts to provide scores,
identify missing components, and suggest improvements.
"""
from typing import Dict, List


# Components to check for
PROMPT_COMPONENTS = {
    "role_definition": {
        "keywords": ["you are", "act as", "role", "expert", "specialist", "assistant"],
        "weight": 15,
        "description": "Role definition - tells the AI who to act as",
    },
    "context": {
        "keywords": ["context", "background", "situation", "given that", "given the", "scenario"],
        "weight": 15,
        "description": "Context/background information",
    },
    "task_clarity": {
        "keywords": ["task", "create", "write", "generate", "analyze", "explain", "build", "develop"],
        "weight": 20,
        "description": "Clear task or action statement",
    },
    "constraints": {
        "keywords": ["constraint", "rule", "must", "should", "avoid", "don't", "do not", "limit", "maximum", "minimum"],
        "weight": 10,
        "description": "Constraints or rules to follow",
    },
    "output_format": {
        "keywords": ["format", "structure", "output", "response should", "markdown", "json", "list", "table", "bullet"],
        "weight": 15,
        "description": "Output format specification",
    },
    "tone_audience": {
        "keywords": ["tone", "audience", "style", "professional", "casual", "formal", "technical", "beginner"],
        "weight": 10,
        "description": "Tone or target audience specification",
    },
    "examples": {
        "keywords": ["example", "for instance", "such as", "e.g.", "like this", "sample"],
        "weight": 10,
        "description": "Examples or demonstrations (few-shot)",
    },
    "specificity": {
        "keywords": [],
        "weight": 5,
        "description": "Sufficient specificity and detail",
    },
}


def debug_prompt(prompt_text: str) -> Dict:
    """
    Analyze a prompt and provide debugging information.

    Returns:
        Dict with keys: score, components_found, components_missing,
                       suggestions, analysis, grade
    """
    text = prompt_text.lower().strip()
    word_count = len(prompt_text.split())

    components_found = []
    components_missing = []
    total_score = 0
    max_score = 0

    for comp_name, comp_info in PROMPT_COMPONENTS.items():
        max_score += comp_info["weight"]

        if comp_name == "specificity":
            # Special handling: score based on length and detail
            if word_count > 50:
                score = comp_info["weight"]
            elif word_count > 20:
                score = comp_info["weight"] * 0.6
            else:
                score = comp_info["weight"] * 0.2

            total_score += score
            if score >= comp_info["weight"] * 0.5:
                components_found.append({
                    "name": comp_name,
                    "description": comp_info["description"],
                    "score": round(score, 1),
                    "max_score": comp_info["weight"],
                })
            else:
                components_missing.append({
                    "name": comp_name,
                    "description": comp_info["description"],
                    "score": round(score, 1),
                    "max_score": comp_info["weight"],
                })
            continue

        # Keyword-based detection
        matches = [kw for kw in comp_info["keywords"] if kw in text]

        if matches:
            score = min(comp_info["weight"], comp_info["weight"] * (len(matches) / max(len(comp_info["keywords"]) * 0.3, 1)))
            total_score += score
            components_found.append({
                "name": comp_name,
                "description": comp_info["description"],
                "keywords_found": matches,
                "score": round(score, 1),
                "max_score": comp_info["weight"],
            })
        else:
            components_missing.append({
                "name": comp_name,
                "description": comp_info["description"],
                "score": 0,
                "max_score": comp_info["weight"],
            })

    # Calculate final score (0-100)
    final_score = round((total_score / max_score) * 100) if max_score > 0 else 0

    # Generate suggestions
    suggestions = _generate_suggestions(components_missing, word_count, text)

    # Assign grade
    grade = _assign_grade(final_score)

    return {
        "score": final_score,
        "grade": grade,
        "word_count": word_count,
        "components_found": components_found,
        "components_missing": components_missing,
        "suggestions": suggestions,
        "analysis": _generate_analysis(final_score, components_found, components_missing, word_count),
    }


def _generate_suggestions(missing: List[Dict], word_count: int, text: str) -> List[str]:
    """Generate improvement suggestions based on missing components."""
    suggestions = []

    missing_names = {m["name"] for m in missing}

    if "role_definition" in missing_names:
        suggestions.append(
            "Add a role definition: Start with 'You are a [role]' to give the AI "
            "a clear persona and expertise level."
        )

    if "context" in missing_names:
        suggestions.append(
            "Add context: Explain the background or situation to help the AI "
            "understand what you need and why."
        )

    if "task_clarity" in missing_names:
        suggestions.append(
            "Clarify the task: Explicitly state what action the AI should perform. "
            "Use clear verbs like 'create', 'analyze', 'explain', etc."
        )

    if "constraints" in missing_names:
        suggestions.append(
            "Add constraints: Specify rules like word limits, topics to avoid, "
            "or required elements to include."
        )

    if "output_format" in missing_names:
        suggestions.append(
            "Specify output format: Tell the AI how to structure the response "
            "(e.g., 'Use bullet points', 'Format as JSON', 'Include headers')."
        )

    if "tone_audience" in missing_names:
        suggestions.append(
            "Define tone and audience: Specify who will read the response and "
            "what tone to use (e.g., 'professional', 'casual', 'technical')."
        )

    if "examples" in missing_names:
        suggestions.append(
            "Consider adding examples: Few-shot examples help the AI understand "
            "exactly what quality and format you expect."
        )

    if word_count < 20:
        suggestions.append(
            "Your prompt is very short. Adding more detail typically leads to "
            "better results from AI models."
        )

    return suggestions


def _assign_grade(score: int) -> str:
    """Assign a letter grade based on score."""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B+"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C+"
    elif score >= 40:
        return "C"
    elif score >= 30:
        return "D"
    else:
        return "F"


def _generate_analysis(
    score: int, found: List[Dict], missing: List[Dict], word_count: int
) -> str:
    """Generate a human-readable analysis summary."""
    parts = [f"Prompt Score: {score}/100"]

    if score >= 80:
        parts.append("This is a well-structured prompt with most key components present.")
    elif score >= 60:
        parts.append("This prompt has a good foundation but could be improved with additional components.")
    elif score >= 40:
        parts.append("This prompt is functional but missing several important components for optimal results.")
    else:
        parts.append("This prompt needs significant improvement. Adding structure will greatly enhance AI output quality.")

    parts.append(f"\nComponents present: {len(found)}/{len(found) + len(missing)}")
    parts.append(f"Word count: {word_count}")

    if missing:
        parts.append(f"\nMissing components: {', '.join(m['name'].replace('_', ' ').title() for m in missing)}")

    return "\n".join(parts)
