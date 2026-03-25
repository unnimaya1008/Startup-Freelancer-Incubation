import threading
import re

from freelancer.ai_verifier import verify_github, verify_certificate, _gemini_text, _extract_score


def _is_valid_github_url(url: str) -> bool:
    if not url:
        return False
    return re.match(r"^https?://(www\.)?github\.com/[^/\s]+/?$", url.strip(), re.IGNORECASE) is not None


def _is_valid_linkedin_url(url: str) -> bool:
    if not url:
        return False
    return re.match(r"^https?://(www\.)?linkedin\.com/.*$", url.strip(), re.IGNORECASE) is not None


def verify_linkedin(linkedin_url: str) -> dict:
    if not linkedin_url:
        return {"score": 0, "report": "No LinkedIn URL provided; skipping LinkedIn check."}

    prompt = f"""
You are verifying a mentor profile.
Assess if this LinkedIn URL looks plausible and consistent for a real professional profile.
LinkedIn URL: {linkedin_url}

Return:
1. Brief assessment (max 4 sentences).
2. Line: FRAUD_SCORE: <number 0-100>
"""
    report = _gemini_text(prompt)
    score = _extract_score(report, fallback=30)
    return {"score": score, "report": f"=== LinkedIn Analysis ===\n{report}"}


def run_full_verification(profile_id: int) -> None:
    from mentors.models import MentorProfile  # avoid circular

    try:
        profile = MentorProfile.objects.get(pk=profile_id)
    except MentorProfile.DoesNotExist:
        return

    try:
        github_url = (profile.github_url or "").strip()
        linkedin_url = (profile.linkedin_profile or "").strip()

        if not github_url and not linkedin_url:
            profile.verification_status = "UNVERIFIED"
            profile.ai_verification_report = (
                "Verification requires GitHub or LinkedIn. None provided, marking as Unverified."
            )
            profile.save(update_fields=["verification_status", "ai_verification_report"])
            return

        if github_url and not _is_valid_github_url(github_url):
            profile.verification_status = "UNVERIFIED"
            profile.ai_verification_report = "Invalid GitHub URL provided. Marking as Unverified."
            profile.save(update_fields=["verification_status", "ai_verification_report"])
            return

        if linkedin_url and not _is_valid_linkedin_url(linkedin_url):
            profile.verification_status = "UNVERIFIED"
            profile.ai_verification_report = "Invalid LinkedIn URL provided. Marking as Unverified."
            profile.save(update_fields=["verification_status", "ai_verification_report"])
            return

        gh_result = verify_github(github_url)
        cert_path = ""
        if profile.certificate:
            try:
                cert_path = profile.certificate.path
            except Exception:
                cert_path = ""
        cert_result = verify_certificate(cert_path)
        li_result = verify_linkedin(linkedin_url)

        scores = [gh_result["score"], cert_result["score"]]
        if linkedin_url:
            scores.append(li_result["score"])

        combined_score = int(sum(scores) / len(scores))

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
            + ("\n\n" + li_result["report"] if linkedin_url else "")
            + f"\n\n=== Overall Fraud Score: {combined_score}/100 ==="
        )

        profile.fraud_score = combined_score
        profile.verification_status = status
        profile.ai_verification_report = full_report
        profile.save(update_fields=["fraud_score", "verification_status", "ai_verification_report"])

    except Exception as exc:
        profile.verification_status = "UNVERIFIED"
        profile.ai_verification_report = f"Verification error: {exc}"
        profile.save(update_fields=["verification_status", "ai_verification_report"])


def trigger_verification_async(profile_id: int) -> None:
    t = threading.Thread(target=run_full_verification, args=(profile_id,), daemon=True)
    t.start()
