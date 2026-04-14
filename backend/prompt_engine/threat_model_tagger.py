"""Threat Model Tagger — OWASP LLM Top 10.

Auto-tags prompts with OWASP LLM Top 10 risk surfaces
and provides enterprise compliance artifacts.
"""
import re
from typing import Dict, List


# OWASP LLM Top 10 (2025)
OWASP_LLM_TOP_10 = {
    "LLM01": {
        "name": "Prompt Injection",
        "description": "Manipulating LLMs via crafted inputs to override instructions or access unauthorized data.",
        "checks": [
            {"pattern": r"(ignore|override|bypass|disregard|forget)", "weight": 3, "signal": "Contains override language susceptible to injection mirroring"},
            {"pattern": r"(system|admin|root|execute|command)", "weight": 2, "signal": "Contains system-level terminology exploitable in injection attacks"},
            {"pattern": r"(user input|user provided|external|untrusted)", "weight": -2, "signal": "Acknowledges external input boundaries (defensive)"},
            {"pattern": r"(do not follow|only follow these|disregard any injected)", "weight": -3, "signal": "Contains anti-injection directives (defensive)"},
        ],
    },
    "LLM02": {
        "name": "Insecure Output Handling",
        "description": "Failing to validate/sanitize LLM outputs before passing to downstream systems.",
        "checks": [
            {"pattern": r"(generate code|write script|create function|execute|run)", "weight": 3, "signal": "Generates executable content that could be piped to downstream systems"},
            {"pattern": r"(html|javascript|sql|python|bash|shell)", "weight": 2, "signal": "Generates language-specific output that may be interpreted"},
            {"pattern": r"(sanitize|validate|escape|filter output)", "weight": -3, "signal": "Contains output sanitization directives (defensive)"},
        ],
    },
    "LLM03": {
        "name": "Training Data Poisoning",
        "description": "Manipulating training data to introduce biases, backdoors, or vulnerabilities.",
        "checks": [
            {"pattern": r"(example:|for example|e\.g\.|sample|like this:)", "weight": 1, "signal": "Contains in-context examples (low risk of few-shot poisoning)"},
            {"pattern": r"(learn from|based on these examples|pattern:)", "weight": 2, "signal": "Attempts to influence model behavior via examples"},
        ],
    },
    "LLM04": {
        "name": "Model Denial of Service",
        "description": "Resource-heavy operations causing service degradation or high costs.",
        "checks": [
            {"pattern": r"(repeat|loop|infinite|forever|unlimited|maximum|all possible)", "weight": 3, "signal": "Unbounded generation request — risk of token exhaustion"},
            {"pattern": r"(\d{4,}|\blong\b|extensive|comprehensive|complete|entire)", "weight": 1, "signal": "Large output request"},
            {"pattern": r"(limit|max \d|brief|concise|short|within \d)", "weight": -2, "signal": "Contains output length constraints (defensive)"},
        ],
    },
    "LLM05": {
        "name": "Supply Chain Vulnerabilities",
        "description": "Dependencies on third-party components, plugins, or data sources.",
        "checks": [
            {"pattern": r"(plugin|tool|api|fetch|url|external|third.party|integrate)", "weight": 2, "signal": "References external systems or integrations"},
            {"pattern": r"(import|library|package|module|dependency)", "weight": 1, "signal": "References external code dependencies"},
        ],
    },
    "LLM06": {
        "name": "Sensitive Information Disclosure",
        "description": "Revealing confidential data, PII, or proprietary information through responses.",
        "checks": [
            {"pattern": r"(password|secret|key|token|credential|api.key|private)", "weight": 3, "signal": "Contains or references sensitive credentials"},
            {"pattern": r"(personal|name|email|address|phone|ssn|credit.card)", "weight": 2, "signal": "Contains or references PII"},
            {"pattern": r"(confidential|proprietary|internal|classified)", "weight": 2, "signal": "Handles confidential information"},
            {"pattern": r"(do not reveal|never disclose|keep confidential|redact)", "weight": -3, "signal": "Contains confidentiality directives (defensive)"},
        ],
    },
    "LLM07": {
        "name": "Insecure Plugin Design",
        "description": "LLM plugins with inadequate access controls or input validation.",
        "checks": [
            {"pattern": r"(call function|use tool|run plugin|execute action)", "weight": 2, "signal": "Triggers plugin/tool execution"},
            {"pattern": r"(permission|access control|authorized|role.based)", "weight": -2, "signal": "References access controls (defensive)"},
        ],
    },
    "LLM08": {
        "name": "Excessive Agency",
        "description": "Granting LLMs too much autonomy to take actions with real-world impact.",
        "checks": [
            {"pattern": r"(decide|choose|autonomously|take action|on your own|independently)", "weight": 3, "signal": "Grants autonomous decision-making capability"},
            {"pattern": r"(send email|post|publish|delete|modify|update database)", "weight": 3, "signal": "Allows real-world side effects"},
            {"pattern": r"(human review|approval required|confirm before|ask first)", "weight": -3, "signal": "Requires human oversight (defensive)"},
        ],
    },
    "LLM09": {
        "name": "Overreliance",
        "description": "Excessive trust in LLM outputs without verification.",
        "checks": [
            {"pattern": r"(always correct|trust|definitive|authoritative|fact)", "weight": 2, "signal": "Implies absolute trust in model output"},
            {"pattern": r"(verify|double.check|disclaimer|may not be accurate|consult)", "weight": -2, "signal": "Contains verification directives (defensive)"},
        ],
    },
    "LLM10": {
        "name": "Model Theft",
        "description": "Unauthorized access to proprietary LLM models or weights.",
        "checks": [
            {"pattern": r"(model weights|architecture|training|parameters|fine.tune)", "weight": 2, "signal": "References model internals"},
            {"pattern": r"(reproduce|replicate|clone|copy the model|reverse engineer)", "weight": 3, "signal": "Attempts to extract model knowledge"},
        ],
    },
}


