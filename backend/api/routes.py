"""API Routes.

Main API endpoints for prompt generation, debugging, history, library,
workflows, and user API key management.
"""
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from api.auth import get_current_user
from database import get_db
from models import User, PromptHistory, PromptLibrary, Workflow, UserAPIKey
from prompt_engine.intent_analyzer import analyze_intent
from prompt_engine.context_builder import build_context
from prompt_engine.prompt_architect import architect_prompt
from prompt_engine.prompt_optimizer import optimize_prompt
from prompt_engine.prompt_debugger import debug_prompt
from prompt_engine.security_scanner import scan_prompt
from model_adapters.adapter_factory import get_adapter, get_available_models
from workflow_engine.engine import execute_workflow
from encryption import encrypt_value, decrypt_value, mask_key

router = APIRouter(prefix="/api", tags=["Prompts"])

# --- Input length limits ---
MAX_REQUEST_LEN = 10_000
MAX_PROMPT_LEN = 50_000


# --- Helper: fetch decrypted API keys for a user ---

def _get_user_api_keys(user: User, db: Session) -> Dict[str, str]:
    """Return a dict mapping provider → decrypted API key for the user."""
    rows = db.query(UserAPIKey).filter(UserAPIKey.user_id == user.id).all()
    keys: Dict[str, str] = {}
    for row in rows:
        try:
            keys[row.provider] = decrypt_value(row.encrypted_key)
        except Exception:
            pass  # corrupted key → skip, user can re-add
    return keys


# --- Request/Response Models ---

class GenerateRequest(BaseModel):
    user_request: str
    provider: str = "openai"
    model_name: Optional[str] = None
    custom_role: Optional[str] = None
    custom_tone: Optional[str] = None
    execute: bool = True

    @field_validator("user_request")
    @classmethod
    def validate_request(cls, v: str) -> str:
        if len(v) > MAX_REQUEST_LEN:
            raise ValueError(f"Request too long (max {MAX_REQUEST_LEN} chars)")
        return v


class GenerateResponse(BaseModel):
    user_request: str
    intent: dict
    context: dict
    generated_prompt: str
    optimizations: list
    security_scan: dict
    ai_response: Optional[str] = None
    model_used: str
    history_id: Optional[str] = None


class DebugRequest(BaseModel):
    prompt_text: str

    @field_validator("prompt_text")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if len(v) > MAX_PROMPT_LEN:
            raise ValueError(f"Prompt too long (max {MAX_PROMPT_LEN} chars)")
        return v


class LibraryCreateRequest(BaseModel):
    title: str
    category: str
    prompt_text: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class LibraryUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    prompt_text: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class WorkflowCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[dict]


class WorkflowRunRequest(BaseModel):
    workflow_id: str
    provider: str = "openai"
    model_name: Optional[str] = None


# --- API Key management models ---

class APIKeyCreateRequest(BaseModel):
    provider: str
    api_key: str
    label: Optional[str] = None

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        valid = {"openai", "claude", "gemini", "mistral", "deepseek", "ollama"}
        if v.lower().strip() not in valid:
            raise ValueError(f"Invalid provider. Must be one of: {', '.join(valid)}")
        return v.lower().strip()

    @field_validator("api_key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not v or len(v.strip()) < 8:
            raise ValueError("API key is too short")
        if len(v) > 500:
            raise ValueError("API key is too long")
        return v.strip()


class APIKeyResponse(BaseModel):
    id: str
    provider: str
    label: Optional[str]
    masked_key: str
    created_at: str
    updated_at: str


# --- Health Check ---

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "PromptForge AI", "version": "1.0.0"}


# --- Models ---

