"""Custom CSS injection and design system components for NASA Exoplanet Finder."""
import streamlit as st

CUSTOM_CSS = """
<style>
/* Space Deep Theme Custom Styling */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #F4F7FF;
}

/* Base background */
.stApp {
    background-color: #070B14;
    background-image: radial-gradient(circle at 50% 0%, #111C30 0%, #070B14 75%);
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #0D1424 !important;
    border-right: 1px solid #1B2844;
}

section[data-testid="stSidebar"] div.stRadio > label {
    color: #9AAAC1 !important;
}

/* Dashboard Metric Cards */
.metric-card {
    background: #111C30;
    border: 1px solid #1D2B48;
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 15px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: #63B3FF;
}

.metric-card.accent-blue { border-top: 3px solid #63B3FF; }
.metric-card.accent-purple { border-top: 3px solid #8B7CFF; }
.metric-card.accent-green { border-top: 3px solid #35D49A; }
.metric-card.accent-amber { border-top: 3px solid #FFBE55; }
.metric-card.accent-rose { border-top: 3px solid #FF657A; }

.metric-label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9AAAC1;
    font-weight: 600;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #F4F7FF;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.2;
}

.metric-subtext {
    font-size: 0.78rem;
    color: #9AAAC1;
    margin-top: 6px;
}

/* Hero Header */
.nasa-hero {
    background: linear-gradient(135deg, rgba(17, 28, 48, 0.8) 0%, rgba(13, 20, 36, 0.9) 100%);
    border: 1px solid #1D2B48;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 25px;
    position: relative;
    overflow: hidden;
}

.nasa-hero::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 250px;
    height: 100%;
    background: radial-gradient(circle at center, rgba(99, 179, 255, 0.12) 0%, transparent 70%);
    pointer-events: none;
}

.hero-title {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #F4F7FF;
    margin-bottom: 6px;
}

.hero-tagline {
    font-size: 1.05rem;
    color: #9AAAC1;
    font-weight: 400;
    margin-bottom: 12px;
}

.badge-tag {
    display: inline-block;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 20px;
    margin-right: 8px;
    letter-spacing: 0.04em;
    font-family: 'JetBrains Mono', monospace;
}

.badge-pc { background: rgba(53, 212, 154, 0.15); color: #35D49A; border: 1px solid rgba(53, 212, 154, 0.3); }
.badge-afp { background: rgba(255, 101, 122, 0.15); color: #FF657A; border: 1px solid rgba(255, 101, 122, 0.3); }
.badge-ntp { background: rgba(255, 190, 85, 0.15); color: #FFBE55; border: 1px solid rgba(255, 190, 85, 0.3); }
.badge-nasa { background: rgba(99, 179, 255, 0.15); color: #63B3FF; border: 1px solid rgba(99, 179, 255, 0.3); }

/* Scientific Info Callout */
.science-alert {
    background: #111C30;
    border-left: 4px solid #63B3FF;
    border-radius: 6px;
    padding: 14px 18px;
    margin: 15px 0;
    font-size: 0.88rem;
    color: #D1DCF0;
}

.science-alert.warning { border-left-color: #FFBE55; }
.science-alert.success { border-left-color: #35D49A; }
.science-alert.danger { border-left-color: #FF657A; }

/* Custom table styling */
div[data-testid="stDataFrame"] {
    border: 1px solid #1D2B48;
    border-radius: 8px;
    background: #0D1424;
}

/* Custom scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #070B14;
}
::-webkit-scrollbar-thumb {
    background: #1D2B48;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #63B3FF;
}
</style>
"""


def apply_custom_css() -> None:
    """Inject NASA deep-space custom CSS into Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero(
    title: str = "EXOPLANET FINDER",
    tagline: str = "Discover New Worlds Beyond Our Solar System.",
    badges: list[tuple[str, str]] = None,
) -> None:
    """Render the master hero banner."""
    badges = badges or [("NASA Kepler DR24", "badge-nasa"), ("Dual-View 1D CNN", "badge-pc")]
    badges_html = "".join([f'<span class="badge-tag {cls}">{txt}</span>' for txt, cls in badges])

    st.markdown(
        f"""
        <div class="nasa-hero">
            <div class="hero-title">{title}</div>
            <div class="hero-tagline">{tagline}</div>
            <div>{badges_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(
    label: str,
    value: str,
    subtext: str = "",
    accent: str = "blue",
) -> None:
    """Render a styled scientific metric card."""
    accent_class = f"accent-{accent}"
    st.markdown(
        f"""
        <div class="metric-card {accent_class}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-subtext">{subtext}</div>' if subtext else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alert(text: str, level: str = "info") -> None:
    """Render scientific alert callout box."""
    level_class = level if level in ["warning", "success", "danger"] else "info"
    st.markdown(
        f"""
        <div class="science-alert {level_class}">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )

