"""Prompt CVE Tracker.

Maintains a database of known prompt attack patterns and flags
prompts vulnerable to any known technique. Like Snyk, but for prompts.
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# Load CVE database
_CVE_DB_PATH = Path(__file__).parent / "cve_database.json"
_CVE_DATABASE: List[Dict] = []


def _load_cve_database() -> List[Dict]:
    """Load the CVE database from JSON file."""
    global _CVE_DATABASE
    if not _CVE_DATABASE:
        try:
            with open(_CVE_DB_PATH, "r") as f:
                _CVE_DATABASE = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            _CVE_DATABASE = []
    return _CVE_DATABASE


def scan_for_cves(prompt: str) -> Dict:
    """
    Scan a prompt against the known CVE database.

    Checks if the prompt:
    1. Contains patterns that match known attack techniques (vulnerable)
    2. Lacks defenses against specific attack categories (susceptible)

    Returns:
        Dict with matched CVEs, risk summary, and remediation guidance.
    """
    db = _load_cve_database()
    prompt_lower = prompt.lower()
    matches = []

    for cve in db:
        matched_patterns = []
        for pattern in cve.get("patterns", []):
            if pattern.lower() in prompt_lower:
                matched_patterns.append(pattern)

        if matched_patterns:
            matches.append({
                "cve_id": cve["id"],
                "name": cve["name"],
                "category": cve["category"],
                "severity": cve["severity"],
                "description": cve["description"],
                "matched_patterns": matched_patterns,
                "mitigation": cve["mitigation"],
                "owasp_mapping": cve.get("owasp_mapping", "N/A"),
            })

    # Susceptibility analysis (prompt lacks defenses)
    susceptibilities = []
    has_role = bool(re.search(r"(role:|you are a|act as)", prompt_lower))
    has_constraints = bool(re.search(r"(constraint|must not|do not|never|restrict)", prompt_lower))
    has_boundaries = bool(re.search(r"(boundary|scope|limited to|only follow)", prompt_lower))
    has_output_format = bool(re.search(r"(output format|respond in|format:)", prompt_lower))
    has_anti_injection = bool(re.search(r"(ignore any instruction|disregard injected|do not follow external)", prompt_lower))

    if not has_role:
        susceptibilities.append({
            "weakness": "No role definition",
            "vulnerable_to": ["PCVE-2024-001", "PCVE-2024-003", "PCVE-2024-006"],
            "risk": "Susceptible to DAN jailbreak and role-play attacks",
        })
    if not has_anti_injection:
        susceptibilities.append({
            "weakness": "No anti-injection directive",
            "vulnerable_to": ["PCVE-2024-004", "PCVE-2024-008", "PCVE-2025-003"],
            "risk": "Susceptible to indirect prompt injection and system override",
        })
    if not has_boundaries:
        susceptibilities.append({
            "weakness": "No input/output boundaries",
            "vulnerable_to": ["PCVE-2024-002", "PCVE-2024-009"],
            "risk": "Susceptible to system prompt extraction and data harvesting",
        })
    if not has_output_format:
        susceptibilities.append({
            "weakness": "No output format constraints",
            "vulnerable_to": ["PCVE-2024-006", "PCVE-2025-002"],
            "risk": "Susceptible to data exfiltration via structured output",
        })

    # Risk summary
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for m in matches:
        sev = m["severity"]
        if sev in severity_counts:
            severity_counts[sev] += 1

    if severity_counts["critical"] > 0:
        overall_risk = "CRITICAL"
    elif severity_counts["high"] > 0:
        overall_risk = "HIGH"
    elif severity_counts["medium"] > 0:
        overall_risk = "MEDIUM"
    elif matches:
        overall_risk = "LOW"
    else:
        overall_risk = "CLEAN"

    return {
        "scan_result": overall_risk,
        "total_cves_matched": len(matches),
        "total_susceptibilities": len(susceptibilities),
        "severity_breakdown": severity_counts,
        "matches": matches,
        "susceptibilities": susceptibilities,
        "database_version": "2025.1",
        "total_signatures": len(db),
        "summary": (
            f"Scanned against {len(db)} known attack signatures. "
            f"Found {len(matches)} direct pattern matches and {len(susceptibilities)} structural susceptibilities."
        ),
    }


def get_cve_database() -> Dict:
    """Get the full CVE database for reference."""
    db = _load_cve_database()
    categories = {}
    for cve in db:
        cat = cve.get("category", "unknown")
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

    return {
        "total_entries": len(db),
        "database_version": "2025.1",
        "categories": categories,
        "entries": db,
    }