@router.get("/models")
def list_models(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get available AI models and their configuration status for the current user."""
    user_keys = _get_user_api_keys(user, db)
    return get_available_models(user_keys)


# --- API Key Management ---

@router.get("/settings/api-keys")
def list_api_keys(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all configured API keys for the user (masked)."""
    rows = (
        db.query(UserAPIKey)
        .filter(UserAPIKey.user_id == user.id)
        .order_by(UserAPIKey.provider)
        .all()
    )
    items = []
    for row in rows:
        try:
            decrypted = decrypt_value(row.encrypted_key)
            masked = mask_key(decrypted)
        except Exception:
            masked = "•••• (corrupted)"

        items.append(APIKeyResponse(
            id=row.id,
            provider=row.provider,
            label=row.label,
            masked_key=masked,
            created_at=row.created_at.isoformat() if row.created_at else "",
            updated_at=row.updated_at.isoformat() if row.updated_at else "",
        ))

    return {"items": items, "total": len(items)}


@router.post("/settings/api-keys")
def add_or_update_api_key(
    req: APIKeyCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add or update an API key for a provider. Replaces existing key for that provider."""
    # Check if user already has a key for this provider
    existing = (
        db.query(UserAPIKey)
        .filter(UserAPIKey.user_id == user.id, UserAPIKey.provider == req.provider)
        .first()
    )

    encrypted = encrypt_value(req.api_key)

    if existing:
        existing.encrypted_key = encrypted
        existing.label = req.label or existing.label
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "id": existing.id, "provider": req.provider}
    else:
        key_record = UserAPIKey(
            user_id=user.id,
            provider=req.provider,
            encrypted_key=encrypted,
            label=req.label,
        )
        db.add(key_record)
        db.commit()
        db.refresh(key_record)
        return {"status": "created", "id": key_record.id, "provider": req.provider}


@router.delete("/settings/api-keys/{key_id}")
def delete_api_key(
    key_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a user's API key."""
    key_record = (
        db.query(UserAPIKey)
        .filter(UserAPIKey.id == key_id, UserAPIKey.user_id == user.id)
        .first()
    )
    if not key_record:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(key_record)
    db.commit()
    return {"status": "deleted", "id": key_id}


# --- Prompt Generation ---

@router.post("/generate", response_model=GenerateResponse)
async def generate_prompt(
    req: GenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Full execution pipeline: Input → Intent → Context → Architect → Optimize → Execute."""
    if not req.user_request.strip():
        raise HTTPException(status_code=400, detail="User request cannot be empty")

    # Step 1: Analyze intent
    intent_data = analyze_intent(req.user_request)

    # Step 2: Build context
    context_data = build_context(req.user_request, intent_data)

    # Step 3: Architect the prompt
    prompt_data = architect_prompt(
        req.user_request, intent_data, context_data,
        custom_role=req.custom_role, custom_tone=req.custom_tone,
    )

    # Step 4: Optimize
    optimized = optimize_prompt(prompt_data)

    # Step 5: Security scan
    security_result = scan_prompt(optimized["full_prompt"])

    # Step 6: Execute (if requested and safe)
    ai_response = None
    model_used = f"{req.provider}/{req.model_name or 'default'}"

    if req.execute:
        user_keys = _get_user_api_keys(user, db)
        adapter = get_adapter(req.provider, req.model_name, user_api_keys=user_keys)
        model_used = f"{req.provider}/{adapter.model_name}"
        result = await adapter.generate(optimized["full_prompt"])
        if result["success"]:
            ai_response = result["response"]
        else:
            ai_response = f"Error: {result['error']}"

    # Step 7: Save to history
    history = PromptHistory(
        user_id=user.id,
        user_request=req.user_request,
        intent_category=intent_data["category"],
        generated_prompt=optimized["full_prompt"],
        model_used=model_used,
        ai_response=ai_response,
        security_warnings=security_result.get("warnings", []),
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    return GenerateResponse(
        user_request=req.user_request,
        intent=intent_data,
        context=context_data,
        generated_prompt=optimized["full_prompt"],
        optimizations=optimized.get("optimizations_applied", []),
        security_scan=security_result,
        ai_response=ai_response,
        model_used=model_used,
        history_id=history.id,
    )


# --- Prompt Debugger ---

@router.post("/debug")
def debug_existing_prompt(
    req: DebugRequest,
    user: User = Depends(get_current_user),
):
    """Analyze an existing prompt and provide improvement suggestions."""
    if not req.prompt_text.strip():
        raise HTTPException(status_code=400, detail="Prompt text cannot be empty")

    return debug_prompt(req.prompt_text)


# --- Prompt History ---

@router.get("/history")
def get_history(
    skip: int = 0,
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get prompt history for the current user."""
    if limit > 100:
        limit = 100

    items = (
        db.query(PromptHistory)
        .filter(PromptHistory.user_id == user.id)
        .order_by(PromptHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(PromptHistory).filter(PromptHistory.user_id == user.id).count()

    return {
        "items": [
            {
                "id": item.id,
                "user_request": item.user_request,
                "intent_category": item.intent_category,
                "generated_prompt": item.generated_prompt,
                "model_used": item.model_used,
                "ai_response": item.ai_response,
                "security_warnings": item.security_warnings,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in items
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.delete("/history/{history_id}")
def delete_history_item(
    history_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a prompt history item."""
    item = (
        db.query(PromptHistory)
        .filter(PromptHistory.id == history_id, PromptHistory.user_id == user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="History item not found")

    db.delete(item)
    db.commit()
    return {"status": "deleted", "id": history_id}


# --- Prompt Library ---

@router.get("/library")
def get_library(
    category: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get saved prompts from the library."""
    query = db.query(PromptLibrary).filter(PromptLibrary.user_id == user.id)
    if category:
        query = query.filter(PromptLibrary.category == category)

    items = query.order_by(PromptLibrary.updated_at.desc()).all()
    return {
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "prompt_text": item.prompt_text,
                "description": item.description,
                "tags": item.tags,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in items
        ],
        "total": len(items),
    }


@router.post("/library")
def create_library_item(
    req: LibraryCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a prompt to the library."""
    item = PromptLibrary(
        user_id=user.id,
        title=req.title,
        category=req.category,
        prompt_text=req.prompt_text,
        description=req.description,
        tags=req.tags,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {
        "id": item.id,
        "title": item.title,
        "category": item.category,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


@router.put("/library/{item_id}")
def update_library_item(
    item_id: str,
    req: LibraryUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a library item."""
    item = (
        db.query(PromptLibrary)
        .filter(PromptLibrary.id == item_id, PromptLibrary.user_id == user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Library item not found")

    for field, value in req.model_dump(exclude_none=True).items():
        setattr(item, field, value)

    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return {"status": "updated", "id": item.id}


@router.delete("/library/{item_id}")
def delete_library_item(
    item_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a library item."""
    item = (
        db.query(PromptLibrary)
        .filter(PromptLibrary.id == item_id, PromptLibrary.user_id == user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Library item not found")

    db.delete(item)
    db.commit()
    return {"status": "deleted", "id": item_id}


# --- Workflows ---

@router.get("/workflows")
def get_workflows(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's workflows."""
    items = (
        db.query(Workflow)
        .filter(Workflow.user_id == user.id)
        .order_by(Workflow.updated_at.desc())
        .all()
    )
    return {
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "steps": item.steps,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in items
        ],
        "total": len(items),
    }


@router.post("/workflows")
def create_workflow(
    req: WorkflowCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new workflow."""
    workflow = Workflow(
        user_id=user.id,
        name=req.name,
        description=req.description,
        steps=req.steps,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return {
        "id": workflow.id,
        "name": workflow.name,
        "steps_count": len(workflow.steps),
    }


@router.post("/workflows/run")
async def run_workflow(
    req: WorkflowRunRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Execute a workflow."""
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == req.workflow_id, Workflow.user_id == user.id)
        .first()
    )
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    user_keys = _get_user_api_keys(user, db)

    result = await execute_workflow(
        steps=workflow.steps,
        provider=req.provider,
        model_name=req.model_name,
        user_api_keys=user_keys,
    )

    return result


@router.delete("/workflows/{workflow_id}")
def delete_workflow(
    workflow_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a workflow."""
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id, Workflow.user_id == user.id)
        .first()
    )
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    db.delete(workflow)
    db.commit()
    return {"status": "deleted", "id": workflow_id}
