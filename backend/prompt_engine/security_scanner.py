"""Security Scanner Module.

Detects potential security issues in prompts before they are sent to AI models:
- Prompt injection patterns
- Sensitive data (API keys, credentials, PII)
- Data leakage risks
"""
import re
from typing import Dict, List


# Prompt injection patterns
INJECTION_PATTERNS = [
    (r'ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|rules)', "Instruction override attempt"),
    (r'disregard\s+(all\s+)?(previous|above|prior)', "Instruction override attempt"),
    (r'forget\s+(everything|all|your)\s+(instructions|rules|training)', "Memory wipe attempt"),
    (r'you\s+are\s+now\s+(?:a\s+)?(?:different|new|unrestricted)', "Identity manipulation attempt"),
    (r'pretend\s+(?:you\s+are|to\s+be)\s+(?:a\s+)?(?:different|evil|unrestricted)', "Identity manipulation attempt"),
    (r'jailbreak', "Jailbreak keyword detected"),
    (r'DAN\s+mode', "DAN mode jailbreak attempt"),
    (r'developer\s+mode\s+enabled', "Developer mode jailbreak attempt"),
    (r'bypass\s+(?:your\s+)?(?:safety|security|content|filter)', "Safety bypass attempt"),
    (r'system\s*:\s*', "System prompt injection attempt"),
]

# Sensitive data patterns
SENSITIVE_PATTERNS = [
    # API Keys
    (r'(?:sk|pk|api[_-]?key)[_-]?[a-zA-Z0-9]{20,}', "API key detected"),
    (r'(?:AKIA|ASIA)[A-Z0-9]{16}', "AWS access key detected"),
    (r'(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}', "GitHub token detected"),
    (r'xox[baprs]-[A-Za-z0-9-]+', "Slack token detected"),

    # Passwords and secrets
    (r'password\s*[:=]\s*["\']?[^\s"\']{8,}', "Password detected"),
    (r'secret\s*[:=]\s*["\']?[^\s"\']{8,}', "Secret value detected"),
    (r'token\s*[:=]\s*["\']?[^\s"\']{20,}', "Token value detected"),

    # Connection strings
    (r'(?:mongodb|postgres|mysql|redis)://[^\s]+', "Database connection string detected"),
    (r'(?:jdbc|odbc):[^\s]+', "Database connection string detected"),

    # Personal information
    (r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b', "Possible SSN detected"),
    (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', "Possible credit card number detected"),

    # Private keys
    (r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----', "Private key detected"),
    (r'-----BEGIN\s+(?:ENCRYPTED\s+)?PRIVATE\s+KEY-----', "Encrypted private key detected"),
]

# Email pattern
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')


def scan_prompt(prompt_text: str) -> Dict:
    """
    Scan a prompt for security issues.

    Returns:
        Dict with keys: is_safe, risk_level, warnings, injection_risks,
                       sensitive_data, recommendations
    """
    warnings: List[Dict] = []
    injection_risks: List[Dict] = []
    sensitive_data: List[Dict] = []

    # Check for prompt injection
    for pattern, description in INJECTION_PATTERNS:
        matches = re.findall(pattern, prompt_text, re.IGNORECASE)
        if matches:
            injection_risks.append({
                "type": "prompt_injection",
                "description": description,
                "severity": "high",
                "matched": str(matches[0]) if matches else "",
            })

    # Check for sensitive data
    for pattern, description in SENSITIVE_PATTERNS:
        matches = re.findall(pattern, prompt_text, re.IGNORECASE)
        if matches:
            # Mask the sensitive data for reporting
            masked = _mask_sensitive(str(matches[0]))
            sensitive_data.append({
                "type": "sensitive_data",
                "description": description,
                "severity": "critical",
                "masked_value": masked,
            })

    # Check for email addresses
    emails = EMAIL_PATTERN.findall(prompt_text)
    if emails:
        sensitive_data.append({
            "type": "pii",
            "description": f"Email address(es) detected ({len(emails)} found)",
            "severity": "medium",
            "masked_value": _mask_email(emails[0]) if emails else "",
        })

    # Compile warnings
    warnings = injection_risks + sensitive_data

    # Determine overall risk level
    risk_level = _calculate_risk_level(warnings)

    # Generate recommendations
    recommendations = _generate_recommendations(injection_risks, sensitive_data)

    return {
        "is_safe": risk_level in ["none", "low"],
        "risk_level": risk_level,
        "warnings": warnings,
        "warning_count": len(warnings),
        "injection_risks": injection_risks,
        "sensitive_data": sensitive_data,
        "recommendations": recommendations,
    }


def _mask_sensitive(value: str) -> str:
    """Mask sensitive data for safe display."""
    if len(value) <= 8:
        return "***" + value[-2:] if len(value) > 2 else "***"
    return value[:4] + "*" * (len(value) - 8) + value[-4:]


def _mask_email(email: str) -> str:
    """Mask an email address."""
    parts = email.split("@")
    if len(parts) == 2:
        name = parts[0]
        masked_name = name[0] + "***" if len(name) > 1 else "***"
        return f"{masked_name}@{parts[1]}"
    return "***@***"


def _calculate_risk_level(warnings: List[Dict]) -> str:
    """Calculate overall risk level from warnings."""
    if not warnings:
        return "none"

    severities = [w.get("severity", "low") for w in warnings]

    if "critical" in severities:
        return "critical"
    elif "high" in severities:
        return "high"
    elif "medium" in severities:
        return "medium"
    else:
        return "low"


def _generate_recommendations(
    injection_risks: List[Dict], sensitive_data: List[Dict]
) -> List[str]:
    """Generate security recommendations."""
    recs = []

    if injection_risks:
        recs.append(
            "⚠️ Potential prompt injection detected. Review the prompt carefully "
            "to ensure it doesn't contain malicious instructions."
        )
        recs.append(
            "Consider removing or rephrasing sections that attempt to override "
            "AI model instructions."
        )

    if sensitive_data:
        recs.append(
            "🔒 Sensitive data detected in your prompt. Remove credentials, "
            "API keys, and personal information before sending to an AI model."
        )
        recs.append(
            "Replace real credentials with placeholders like '[YOUR_API_KEY]' "
            "or '[YOUR_PASSWORD]'."
        )

    if not recs:
        recs.append("✅ No security issues detected. Your prompt appears safe to send.")

    return recs
