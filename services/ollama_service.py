def generate_complaint_package(issue_text: str, authority_info: dict) -> dict:
    department = authority_info.get("department", "Municipal Corporation")
    portal = authority_info.get("grievance_portal", "https://spandana.ap.gov.in")
    website = authority_info.get("website", "https://spandana.ap.gov.in")

    formal_letter = (
        f"To:\n{department}\n\n"
        f"Subject: Request for urgent action on civic issue\n\n"
        f"Dear Sir/Madam,\n\n"
        f"I am writing to report the following issue: {issue_text}.\n"
        f"This issue is affecting public safety and requires immediate attention.\n\n"
        f"Please investigate and take corrective action as soon as possible.\n\n"
        f"Thank you,\n[Your Name]"
    )

    email_text = (
        f"Hello,\n\nI want to report this civic issue: {issue_text}.\n"
        f"Please take necessary action at the earliest.\n\nThank you."
    )

    whatsapp_text = (
        f"{issue_text}. Kindly arrange repairs immediately."
    )

    twitter_text = (
        f"{issue_text}. Request authorities to address this issue urgently."
    )

    recommended_actions = [
        {"key": "recommended_action_submit_complaint", "params": {"department": department}},
        {"key": "recommended_action_attach_photos"},
        {"key": "recommended_action_mention_safety"},
        {"key": "recommended_action_keep_reference"},
        {"key": "recommended_action_escalate"},
    ]

    return {
        "formal_letter": formal_letter,
        "email_text": email_text,
        "whatsapp_text": whatsapp_text,
        "twitter_text": twitter_text,
        "recommended_actions": recommended_actions,
        "portal": portal,
        "website": website,
    }
