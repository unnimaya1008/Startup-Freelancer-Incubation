import os
import re
import threading
import logging
import requests

logger = logging.getLogger(__name__)


def _extract_score(text: str, fallback: int = 50) -> int:
    match = re.search(r"PROPOSAL_SCORE[:\\s]+(\\d+)", text or "", re.IGNORECASE)
    if match:
        return min(100, max(0, int(match.group(1))))
    nums = re.findall(r"\\b(\\d{1,3})\\b", text or "")
    for n in nums:
        if 0 <= int(n) <= 100:
            return int(n)
    return fallback


def _gemini_score(prompt: str) -> tuple[int, str]:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return 0, "GEMINI_API_KEY not configured."

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-1.5-flash:generateContent"
        f"?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500},
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        candidates = resp.json().get("candidates", [])
        if candidates:
            text = candidates[0]["content"]["parts"][0]["text"]
            return _extract_score(text, fallback=60), text
    except Exception as exc:
        logger.error("Proposal ranking request failed: %s", exc)
    return 0, ""


def _fallback_rank(rating_overall: float, verification_status: str, fraud_score: int) -> int:
    status_bonus = {
        "VERIFIED": 25,
        "UNVERIFIED": 0,
        "PENDING": -5,
        "SUSPICIOUS": -30,
    }.get(verification_status or "", 0)

    rating_bonus = int((rating_overall or 0) * 12)
    fraud_penalty = int((fraud_score or 0) * 0.25)
    score = 45 + rating_bonus + status_bonus - fraud_penalty
    return min(100, max(0, score))


def rank_proposal(proposal_id: int) -> None:
    from projects.models import ProjectProposal

    try:
        proposal = ProjectProposal.objects.select_related("freelancer", "freelancer__user").get(pk=proposal_id)
    except ProjectProposal.DoesNotExist:
        logger.error("rank_proposal: proposal %s not found", proposal_id)
        return

    freelancer = proposal.freelancer
    rating_data = freelancer.get_average_ratings
    rating_overall = rating_data.get("overall", 0)
    rating_count = rating_data.get("count", 0)

    prompt = f"""
You are ranking freelancer proposals for a startup.

Consider:
- Proposal quality (clarity, feasibility, detail)
- Freelancer verification status and fraud score
- Freelancer rating (average and count)

Freelancer summary:
name: {freelancer.full_name}
verification_status: {freelancer.verification_status}
fraud_score: {freelancer.fraud_score}
rating_overall: {rating_overall} (from {rating_count} ratings)

Proposal:
{proposal.proposal_text}

Return:
1. Brief reasoning (max 6 sentences) that explicitly cites verification status, rating, and proposal quality.
2. Line: PROPOSAL_SCORE: <number 0-100> (higher is better)
"""

    ai_score, ai_report = _gemini_score(prompt)
    if ai_score <= 0:
        rank_score = _fallback_rank(rating_overall, freelancer.verification_status, freelancer.fraud_score)
        ai_report = ai_report or "AI ranking unavailable. Used fallback scoring."
        ai_score = 0
    else:
        rank_score = ai_score

    proposal.ai_score = ai_score
    proposal.ai_report = ai_report
    proposal.rank_score = rank_score
    proposal.save(update_fields=["ai_score", "ai_report", "rank_score"])


def trigger_proposal_rank_async(proposal_id: int) -> None:
    t = threading.Thread(target=rank_proposal, args=(proposal_id,), daemon=True)
    t.start()
