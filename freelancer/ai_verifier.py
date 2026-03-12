"""
freelancer/ai_verifier.py
--------------------------
AI-powered fraud detection for freelancer profiles.

Uses:
  - GitHub REST API  → profile stats
  - Google Gemini    → reasoning + scoring

Results are saved back to FreelancerProfile:
  verification_status, fraud_score, ai_verification_report
"""

import os
import re
import json
import base64
import threading
import logging
import requests

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Gemini helper
# ------------------------------------------------------------------

def _gemini_text(prompt: str) -> str:
    """Send a text-only prompt to Gemini and return the response text."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return "GEMINI_API_KEY not configured."

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-1.5-flash:generateContent"
        f"?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 600},
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        candidates = resp.json().get("candidates", [])
        if candidates:
            return candidates[0]["content"]["parts"][0]["text"]
    except Exception as exc:
        logger.error("Gemini text request failed: %s", exc)
    return ""


def _gemini_vision(prompt: str, image_b64: str, mime: str = "image/png") -> str:
    """Send image + text prompt to Gemini Vision and return the response text."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return "GEMINI_API_KEY not configured."

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-1.5-flash:generateContent"
        f"?key={api_key}"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"inlineData": {"mimeType": mime, "data": image_b64}},
                ]
            }
        ],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 700},
    }
    try:
        resp = requests.post(url, json=payload, timeout=45)
        resp.raise_for_status()
        candidates = resp.json().get("candidates", [])
        if candidates:
            return candidates[0]["content"]["parts"][0]["text"]
    except Exception as exc:
        logger.error("Gemini vision request failed: %s", exc)
    return ""


# ------------------------------------------------------------------
# Extract numeric score from Gemini response
# ------------------------------------------------------------------

def _extract_score(text: str, fallback: int = 50) -> int:
    """Parse first integer in 'FRAUD_SCORE: <n>' or similar from AI text."""
    match = re.search(r"FRAUD_SCORE[:\s]+(\d+)", text, re.IGNORECASE)
    if match:
        return min(100, max(0, int(match.group(1))))
    # Fallback: first standalone number 0-100
    nums = re.findall(r"\b(\d{1,3})\b", text)
    for n in nums:
        if 0 <= int(n) <= 100:
            return int(n)
    return fallback


# ------------------------------------------------------------------
# GitHub verification
# ------------------------------------------------------------------

def verify_github(github_url: str) -> dict:
    """
    Analyse a GitHub profile URL using the GitHub API + Gemini.
    Returns:
        {
          'score': int (0=trustworthy, 100=fraudulent),
          'report': str
        }
    """
    if not github_url:
        return {"score": 0, "report": "No GitHub URL provided; skipping GitHub check."}

    # Extract username from URL
    match = re.search(r"github\.com/([A-Za-z0-9_.-]+)", github_url)
    if not match:
        return {
            "score": 60,
            "report": f"Could not parse a GitHub username from the URL: {github_url}.",
        }

    username = match.group(1)

    # Fetch GitHub API
    try:
        gh_resp = requests.get(
            f"https://api.github.com/users/{username}",
            headers={"Accept": "application/vnd.github+json"},
            timeout=10,
        )
        if gh_resp.status_code == 404:
            return {
                "score": 80,
                "report": f"GitHub user '{username}' does not exist. Likely a fake URL.",
            }
        gh_data = gh_resp.json()
    except Exception as exc:
        return {"score": 40, "report": f"GitHub API request failed: {exc}"}

    # Collect key stats
    public_repos   = gh_data.get("public_repos", 0)
    followers      = gh_data.get("followers", 0)
    following      = gh_data.get("following", 0)
    created_at     = gh_data.get("created_at", "unknown")
    account_type   = gh_data.get("type", "User")
    bio            = gh_data.get("bio") or "none"
    name           = gh_data.get("name") or "not set"

    prompt = f"""
You are a freelance platform fraud-detection specialist.

Analyse this GitHub profile data and decide if the account looks GENUINE or FAKE/FRAUDULENT:

username       : {username}
name           : {name}
bio            : {bio}
account type   : {account_type}
created at     : {created_at}
public repos   : {public_repos}
followers      : {followers}
following      : {following}

Scoring rules:
- Newly created account (< 3 months old) with 0–2 repos and 0 followers → HIGH fraud risk
- Account with many repos, followers, activity → LOW fraud risk
- Mismatch between profile and typical real developer → MEDIUM risk

Return:
1. A brief assessment (max 5 sentences).
2. A line: FRAUD_SCORE: <number 0-100>  (0 = definitely real, 100 = definitely fake)
"""

    report = _gemini_text(prompt)
    score  = _extract_score(report, fallback=30)

    return {"score": score, "report": f"=== GitHub Analysis ({username}) ===\n{report}"}


