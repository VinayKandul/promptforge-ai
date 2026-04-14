"""Intent Analyzer Module.

Classifies user input into categories and extracts metadata
to drive prompt template selection.
"""
import re
from typing import Dict, List, Tuple


# Category keywords mapping
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "coding": [
        "code", "program", "script", "function", "class", "debug", "fix",
        "algorithm", "api", "database", "sql", "python", "javascript",
        "typescript", "java", "c++", "rust", "go", "html", "css", "react",
        "vue", "angular", "node", "django", "flask", "fastapi", "docker",
        "kubernetes", "deploy", "test", "unit test", "refactor", "optimize",
        "port scan", "nmap", "exploit", "payload", "shell", "terminal",
        "compile", "build", "library", "framework", "backend", "frontend",
        "fullstack", "web app", "mobile app", "cli", "regex", "parse",
    ],
    "content_creation": [
        "blog", "article", "post", "write", "essay", "story", "creative",
        "copywriting", "headline", "caption", "description", "content",
        "newsletter", "email", "letter", "press release", "announcement",
        "book", "chapter", "poem", "lyrics", "speech", "presentation",
        "whitepaper", "case study", "review", "testimonial",
    ],
    "research": [
        "research", "analyze", "compare", "investigate", "study",
        "literature review", "survey", "data", "statistics", "findings",
        "methodology", "hypothesis", "experiment", "evidence", "source",
        "reference", "cite", "journal", "paper", "thesis", "dissertation",
    ],
    "education": [
        "explain", "teach", "lesson", "course", "tutorial", "guide",
        "how to", "step by step", "learn", "understand", "concept",
        "definition", "example", "exercise", "quiz", "exam", "curriculum",
        "syllabus", "lecture", "training", "workshop", "bootcamp",
    ],
    "marketing": [
        "marketing", "seo", "social media", "campaign", "brand",
        "advertisement", "ad copy", "landing page", "conversion",
        "funnel", "audience", "target", "strategy", "growth", "engagement",
        "influencer", "promotion", "launch", "product", "sales",
        "pitch", "slogan", "tagline", "value proposition",
    ],
    "analysis": [
        "analyze", "evaluate", "assess", "audit", "review", "report",
        "summary", "summarize", "breakdown", "insight", "trend",
        "forecast", "predict", "benchmark", "metric", "kpi", "dashboard",
        "visualization", "chart", "graph", "swot", "competitive",
        "risk", "threat", "vulnerability", "security", "compliance",
    ],
}

# Category-specific metadata templates
CATEGORY_TEMPLATES: Dict[str, Dict] = {
    "coding": {
        "default_role": "Senior Software Engineer",
        "default_tone": "technical and precise",
        "output_format": "well-commented code with explanation",
        "constraints": [
            "Follow best practices and design patterns",
            "Include error handling",
            "Add inline comments for complex logic",
            "Consider edge cases",
        ],
    },
    "content_creation": {
        "default_role": "Expert Content Writer",
        "default_tone": "engaging and professional",
        "output_format": "structured content with headings and sections",
        "constraints": [
            "Use clear and compelling language",
            "Include relevant examples",
            "Maintain consistent tone throughout",
            "Optimize for readability",
        ],
    },
    "research": {
        "default_role": "Research Analyst",
        "default_tone": "objective and analytical",
        "output_format": "structured research report with citations",
        "constraints": [
            "Use evidence-based arguments",
            "Present multiple perspectives",
            "Include data and statistics where relevant",
            "Cite sources appropriately",
        ],
    },
    "education": {
        "default_role": "Expert Educator",
        "default_tone": "clear and instructional",
        "output_format": "step-by-step guide with examples",
        "constraints": [
            "Break complex concepts into simple parts",
            "Use analogies and real-world examples",
            "Progress from basic to advanced",
            "Include practice exercises where appropriate",
        ],
    },
    "marketing": {
        "default_role": "Digital Marketing Strategist",
        "default_tone": "persuasive and action-oriented",
        "output_format": "actionable marketing plan with metrics",
        "constraints": [
            "Focus on target audience engagement",
            "Include measurable goals and KPIs",
            "Consider multiple marketing channels",
            "Emphasize ROI and conversion",
        ],
    },
    "analysis": {
        "default_role": "Senior Data Analyst",
        "default_tone": "analytical and data-driven",
        "output_format": "structured analysis report with findings",
        "constraints": [
            "Support conclusions with data",
            "Include visualizations where helpful",
            "Provide actionable recommendations",
            "Consider limitations and biases",
        ],
    },
}


def analyze_intent(user_input: str) -> Dict:
    """
    Analyze user input to classify intent and extract metadata.

    Returns:
        Dict with keys: category, confidence, keywords_matched,
                       template, subcategory
    """
    text = user_input.lower().strip()

    # Score each category
    scores: Dict[str, Tuple[int, List[str]]] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in text]
        scores[category] = (len(matched), matched)

    # Find best match
    best_category = max(scores, key=lambda k: scores[k][0])
    best_score, matched_keywords = scores[best_category]

    # Calculate confidence (0.0 - 1.0)
    if best_score == 0:
        # Default to content_creation for general requests
        best_category = "content_creation"
        confidence = 0.3
        matched_keywords = []
    else:
        total_possible = len(CATEGORY_KEYWORDS[best_category])
        confidence = min(1.0, (best_score / max(total_possible * 0.15, 1)))

    template = CATEGORY_TEMPLATES.get(best_category, CATEGORY_TEMPLATES["content_creation"])

    return {
        "category": best_category,
        "confidence": round(confidence, 2),
        "keywords_matched": matched_keywords,
        "template": template,
        "all_scores": {k: v[0] for k, v in scores.items()},
    }
