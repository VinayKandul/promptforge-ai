"""Prompt Optimizer Module.

Enhances prompts using advanced techniques:
- Role prompting reinforcement
- Context expansion
- Task clarification
- Output structure definition
- Few-shot examples when useful
"""
from typing import Dict, List, Optional


# Few-shot example templates by category
FEW_SHOT_EXAMPLES: Dict[str, str] = {
    "coding": """
## Example of Expected Output Quality:

**User Request:** "Write a function to reverse a string"
**Expected Response:**
```python
def reverse_string(s: str) -> str:
    \"\"\"
    Reverse the input string.

    Args:
        s: The string to reverse

    Returns:
        The reversed string

    Examples:
        >>> reverse_string("hello")
        'olleh'
    \"\"\"
    return s[::-1]
```
The response should demonstrate similarly clean, documented code.""",

    "content_creation": """
## Example of Expected Output Quality:

The response should be well-structured with:
- An engaging introduction that hooks the reader
- Clear sections with descriptive headings
- Practical examples and actionable insights
- A compelling conclusion with takeaways""",

    "research": """
## Example of Expected Output Quality:

The response should follow this research structure:
- Executive summary of findings
- Methodology and approach
- Detailed analysis with evidence
- Key insights and patterns
- Recommendations and next steps""",

    "education": """
## Example of Expected Output Quality:

The response should follow a clear learning path:
- Start with what the student already knows
- Introduce new concepts gradually
- Use analogies and real-world examples
- Include practice problems or exercises
- Summarize key takeaways""",
}


def optimize_prompt(prompt_data: Dict, enable_few_shot: bool = True) -> Dict:
    """
    Optimize and enhance the structured prompt.

    Args:
        prompt_data: Output from prompt_architect.architect_prompt()
        enable_few_shot: Whether to include few-shot examples

    Returns:
        Enhanced prompt_data with optimized full_prompt
    """
    category = prompt_data.get("category", "content_creation")
    full_prompt = prompt_data.get("full_prompt", "")

    optimizations_applied = []

    # 1. Role prompting reinforcement
    full_prompt = _reinforce_role(full_prompt, prompt_data.get("role", ""))
    optimizations_applied.append("role_reinforcement")

    # 2. Add chain-of-thought for complex tasks
    if _is_complex_task(prompt_data):
        full_prompt = _add_chain_of_thought(full_prompt)
        optimizations_applied.append("chain_of_thought")

    # 3. Add few-shot examples
    if enable_few_shot and category in FEW_SHOT_EXAMPLES:
        full_prompt = _add_few_shot(full_prompt, category)
        optimizations_applied.append("few_shot_examples")

    # 4. Add quality assurance checklist
    full_prompt = _add_quality_checklist(full_prompt, category)
    optimizations_applied.append("quality_checklist")

    # 5. Add anti-hallucination instructions
    full_prompt = _add_accuracy_instructions(full_prompt)
    optimizations_applied.append("accuracy_instructions")

    # Update and return
    result = dict(prompt_data)
    result["full_prompt"] = full_prompt
    result["optimizations_applied"] = optimizations_applied

    return result


def _reinforce_role(prompt: str, role: str) -> str:
    """Reinforce the role assignment with stronger framing."""
    reinforcement = (
        f"\nIMPORTANT: You must maintain the perspective and expertise of a "
        f"{role} throughout your entire response. Draw upon deep domain "
        f"knowledge and professional experience."
    )
    return prompt + reinforcement


def _is_complex_task(prompt_data: Dict) -> bool:
    """Determine if the task is complex enough for chain-of-thought."""
    indicators = 0
    task = prompt_data.get("task", "")
    if len(task.split()) > 30:
        indicators += 1
    if prompt_data.get("audience") in ["advanced", "technical"]:
        indicators += 1
    if "comprehensive" in prompt_data.get("constraints", "").lower():
        indicators += 1
    category = prompt_data.get("category", "")
    if category in ["coding", "research", "analysis"]:
        indicators += 1
    return indicators >= 2


def _add_chain_of_thought(prompt: str) -> str:
    """Add chain-of-thought reasoning instruction."""
    cot = (
        "\n\n## REASONING APPROACH\n"
        "Think through this step-by-step:\n"
        "1. First, understand the core requirement\n"
        "2. Break down the problem into components\n"
        "3. Address each component systematically\n"
        "4. Synthesize your findings into a cohesive response\n"
        "5. Review for completeness and accuracy"
    )
    return prompt + cot


def _add_few_shot(prompt: str, category: str) -> str:
    """Add few-shot examples for the category."""
    example = FEW_SHOT_EXAMPLES.get(category, "")
    if example:
        return prompt + "\n" + example
    return prompt


def _add_quality_checklist(prompt: str, category: str) -> str:
    """Add a quality assurance checklist."""
    checklists = {
        "coding": (
            "\n\n## QUALITY CHECKLIST\n"
            "Before responding, verify:\n"
            "- [ ] Code is syntactically correct\n"
            "- [ ] Edge cases are handled\n"
            "- [ ] Code is well-documented\n"
            "- [ ] Best practices are followed"
        ),
        "content_creation": (
            "\n\n## QUALITY CHECKLIST\n"
            "Before responding, verify:\n"
            "- [ ] Content is engaging from the first sentence\n"
            "- [ ] All sections flow logically\n"
            "- [ ] No factual errors or unsupported claims\n"
            "- [ ] Conclusion provides clear value"
        ),
        "research": (
            "\n\n## QUALITY CHECKLIST\n"
            "Before responding, verify:\n"
            "- [ ] All claims are supported by evidence\n"
            "- [ ] Multiple perspectives are considered\n"
            "- [ ] Analysis is objective and unbiased\n"
            "- [ ] Recommendations are actionable"
        ),
    }

    default_checklist = (
        "\n\n## QUALITY CHECKLIST\n"
        "Before responding, verify:\n"
        "- [ ] Response fully addresses the request\n"
        "- [ ] Content is accurate and well-organized\n"
        "- [ ] Tone matches the target audience\n"
        "- [ ] No critical information is missing"
    )

    return prompt + checklists.get(category, default_checklist)


def _add_accuracy_instructions(prompt: str) -> str:
    """Add instructions to reduce hallucination."""
    instruction = (
        "\n\nIMPORTANT: If you're unsure about specific facts, data, or claims, "
        "clearly indicate the level of certainty. Do not fabricate statistics, "
        "quotes, or references. It's better to acknowledge limitations than to "
        "provide inaccurate information."
    )
    return prompt + instruction