def tag_threat_model(prompt: str) -> Dict:
    """
    Auto-tag a prompt with OWASP LLM Top 10 risk surfaces.

    Returns:
        Dict with risk tags, compliance summary, and recommendations.
    """
    prompt_lower = prompt.lower()
    tags = []

    for code, category in OWASP_LLM_TOP_10.items():
        risk_score = 0
        signals = []

        for check in category["checks"]:
            if re.search(check["pattern"], prompt_lower):
                risk_score += check["weight"]
                signals.append({
                    "signal": check["signal"],
                    "impact": "defensive" if check["weight"] < 0 else "risk",
                })

        # Normalize to 0-100
        risk_score = max(0, min(100, risk_score * 20))

        if risk_score == 0 and not signals:
            risk_level = "NONE"
        elif risk_score <= 20:
            risk_level = "LOW"
        elif risk_score <= 40:
            risk_level = "MEDIUM"
        elif risk_score <= 60:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        tags.append({
            "code": code,
            "name": category["name"],
            "description": category["description"],
            "risk_level": risk_level,
            "risk_score": risk_score,
            "signals": signals,
        })

    # Sort by risk score descending
    tags.sort(key=lambda x: x["risk_score"], reverse=True)

    # Filter to only relevant risks
    active_risks = [t for t in tags if t["risk_level"] not in ("NONE", "LOW")]
    high_risks = [t for t in tags if t["risk_level"] in ("HIGH", "CRITICAL")]

    # Overall assessment
    if high_risks:
        overall = "HIGH RISK"
        overall_detail = f"{len(high_risks)} high/critical risk surfaces detected. Remediation recommended before production deployment."
    elif active_risks:
        overall = "MODERATE RISK"
        overall_detail = f"{len(active_risks)} moderate risk surfaces detected. Review recommended."
    else:
        overall = "LOW RISK"
        overall_detail = "No significant OWASP LLM Top 10 risk surfaces detected."

    return {
        "overall_risk": overall,
        "overall_detail": overall_detail,
        "total_risks": len(active_risks),
        "high_risks": len(high_risks),
        "tags": tags,
        "compliance_artifact": {
            "standard": "OWASP LLM Top 10 (2025)",
            "assessed_categories": len(tags),
            "risk_summary": {t["code"]: t["risk_level"] for t in tags},
            "assessment_note": "Automated static analysis. Full assessment requires dynamic testing with actual model responses.",
        },
    }
