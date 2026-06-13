import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "authorities.json")

KEYWORD_MAP = {
    "pothole": "Road Damage",
    "road": "Road Damage",
    "drainage": "Drainage",
    "sewer": "Sanitation",
    "garbage": "Garbage Collection",
    "waste": "Garbage Collection",
    "water": "Water Supply",
    "tap": "Water Supply",
    "electricity": "Electricity Outage",
    "power": "Electricity Outage",
    "light": "Streetlight Issue",
    "streetlight": "Streetlight Issue",
    "pollution": "Pollution",
    "signal": "Traffic Signal",
}


def _load_authority_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {}


authority_data = _load_authority_data()


def categorize_issue(issue_text: str) -> str:
    text = issue_text.lower()
    for keyword, category in KEYWORD_MAP.items():
        if keyword in text:
            return category
    return "General Civic Issue"


CITY_OVERRIDES = {
    "hyderabad": {
        "local_office": "Greater Hyderabad Municipal Corporation Office",
        "email": "ghmc.support@telangana.gov.in",
        "helpline": "040-1234-5678",
    },
    "warangal": {
        "local_office": "Warangal Municipal Corporation Office",
        "email": "warangal.support@telangana.gov.in",
        "helpline": "0870-123-4567",
    },
    "karimnagar": {
        "local_office": "Karimnagar Municipal Corporation Office",
        "email": "karimnagar.support@telangana.gov.in",
        "helpline": "0878-123-4567",
    },
    "nizamabad": {
        "local_office": "Nizamabad Municipal Office",
        "email": "nizamabad.support@telangana.gov.in",
        "helpline": "08462-123456",
    },
    "rangareddy": {
        "local_office": "Rangareddy District Municipal Office",
        "email": "rangareddy.support@telangana.gov.in",
        "helpline": "040-2345-6789",
    },
    "medchal-malkajgiri": {
        "local_office": "Medchal-Malkajgiri Municipal Office",
        "email": "medchal.support@telangana.gov.in",
        "helpline": "040-3456-7890",
    },
}


def get_authority_info(issue_text: str, category: str, district: str = None, *args, **kwargs) -> dict:
    info = authority_data.get(category, {}).copy()
    if not info:
        info = {
            "department": "Municipal Corporation",
            "website": "https://spandana.telangana.gov.in",
            "grievance_portal": "https://spandana.telangana.gov.in",
            "submission_options": [
                "Local Municipal Office",
                "Grievance Portal",
                "Email",
                "Phone Helpline",
            ],
            "email": "support@telangana.gov.in",
            "helpline": "1800-123-456",
        }

    if district:
        district_key = district.strip().lower()
        override = CITY_OVERRIDES.get(district_key)
        if override:
            info = {**info, **override}
            if "local_office" in override:
                office_name = override["local_office"]
                if "Local Municipal Office" in info.get("submission_options", []):
                    info["submission_options"] = [
                        office_name if option == "Local Municipal Office" else option
                        for option in info.get("submission_options", [])
                    ]
    return info


def estimate_urgency(issue_text: str) -> dict:
    text = issue_text.lower()
    if any(word in text for word in ["accident", "danger", "fatal", "risk", "unsafe"]):
        return {
            "severity": "High",
            "reason_key": "reason_public_safety",
            "reason": "Public safety risk due to accident possibility.",
        }
    if any(word in text for word in ["leak", "contamination", "pollution"]):
        return {
            "severity": "High",
            "reason_key": "reason_health_safety",
            "reason": "Health and safety concern needs timely redressal.",
        }
    if any(word in text for word in ["broken", "not working", "delay"]):
        return {
            "severity": "Medium",
            "reason_key": "reason_service_disruption",
            "reason": "Service disruption should be resolved soon.",
        }
    return {
        "severity": "Medium",
        "reason_key": "reason_general_civic_issue",
        "reason": "Issue should be addressed through the appropriate civic department.",
    }


def get_escalation_path(category: str) -> list:
    return [
        {"level": "Level 1", "office": "Municipal Complaint Portal"},
        {"level": "Level 2", "office": "District Collector Grievance Cell"},
        {"level": "Level 3", "office": "State Public Grievance Portal"},
    ]
