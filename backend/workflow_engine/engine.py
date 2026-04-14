"""Workflow Engine.

Executes multi-step AI workflows where each step's output
feeds into the next step's context.
"""
from typing import Dict, List, Optional
from prompt_engine.intent_analyzer import analyze_intent
from prompt_engine.context_builder import build_context
from prompt_engine.prompt_architect import architect_prompt
from prompt_engine.prompt_optimizer import optimize_prompt
from model_adapters.adapter_factory import get_adapter


async def execute_workflow(
    steps: List[Dict],
    provider: str,
    model_name: Optional[str] = None,
    user_api_keys: Optional[Dict[str, str]] = None,
) -> Dict:
    """
    Execute a multi-step workflow.

    Each step has:
        - name: Step label
        - instruction: What this step should do
        - use_previous_output: bool, whether to include previous step's output

    Returns:
        Dict with keys: steps_completed, results, success, total_steps
    """
    adapter = get_adapter(provider, model_name, user_api_keys=user_api_keys)
    results = []
    previous_output = ""

    for i, step in enumerate(steps):
        step_name = step.get("name", f"Step {i + 1}")
        instruction = step.get("instruction", "")
        use_prev = step.get("use_previous_output", True)

        # Build context including previous output
        full_input = instruction
        if use_prev and previous_output and i > 0:
            full_input = (
                f"Previous step output:\n---\n{previous_output}\n---\n\n"
                f"Current task: {instruction}"
            )

        # Run through the prompt pipeline
        intent_data = analyze_intent(full_input)
        context_data = build_context(full_input, intent_data)
        prompt_data = architect_prompt(full_input, intent_data, context_data)
        optimized = optimize_prompt(prompt_data)

        # Execute against the model
        response = await adapter.generate(optimized["full_prompt"])

        step_result = {
            "step_number": i + 1,
            "step_name": step_name,
            "instruction": instruction,
            "generated_prompt_preview": optimized["full_prompt"][:200] + "...",
            "response": response.get("response", ""),
            "success": response.get("success", False),
            "error": response.get("error"),
        }

        results.append(step_result)

        if response.get("success"):
            previous_output = response.get("response", "")
        else:
            # Stop workflow on error
            return {
                "steps_completed": i + 1,
                "total_steps": len(steps),
                "results": results,
                "success": False,
                "error": f"Workflow stopped at step {i + 1}: {response.get('error', 'Unknown error')}",
            }

    return {
        "steps_completed": len(steps),
        "total_steps": len(steps),
        "results": results,
        "success": True,
        "error": None,
    }
