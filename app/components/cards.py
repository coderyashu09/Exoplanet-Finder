"""Visual card components for candidate profiles, stellar parameters, and ML predictions."""
import streamlit as st


def render_prediction_badge(category: str, prob: float, threshold: float) -> None:
    """Render high-visibility verdict badge."""
    if category == "Planet-like Signal":
        badge_style = "background: rgba(53, 212, 154, 0.15); border: 2px solid #35D49A; color: #35D49A;"
        icon = "🪐"
        verdict_desc = f"Transit signal exceeds threshold ({threshold:.2f}) with high planetary probability ({prob*100:.1f}%)."
    elif category == "Non-Planet Signal":
        badge_style = "background: rgba(255, 101, 122, 0.15); border: 2px solid #FF657A; color: #FF657A;"
        icon = "❌"
        verdict_desc = f"Transit signal is consistent with astrophysical false positive or stellar variability ({prob*100:.1f}% probability)."
    else:
        badge_style = "background: rgba(255, 190, 85, 0.15); border: 2px solid #FFBE55; color: #FFBE55;"
        icon = "⚠️"
        verdict_desc = "Insufficient light curve coverage or uninitialized neural weights to produce definitive classification."

    st.markdown(
        f"""
        <div style="border-radius: 12px; padding: 20px 24px; margin: 15px 0; {badge_style}">
            <div style="font-size: 0.8rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;">
                AI PREDICTION CLASSIFICATION
            </div>
            <div style="font-size: 2.1rem; font-weight: 800; margin: 6px 0; display: flex; align-items: center; gap: 10px;">
                <span>{icon}</span> <span>{category}</span>
            </div>
            <div style="font-size: 0.95rem; opacity: 0.9;">
                {verdict_desc}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_orbital_parameters_card(row: dict) -> None:
    """Render orbital parameters in a clean grid card."""
    period = row.get("tce_period", 0.0)
    epoch = row.get("tce_time0bk", 0.0)
    duration = row.get("tce_duration", 0.0)
    depth = row.get("tce_depth", 0.0)
    snr = row.get("tce_model_snr", 0.0)

    st.markdown(
        f"""
        <div style="background: #111C30; border: 1px solid #1D2B48; border-radius: 12px; padding: 18px 22px; margin-bottom: 20px;">
            <div style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: #9AAAC1; margin-bottom: 12px; font-weight: 600;">
                Orbital Ephemeris & Transit Parameters
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 14px;">
                <div>
                    <div style="font-size: 0.75rem; color: #9AAAC1;">Orbital Period</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #63B3FF; font-family: monospace;">{period:.4f} d</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #9AAAC1;">Transit Epoch (t₀)</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #F4F7FF; font-family: monospace;">{epoch:.3f} BKJD</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #9AAAC1;">Transit Duration</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #F4F7FF; font-family: monospace;">{duration:.2f} hrs</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #9AAAC1;">Transit Depth</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #35D49A; font-family: monospace;">{depth:,.0f} ppm</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #9AAAC1;">Model SNR</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #FFBE55; font-family: monospace;">{snr:.1f}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

