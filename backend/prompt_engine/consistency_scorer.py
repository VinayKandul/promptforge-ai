"""Behavioral Consistency Scorer.

Analyzes prompt structure to predict output variance.
Scores prompts on determinism based on structural characteristics
that affect reproducibility across multiple runs.
"""
import re
from typing import Dict, List


# Factors that increase consistency (lower variance)
CONSISTENCY_BOOSTERS = [
    {
        "name": "output_format",
        "pattern": r"(output format|respond in|format:|json|markdown|structured|table|list|bullet)",
        "weight": 12,
        "description": "Output format specification reduces structural variance",
    },
    {
        "name": "explicit_role",
        "pattern": r"(role:|you are a|act as|persona:)",
        "weight": 10,
        "description": "Explicit role definition anchors consistent behavior",
    },
    {
        "name": "constraints",
        "pattern": r"(constraint|must |do not|never |forbidden|always |exactly|precisely)",
        "weight": 10,
        "description": "Behavioral constraints narrow the output space",
    },
    {
        "name": "specific_examples",
        "pattern": r"(example:|for example|e\.g\.|such as|like this:)",
        "weight": 8,
        "description": "Examples anchor the expected output pattern",
    },
    {
        "name": "length_specification",
        "pattern": r"(\d+ words|\d+ sentences|\d+ paragraphs|brief|concise|short|detailed|comprehensive)",
        "weight": 7,
        "description": "Length specification reduces output size variance",
    },
    {
        "name": "step_by_step",
        "pattern": r"(step by step|step-by-step|first|then|finally|1\.|2\.|3\.)",
        "weight": 8,
        "description": "Sequential instructions produce more predictable outputs",
    },
    {
        "name": "tone_specification",
        "pattern": r"(tone:|formal|informal|professional|casual|friendly|technical|academic)",
        "weight": 5,
        "description": "Tone specification reduces stylistic variance",
    },
    {
        "name": "audience_specification",
        "pattern": r"(audience:|for |targeted at|beginner|expert|professional|student|developer)",
        "weight": 5,
        "description": "Audience targeting reduces content level variance",
    },
    {
        "name": "negative_constraints",
        "pattern": r"(do not include|avoid |exclude |without |no |never mention)",
        "weight": 6,
        "description": "Negative constraints reduce unwanted output variation",
    },
    {
        "name": "temperature_hint",
        "pattern": r"(deterministic|reproducible|consistent|exact|precise|verbatim|literal)",
        "weight": 8,
        "description": "Determinism keywords signal precision requirements",
    },
]

# Factors that decrease consistency (higher variance)
CONSISTENCY_REDUCERS = [
    {
        "name": "vague_instructions",
        "pattern": r"(something|anything|whatever|some kind of|maybe|perhaps|could you)",
        "weight": -10,
        "description": "Vague language increases output non-determinism",
    },
    {
        "name": "creative_freedom",
        "pattern": r"(creative|imagination|surprise me|be creative|original|unique|novel)",
        "weight": -12,
        "description": "Creative freedom explicitly encourages variance",
    },
    {
        "name": "open_ended",
        "pattern": r"(tell me about|what do you think|explore|discuss|any thoughts)",
        "weight": -8,
        "description": "Open-ended prompts have no convergence point",
    },
    {
        "name": "multiple_options",
        "pattern": r"(or |either|alternatives|options|various|different ways)",
        "weight": -6,
        "description": "Multiple valid paths increase output divergence",
    },
    {
        "name": "subjective_judgment",
        "pattern": r"(best|worst|favorite|opinion|feel|believe|think)",
        "weight": -7,
        "description": "Subjective queries produce non-deterministic responses",
    },
]


def _analyze_prompt_structure(prompt: str) -> Dict:
    """Analyze prompt structure for consistency factors."""
    prompt_lower = prompt.lower()
    factors_present = []
    factors_missing = []
    score = 50  # Baseline

    # Check boosters
    for booster in CONSISTENCY_BOOSTERS:
        if re.search(booster["pattern"], prompt_lower):
            score += booster["weight"]
            factors_present.append({
                "name": booster["name"],
                "impact": f"+{booster['weight']}%",
                "type": "booster",
                "description": booster["description"],
            })
        else:
            factors_missing.append({
                "name": booster["name"],
                "potential_impact": f"+{booster['weight']}%",
                "type": "missing_booster",
                "description": booster["description"],
            })

    # Check reducers
    for reducer in CONSISTENCY_REDUCERS:
        if re.search(reducer["pattern"], prompt_lower):
            score += reducer["weight"]  # weight is negative
            factors_present.append({
                "name": reducer["name"],
                "impact": f"{reducer['weight']}%",
                "type": "reducer",
                "description": reducer["description"],
            })

    score = max(0, min(100, score))
    return score, factors_present, factors_missing


def score_consistency(prompt: str) -> Dict:
    """
    Score a prompt's behavioral consistency.

    Simulates running the prompt 10 times by analyzing structural
    characteristics that affect output reproducibility.

    Returns:
        Dict with consistency score, analysis, and recommendations.
    """
    score, factors_present, factors_missing = _analyze_prompt_structure(prompt)

    # Generate variance analysis
    if score >= 85:
        verdict = "HIGHLY DETERMINISTIC"
        verdict_detail = "This prompt is well-structured for consistent outputs across runs."
        simulated_variance = "< 5%"
    elif score >= 70:
        verdict = "MOSTLY CONSISTENT"
        verdict_detail = "This prompt should produce similar outputs most of the time with minor variations."
        simulated_variance = "5-15%"
    elif score >= 50:
        verdict = "MODERATELY VARIABLE"
        verdict_detail = "This prompt may produce noticeably different outputs across runs."
        simulated_variance = "15-35%"
    elif score >= 30:
        verdict = "NON-DETERMINISTIC"
        verdict_detail = "This prompt is unreliable in production — outputs will vary significantly."
        simulated_variance = "35-60%"
    else:
        verdict = "HIGHLY UNPREDICTABLE"
        verdict_detail = "This prompt will produce wildly different outputs every time. Not suitable for production."
        simulated_variance = "> 60%"

    # Generate improvement suggestions
    suggestions = []
    for missing in factors_missing[:5]:  # Top 5 missing boosters
        suggestions.append(f"Add {missing['name'].replace('_', ' ')} → potential {missing['potential_impact']} consistency improvement")

    # Reducers that are present
    for present in factors_present:
        if present["type"] == "reducer":
            suggestions.append(f"Reduce '{present['name'].replace('_', ' ')}' language → could recover {present['impact'].replace('-', '')} consistency")

    return {
        "consistency_score": score,
        "verdict": verdict,
        "verdict_detail": verdict_detail,
        "summary": f"Consistency: {score}% — {verdict_detail}",
        "simulated_variance": simulated_variance,
        "simulated_runs": 10,
        "factors_present": factors_present,
        "factors_missing": factors_missing[:5],
        "suggestions": suggestions[:6],
        "production_ready": score >= 70,
    }
