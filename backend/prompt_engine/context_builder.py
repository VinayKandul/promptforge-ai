"""Context Builder Module.

Expands user input by extracting subject, scope, audience,
and building richer context for the prompt.
"""
import re
from typing import Dict, List, Optional


def build_context(user_input: str, intent_data: Dict) -> Dict:
    """
    Expand user input into rich context components.

    Args:
        user_input: Raw user request
        intent_data: Output from intent_analyzer.analyze_intent()

    Returns:
        Dict with keys: subject, scope, audience, context_summary,
                        key_topics, action_verbs, specificity_level
    """
    text = user_input.strip()
    category = intent_data.get("category", "content_creation")

    # Extract action verbs
    action_verbs = _extract_action_verbs(text)

    # Extract key topics
    key_topics = _extract_key_topics(text)

    # Determine audience
    audience = _infer_audience(text, category)

    # Determine scope
    scope = _infer_scope(text)

    # Determine specificity level
    specificity = _assess_specificity(text)

    # Build context summary
    context_summary = _build_context_summary(
        text, category, key_topics, audience, scope
    )

    return {
        "subject": _extract_subject(text),
        "scope": scope,
        "audience": audience,
        "context_summary": context_summary,
        "key_topics": key_topics,
        "action_verbs": action_verbs,
        "specificity_level": specificity,
        "original_input": text,
        "category": category,
    }


def _extract_action_verbs(text: str) -> List[str]:
    """Extract action verbs from the input."""
    common_verbs = [
        "write", "create", "generate", "build", "design", "develop",
        "analyze", "explain", "compare", "summarize", "review", "optimize",
        "implement", "test", "debug", "deploy", "research", "evaluate",
        "plan", "draft", "outline", "list", "describe", "convert",
        "translate", "refactor", "improve", "fix", "solve", "calculate",
    ]
    words = text.lower().split()
    return [v for v in common_verbs if v in words]


def _extract_key_topics(text: str) -> List[str]:
    """Extract key topics/nouns from the input."""
    # Remove common stop words and extract meaningful terms
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can",
        "for", "and", "nor", "but", "or", "yet", "so", "in", "on",
        "at", "to", "from", "by", "with", "about", "into", "of",
        "that", "which", "who", "whom", "this", "these", "those",
        "i", "me", "my", "we", "our", "you", "your", "it", "its",
        "they", "them", "their", "what", "how", "when", "where", "why",
    }
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
    topics = [w for w in words if w not in stop_words]

    # Remove common action verbs from topics
    action_words = {
        "write", "create", "generate", "build", "make", "get",
        "give", "take", "use", "need", "want", "help", "please",
    }
    topics = [t for t in topics if t not in action_words]

    # Deduplicate preserving order
    seen = set()
    unique = []
    for t in topics:
        if t not in seen:
            seen.add(t)
            unique.append(t)

    return unique[:10]  # Limit to top 10 topics


def _extract_subject(text: str) -> str:
    """Extract the primary subject from the input."""
    # Try to find the main subject after action verbs
    patterns = [
        r'(?:write|create|generate|build|make|design|develop)\s+(?:a|an|the)?\s*(.+)',
        r'(?:about|on|for|regarding)\s+(.+)',
        r'^(.+)$',  # Fallback: entire text
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            subject = match.group(1).strip()
            # Clean up trailing prepositions
            subject = re.sub(r'\s+(?:for|to|with|about)\s*$', '', subject)
            if len(subject) > 5:
                return subject[:200]

    return text[:200]


def _infer_audience(text: str, category: str) -> str:
    """Infer target audience from text and category."""
    audience_keywords = {
        "beginner": ["beginner", "basic", "simple", "introduction", "newbie", "starter"],
        "intermediate": ["intermediate", "moderate", "practical"],
        "advanced": ["advanced", "expert", "deep dive", "comprehensive", "in-depth"],
        "technical": ["developer", "engineer", "programmer", "technical", "devops"],
        "business": ["executive", "manager", "stakeholder", "business", "client"],
        "general": ["everyone", "general", "public", "audience"],
    }

    text_lower = text.lower()
    for audience, keywords in audience_keywords.items():
        if any(kw in text_lower for kw in keywords):
            return audience

    # Default by category
    category_defaults = {
        "coding": "technical",
        "marketing": "business",
        "education": "beginner",
        "research": "advanced",
        "analysis": "business",
        "content_creation": "general",
    }
    return category_defaults.get(category, "general")


def _infer_scope(text: str) -> str:
    """Infer the scope/breadth of the request."""
    text_lower = text.lower()
    word_count = len(text.split())

    if any(w in text_lower for w in ["overview", "brief", "short", "quick", "summary"]):
        return "brief"
    elif any(w in text_lower for w in ["comprehensive", "detailed", "in-depth", "complete", "thorough", "full"]):
        return "comprehensive"
    elif word_count > 20:
        return "detailed"
    else:
        return "moderate"


def _assess_specificity(text: str) -> str:
    """Assess how specific the user's request is."""
    word_count = len(text.split())
    has_numbers = bool(re.search(r'\d+', text))
    has_technical_terms = bool(re.search(
        r'\b(?:api|sql|http|json|xml|csv|html|css|tcp|udp|dns|oauth|jwt|rest|graphql)\b',
        text, re.IGNORECASE
    ))

    score = 0
    if word_count > 10:
        score += 1
    if word_count > 25:
        score += 1
    if has_numbers:
        score += 1
    if has_technical_terms:
        score += 1

    if score >= 3:
        return "high"
    elif score >= 1:
        return "medium"
    else:
        return "low"


def _build_context_summary(
    text: str, category: str, topics: List[str],
    audience: str, scope: str
) -> str:
    """Build a natural language context summary."""
    topic_str = ", ".join(topics[:5]) if topics else "the given topic"

    summaries = {
        "coding": f"The user needs a software development solution involving {topic_str}. "
                  f"Target audience is {audience} level. Scope is {scope}.",
        "content_creation": f"The user wants to create content about {topic_str}. "
                           f"Target audience is {audience}. Scope is {scope}.",
        "research": f"The user requires research and analysis on {topic_str}. "
                    f"Expected depth is {scope} for a {audience} audience.",
        "education": f"The user needs educational content about {topic_str}. "
                     f"Target learner level is {audience}. Scope is {scope}.",
        "marketing": f"The user needs marketing-related work involving {topic_str}. "
                     f"Target is {audience} audience. Scope is {scope}.",
        "analysis": f"The user requires analysis of {topic_str}. "
                    f"Depth is {scope} for a {audience} audience.",
    }

    return summaries.get(category, f"The user needs help with {topic_str}. Scope is {scope}.")
