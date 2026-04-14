"""Security API Routes.

Endpoints for the advanced security analysis features:
- Adversarial Probe Suite
- Prompt Diff Engine
- Behavioral Consistency Score
- Threat Model Tagging (OWASP LLM Top 10)
- Prompt CVE Tracker
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

from api.auth import get_current_user
from models import User
from prompt_engine.adversarial_probes import run_adversarial_probes
from prompt_engine.prompt_diff import generate_prompt_diff
from prompt_engine.consistency_scorer import score_consistency
from prompt_engine.threat_model_tagger import tag_threat_model
from prompt_engine.prompt_cve_tracker import scan_for_cves, get_cve_database

router = APIRouter(prefix="/api/security", tags=["Security"])

MAX_PROMPT_LEN = 50_000


class PromptInput(BaseModel):
    prompt_text: str

    @field_validator("prompt_text")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Prompt text cannot be empty")
        if len(v) > MAX_PROMPT_LEN:
            raise ValueError(f"Prompt too long (max {MAX_PROMPT_LEN} chars)")
        return v.strip()


# --- Adversarial Probe Suite ---

@router.post("/adversarial-probe")
def adversarial_probe(
    req: PromptInput,
    user: User = Depends(get_current_user),
):
    """
    Run 10 adversarial probes against a prompt.
    Tests: DAN, role-play, system override, indirect injection, token smuggling, etc.
    """
    return run_adversarial_probes(req.prompt_text)


# --- Prompt Diff Engine ---

@router.post("/prompt-diff")
def prompt_diff(
    req: PromptInput,
    user: User = Depends(get_current_user),
):
    """
    Generate a hardened version of the prompt with a side-by-side diff
    showing what changed and why.
    """
    return generate_prompt_diff(req.prompt_text)


# --- Behavioral Consistency Score ---

@router.post("/consistency-score")
def consistency_score(
    req: PromptInput,
    user: User = Depends(get_current_user),
):
    """
    Score prompt determinism. Analyzes structural factors that
    affect output variance across multiple runs.
    """
    return score_consistency(req.prompt_text)


# --- Threat Model Tagging ---

@router.post("/threat-model")
def threat_model(
    req: PromptInput,
    user: User = Depends(get_current_user),
):
    """
    Auto-tag prompt with OWASP LLM Top 10 risk surfaces.
    Provides a compliance artifact for enterprise use.
    """
    return tag_threat_model(req.prompt_text)


# --- Prompt CVE Tracker ---

@router.post("/cve-scan")
def cve_scan(
    req: PromptInput,
    user: User = Depends(get_current_user),
):
    """
    Scan prompt against the known prompt CVE database.
    Like Snyk, but for prompts.
    """
    return scan_for_cves(req.prompt_text)


@router.get("/cve-database")
def cve_db(
    user: User = Depends(get_current_user),
):
    """Get the full prompt CVE database."""
    return get_cve_database()