# ------------------------------------------------------------------
# Certificate verification
# ------------------------------------------------------------------

def verify_certificate(file_path: str) -> dict:
    """
    Analyse an uploaded certificate file using Gemini Vision.
    Supports JPEG, PNG, and PDFs (first page rendered as image by Gemini).
    Returns:
        {
          'score': int (0=authentic, 100=fake/tampered),
          'report': str
        }
    """
    if not file_path or not os.path.exists(file_path):
        return {"score": 0, "report": "No certificate uploaded; skipping certificate check."}

    # Determine MIME type
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
    }
    mime = mime_map.get(ext, "image/jpeg")

    # Read & encode
    try:
        with open(file_path, "rb") as f:
            raw = f.read()
        image_b64 = base64.b64encode(raw).decode("utf-8")
    except Exception as exc:
        return {"score": 50, "report": f"Could not read certificate file: {exc}"}

    prompt = """
You are a certificate fraud detection expert for a freelancing platform.

Examine this certificate image carefully and assess its authenticity.

Check for:
1. Signs of digital tampering or photoshopping (pixel inconsistencies, fonts, misaligned elements)
2. Whether the issuing organisation looks real and reputable
3. Whether the layout, seal, and signatures look genuine
4. Any suspicious quality issues (blurriness, cut-and-paste artifacts)

Return:
1. A brief assessment (max 6 sentences) of what you see.
2. A line: FRAUD_SCORE: <number 0-100>  (0 = looks completely authentic, 100 = clearly fake/tampered)
"""

    report = _gemini_vision(prompt, image_b64, mime)
    score  = _extract_score(report, fallback=40)

    return {"score": score, "report": f"=== Certificate Analysis ===\n{report}"}


# ------------------------------------------------------------------
# Full verification orchestrator
# ------------------------------------------------------------------

def run_full_verification(profile_id: int) -> None:
    """
    Runs both GitHub and certificate checks for a FreelancerProfile,
    then saves results back to the database.
    Designed to be called in a background thread.
    """
    # Import inside function to avoid circular imports at module load time
    from freelancer.models import FreelancerProfile  # noqa

    try:
        profile = FreelancerProfile.objects.get(pk=profile_id)
    except FreelancerProfile.DoesNotExist:
        logger.error("run_full_verification: profile %s not found", profile_id)
        return

    try:
        # ── GitHub ──
        gh_result   = verify_github(profile.github_url or "")

        # ── Certificate ──
        cert_path = ""
        if profile.certificate:
            try:
                cert_path = profile.certificate.path
            except Exception:
                cert_path = ""
        cert_result = verify_certificate(cert_path)

        # ── Combine ──
        combined_score = int((gh_result["score"] + cert_result["score"]) / 2)

        if combined_score >= 70:
            status = "SUSPICIOUS"
        elif combined_score <= 30:
            status = "VERIFIED"
        else:
            status = "UNVERIFIED"

        full_report = (
            gh_result["report"]
            + "\n\n"
            + cert_result["report"]
            + f"\n\n=== Overall Fraud Score: {combined_score}/100 ==="
        )

        profile.fraud_score            = combined_score
        profile.verification_status   = status
        profile.ai_verification_report = full_report
        profile.save(update_fields=["fraud_score", "verification_status", "ai_verification_report"])

        logger.info(
            "Verification complete for profile %s → %s (score %s)",
            profile_id, status, combined_score,
        )

    except Exception as exc:
        logger.error("run_full_verification failed for profile %s: %s", profile_id, exc)
        try:
            profile.verification_status = "UNVERIFIED"
            profile.ai_verification_report = f"Verification error: {exc}"
            profile.save(update_fields=["verification_status", "ai_verification_report"])
        except Exception:
            pass


def trigger_verification_async(profile_id: int) -> None:
    """Fire-and-forget: launch verification in a daemon thread."""
    t = threading.Thread(target=run_full_verification, args=(profile_id,), daemon=True)
    t.start()
