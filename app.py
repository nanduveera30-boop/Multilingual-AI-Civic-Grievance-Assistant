import importlib
import streamlit as st

from services import authority_service
from services.ollama_service import generate_complaint_package
from services.translation_service import detect_language, translate
from utils.helpers import get_text, load_translations, translate_dynamic

authority_service = importlib.reload(authority_service)

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
}
DISTRICT_OPTIONS = [
    "Adilabad",
    "Bhadradri Kothagudem",
    "Hyderabad",
    "Jagtial",
    "Jangaon",
    "Jayashankar Bhupalpally",
    "Jogulamba Gadwal",
    "Kamareddy",
    "Karimnagar",
    "Khammam",
    "Kumuram Bheem Asifabad",
    "Mahabubabad",
    "Mahabubnagar",
    "Mancherial",
    "Medak",
    "Medchal-Malkajgiri",
    "Mulugu",
    "Narayanpet",
    "Nalgonda",
    "Nirmal",
    "Nizamabad",
    "Peddapalli",
    "Rajanna Sircilla",
    "Rangareddy",
    "Sangareddy",
    "Siddipet",
    "Suryapet",
    "Vikarabad",
    "Wanaparthy",
    "Warangal Rural",
    "Warangal Urban",
    "Yadadri Bhuvanagiri",
]
DEFAULT_LANGUAGE = "English"
DEFAULT_DISTRICT = "Hyderabad"


def initialize_language():
    if "ui_language" not in st.session_state:
        st.session_state["ui_language"] = DEFAULT_LANGUAGE
    if "language" not in st.session_state:
        st.session_state["language"] = LANGUAGES[st.session_state["ui_language"]]
    if "translations" not in st.session_state or st.session_state["translations"] is None:
        st.session_state["translations"] = load_translations(st.session_state["language"])
    if "selected_district" not in st.session_state:
        st.session_state["selected_district"] = DEFAULT_DISTRICT


def on_language_change():
    st.session_state["language"] = LANGUAGES[st.session_state["ui_language"]]
    st.session_state["translations"] = load_translations(st.session_state["language"])


initialize_language()
st.set_page_config(page_title=get_text("page_title"), layout="wide")


def render_sidebar():
    st.sidebar.header(get_text("sidebar_header"))
    st.sidebar.selectbox(
        get_text("select_language_label"),
        list(LANGUAGES.keys()),
        key="ui_language",
        on_change=on_language_change,
    )
    st.sidebar.selectbox(
        get_text("select_district_label"),
        DISTRICT_OPTIONS,
        key="selected_district",
    )
    st.sidebar.markdown(get_text("sidebar_description"))


def render_header():
    st.title(get_text("hero_title"))
    st.markdown(get_text("hero_description"))


def render_issue_form():
    with st.form(key="issue_form"):
        issue_text = st.text_area(
            get_text("issue_text_label"),
            placeholder=get_text("issue_text_placeholder"),
            height=150,
        )
        analyze = st.form_submit_button(get_text("analyze_button"))
    return issue_text.strip(), analyze


render_sidebar()
render_header()
issue_text, analyze = render_issue_form()
output_language = st.session_state["language"]

if analyze and issue_text:
    source_language = detect_language(issue_text)
    canonical_text = issue_text
    if source_language != "en":
        canonical_text = translate(issue_text, "en")

    issue_category = authority_service.categorize_issue(canonical_text)
    authority_info = authority_service.get_authority_info(
        canonical_text,
        issue_category,
        district=st.session_state["selected_district"],
    )
    urgency = authority_service.estimate_urgency(canonical_text)
    escalation = authority_service.get_escalation_path(issue_category)
    complaint_package = generate_complaint_package(canonical_text, authority_info)

    severity_key = f"severity_{urgency['severity'].lower()}"
    st.success(get_text("analysis_complete_message"))
    st.header(get_text("issue_summary_header"))
    st.markdown(
        f"**{get_text('detected_category_label')}:** {translate_dynamic('category', issue_category)}"
    )
    st.markdown(
        f"**{get_text('responsible_department_label')}:** {translate_dynamic('department', authority_info.get('department'))}"
    )
    st.markdown(
        f"**{get_text('severity_label')}:** {get_text(severity_key)}"
    )
    reason_key = urgency.get("reason_key")
    reason_text = get_text(reason_key, default=urgency.get("reason")) if reason_key else urgency.get("reason")
    st.markdown(f"**{get_text('reason_label')}:** {reason_text}")

    st.subheader(get_text("where_to_complain_header"))
    st.markdown(
        f"**{get_text('department_label')}:** {translate_dynamic('department', authority_info.get('department'))}"
    )
    st.markdown(f"**{get_text('submission_options_label')}:**")
    for option in authority_info.get("submission_options", []):
        st.markdown(f"- {translate_dynamic('submission_option', option, option)}")
    st.markdown(f"**{get_text('priority_label')}:** {get_text(severity_key)}")

    st.subheader(get_text("submit_through_header"))
    st.markdown(
        f"**{get_text('portal_label')}:** {authority_info.get('grievance_portal')}  "
    )
    st.markdown(
        f"**{get_text('website_label')}:** {authority_info.get('website')}  "
    )
    if authority_info.get("email"):
        st.markdown(f"**{get_text('email_contact_label')}:** {authority_info.get('email')}")
    if authority_info.get("helpline"):
        st.markdown(f"**{get_text('helpline_label')}:** {authority_info.get('helpline')}")
    elif authority_info.get("contact"):
        st.markdown(f"**{get_text('contact_label')}:** {authority_info.get('contact')}")

    st.subheader(get_text("recommended_action_header"))
    for idx, action in enumerate(complaint_package["recommended_actions"], start=1):
        if isinstance(action, dict):
            action_text = get_text(
                action.get("key", ""),
                default=action.get("default", ""),
                **action.get("params", {}),
            )
        else:
            action_text = translate_dynamic("recommended_action", action, action)
        st.markdown(f"{idx}. {action_text}")

    st.subheader(get_text("escalation_guidance_header"))
    for level in escalation:
        st.markdown(
            f"**{translate_dynamic('escalation_level', level['level'], level['level'])}:** {translate_dynamic('office', level['office'], level['office'])}  "
        )

    st.subheader(get_text("complaint_formats_header"))
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"**{get_text('formal_letter_title')}**")
        st.text_area(get_text("formal_letter_label"), complaint_package["formal_letter"], height=250)
        st.markdown(f"**{get_text('email_title')}**")
        st.text_area(get_text("email_label"), complaint_package["email_text"], height=180)
    with cols[1]:
        st.markdown(f"**{get_text('whatsapp_title')}**")
        st.text_area(get_text("whatsapp_label"), complaint_package["whatsapp_text"], height=120)
        st.markdown(f"**{get_text('twitter_title')}**")
        st.text_area(get_text("twitter_label"), complaint_package["twitter_text"], height=120)

    st.subheader(get_text("ai_system_header"))
    st.markdown(get_text("ai_system_description"))

    if output_language != "en":
        st.subheader(get_text("local_translation_header"))
        translated_letter = translate(complaint_package["formal_letter"], output_language)
        st.text_area(get_text("translated_formal_letter_label"), translated_letter, height=250)
else:
    st.warning(get_text("enter_issue_warning"))
