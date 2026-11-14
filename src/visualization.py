"""NASA-inspired Plotly astronomical data visualizations and styling templates."""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Theme Colors
BG_COLOR = "#070B14"
PAPER_COLOR = "#0D1424"
CARD_COLOR = "#111C30"
ACCENT_PRIMARY = "#63B3FF"
ACCENT_SECONDARY = "#8B7CFF"
SUCCESS_COLOR = "#35D49A"
WARNING_COLOR = "#FFBE55"
DANGER_COLOR = "#FF657A"
TEXT_PRIMARY = "#F4F7FF"
TEXT_MUTED = "#9AAAC1"
GRID_COLOR = "#1B2844"


def apply_space_theme(fig: go.Figure, title: str = "", height: int = 450) -> go.Figure:
    """Apply consistent NASA deep-space aesthetic to a Plotly figure."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>" if title else "",
            "font": {"family": "Inter, Roboto, sans-serif", "size": 16, "color": TEXT_PRIMARY},
            "x": 0.02,
            "y": 0.95,
        },
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=PAPER_COLOR,
        font={"family": "Inter, Roboto, sans-serif", "color": TEXT_PRIMARY, "size": 12},
        height=height,
        margin={"l": 50, "r": 30, "t": 50, "b": 50},
        xaxis={
            "gridcolor": GRID_COLOR,
            "linecolor": GRID_COLOR,
            "tickfont": {"color": TEXT_MUTED},
            "title_font": {"color": TEXT_PRIMARY, "size": 13},
            "showgrid": True,
            "zeroline": False,
        },
        yaxis={
            "gridcolor": GRID_COLOR,
            "linecolor": GRID_COLOR,
            "tickfont": {"color": TEXT_MUTED},
            "title_font": {"color": TEXT_PRIMARY, "size": 13},
            "showgrid": True,
            "zeroline": False,
        },
        legend={
            "bgcolor": CARD_COLOR,
            "bordercolor": GRID_COLOR,
            "borderwidth": 1,
            "font": {"color": TEXT_PRIMARY},
        },
        hoverlabel={
            "bgcolor": CARD_COLOR,
            "bordercolor": ACCENT_PRIMARY,
            "font": {"color": TEXT_PRIMARY, "family": "Inter, sans-serif"},
        },
    )
    return fig


def plot_raw_lightcurve(time_arr: np.ndarray, flux_arr: np.ndarray, title: str = "Stellar Photometry Time Series") -> go.Figure:
    """Plot original raw or stitched light curve."""
    fig = go.Figure()
    # Downsample visually if more than 50,000 cadences for snappy UI rendering
    stride = max(1, len(time_arr) // 25000)
    fig.add_trace(
        go.Scattergl(
            x=time_arr[::stride],
            y=flux_arr[::stride],
            mode="markers",
            marker={"size": 2.5, "color": ACCENT_PRIMARY, "opacity": 0.7},
            name="Kepler Long-Cadence Flux",
            hovertemplate="Time: %{x:.3f} BKJD<br>Flux: %{y:.2f} e-/s<extra></extra>",
        )
    )
    fig.update_xaxes(title_text="Time [BKJD = BJD - 2454833.0]")
    fig.update_yaxes(title_text="Stellar Flux [e-/s]")
    return apply_space_theme(fig, title)


def plot_raw_vs_flattened(
    time_arr: np.ndarray,
    raw_flux: np.ndarray,
    trend_flux: np.ndarray,
    flat_flux: np.ndarray,
) -> go.Figure:
    """Comparative dual-trace visualization: raw flux with continuum trend and flattened flux."""
    fig = go.Figure()
    stride = max(1, len(time_arr) // 20000)

    fig.add_trace(
        go.Scattergl(
            x=time_arr[::stride],
            y=raw_flux[::stride],
            mode="markers",
            marker={"size": 2, "color": TEXT_MUTED, "opacity": 0.4},
            name="Raw Flux",
        )
    )
    fig.add_trace(
        go.Scattergl(
            x=time_arr[::stride],
            y=trend_flux[::stride],
            mode="lines",
            line={"color": WARNING_COLOR, "width": 2},
            name="Continuum Trend (Savitzky-Golay)",
        )
    )
    fig.add_trace(
        go.Scattergl(
            x=time_arr[::stride],
            y=flat_flux[::stride],
            mode="markers",
            marker={"size": 2, "color": ACCENT_PRIMARY, "opacity": 0.6},
            name="Protected Flattened Flux",
            visible="legendonly",
        )
    )
    fig.update_xaxes(title_text="Time [BKJD]")
    fig.update_yaxes(title_text="Flux / Normalized Continuum")
    return apply_space_theme(fig, "Raw Photometry vs Protected Continuum Trend")


def plot_global_view(
    global_view: np.ndarray,
    period: float,
    attributions: Optional[np.ndarray] = None,
) -> go.Figure:
    """Plot Global Phase-Folded Transit Profile (2001 bins) with optional Integrated Gradients overlay."""
    half_p = period / 2.0
    phases = np.linspace(-half_p, half_p, len(global_view))
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=phases,
            y=global_view,
            mode="lines+markers",
            marker={"size": 3, "color": ACCENT_PRIMARY},
            line={"width": 1.5, "color": ACCENT_PRIMARY},
            name="Global View (2001 bins)",
            hovertemplate="Phase: %{x:.4f} days<br>Normalized Flux: %{y:.4f}<extra></extra>",
        )
    )

    if attributions is not None:
        # Scale attributions for secondary axis
        fig.add_trace(
            go.Scatter(
                x=phases,
                y=attributions,
                mode="lines",
                line={"width": 1.5, "color": WARNING_COLOR, "dash": "dot"},
                name="CNN Feature Attribution (Integrated Gradients)",
                yaxis="y2",
                hovertemplate="Phase: %{x:.4f}<br>Attribution: %{y:.4e}<extra></extra>",
            )
        )
        fig.update_layout(
            yaxis2={
                "title": "Attribution Weight",
                "overlaying": "y",
                "side": "right",
                "showgrid": False,
                "tickfont": {"color": WARNING_COLOR},
                "title_font": {"color": WARNING_COLOR},
            }
        )

    fig.update_xaxes(title_text="Orbital Phase [Days from Mid-Transit]")
    fig.update_yaxes(title_text="Normalized Relative Depth")
    return apply_space_theme(fig, f"Global View — Complete Orbit ({period:.2f} d)")


def plot_local_view(
    local_view: np.ndarray,
    duration_hours: float,
    attributions: Optional[np.ndarray] = None,
) -> go.Figure:
    """Plot Local View Zoomed Transit Profile (201 bins) with optional Integrated Gradients overlay."""
    dur_days = duration_hours / 24.0
    window_days = 4.0 * dur_days
    phases_hours = np.linspace(-window_days * 24.0, window_days * 24.0, len(local_view))
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=phases_hours,
            y=local_view,
            mode="lines+markers",
            marker={"size": 4, "color": SUCCESS_COLOR},
            line={"width": 2, "color": SUCCESS_COLOR},
            name="Local View (201 bins)",
            hovertemplate="Phase: %{x:.2f} hrs<br>Normalized Flux: %{y:.4f}<extra></extra>",
        )
    )

    # Ingress and egress marker guides
    half_dur = duration_hours / 2.0
    fig.add_vline(x=-half_dur, line_dash="dash", line_color=WARNING_COLOR, opacity=0.7, annotation_text="Ingress")
    fig.add_vline(x=half_dur, line_dash="dash", line_color=WARNING_COLOR, opacity=0.7, annotation_text="Egress")

    if attributions is not None:
        fig.add_trace(
            go.Scatter(
                x=phases_hours,
                y=attributions,
                mode="lines",
                line={"width": 2, "color": ACCENT_SECONDARY, "dash": "dot"},
                name="CNN Attribution",
                yaxis="y2",
                hovertemplate="Phase: %{x:.2f} hrs<br>Attribution: %{y:.4e}<extra></extra>",
            )
        )
        fig.update_layout(
            yaxis2={
                "title": "Attribution Weight",
                "overlaying": "y",
                "side": "right",
                "showgrid": False,
                "tickfont": {"color": ACCENT_SECONDARY},
                "title_font": {"color": ACCENT_SECONDARY},
            }
        )

    fig.update_xaxes(title_text="Phase relative to Mid-Transit [Hours]")
    fig.update_yaxes(title_text="Normalized Relative Depth")
    return apply_space_theme(fig, f"Local View — Transit Zoom (Duration: {duration_hours:.2f} hrs)")


def plot_training_history(history: Dict[str, list]) -> go.Figure:
    """Plot multi-epoch training and validation loss and ROC-AUC curves."""
    fig = go.Figure()
    epochs = history.get("epoch", [])

    fig.add_trace(
        go.Scatter(x=epochs, y=history.get("train_loss", []), mode="lines+markers", name="Train Loss", line={"color": ACCENT_PRIMARY})
    )
    fig.add_trace(
        go.Scatter(x=epochs, y=history.get("val_loss", []), mode="lines+markers", name="Val Loss", line={"color": DANGER_COLOR})
    )
    fig.add_trace(
        go.Scatter(
            x=epochs,
            y=history.get("val_auc", []),
            mode="lines+markers",
            name="Val ROC-AUC",
            line={"color": SUCCESS_COLOR, "width": 2.5},
            yaxis="y2",
        )
    )

    fig.update_layout(
        yaxis2={
            "title": "Validation ROC-AUC",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
            "range": [0.5, 1.0],
            "tickfont": {"color": SUCCESS_COLOR},
            "title_font": {"color": SUCCESS_COLOR},
        }
    )
    fig.update_xaxes(title_text="Training Epoch")
    fig.update_yaxes(title_text="Binary Cross-Entropy Loss")
    return apply_space_theme(fig, "Dual-View CNN Training & Validation History")


def plot_roc_curves_comparison(
    baseline_fpr: list, baseline_tpr: list, baseline_auc: float,
    cnn_fpr: list, cnn_tpr: list, cnn_auc: float,
) -> go.Figure:
    """Plot test set ROC curves comparing Baseline and Two-View CNN."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=[0, 1], y=[0, 1], mode="lines",
            line={"dash": "dash", "color": TEXT_MUTED, "width": 1},
            name="Random Chance (AUC = 0.50)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=baseline_fpr, y=baseline_tpr, mode="lines",
            line={"color": WARNING_COLOR, "width": 2},
            name=f"Baseline HistGradientBoosting (AUC = {baseline_auc:.4f})",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=cnn_fpr, y=cnn_tpr, mode="lines",
            line={"color": ACCENT_PRIMARY, "width": 2.5},
            name=f"Two-View 1D CNN (AUC = {cnn_auc:.4f})",
        )
    )
    fig.update_xaxes(title_text="False Positive Rate (1 - Specificity)")
    fig.update_yaxes(title_text="True Positive Rate (Sensitivity / Recall)")
    return apply_space_theme(fig, "Receiver Operating Characteristic (ROC) Comparison")


def plot_pr_curves_comparison(
    baseline_rec: list, baseline_prec: list, baseline_ap: float,
    cnn_rec: list, cnn_prec: list, cnn_ap: float,
) -> go.Figure:
    """Plot test set Precision-Recall curves comparing Baseline and Two-View CNN."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=baseline_rec, y=baseline_prec, mode="lines",
            line={"color": WARNING_COLOR, "width": 2},
            name=f"Baseline HistGB (AvgPrec = {baseline_ap:.4f})",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=cnn_rec, y=cnn_prec, mode="lines",
            line={"color": SUCCESS_COLOR, "width": 2.5},
            name=f"Two-View CNN (AvgPrec = {cnn_ap:.4f})",
        )
    )
    fig.update_xaxes(title_text="Recall (Planet Recovery Rate)")
    fig.update_yaxes(title_text="Precision (Positive Predictive Value)")
    return apply_space_theme(fig, "Precision-Recall (PR) Curve Comparison")


def plot_confusion_matrix(cm_dict: Dict[str, int], title: str = "Confusion Matrix") -> go.Figure:
    """Plot 2x2 confusion matrix heatmap with scientific annotations."""
    tn = cm_dict.get("tn", 0)
    fp = cm_dict.get("fp", 0)
    fn = cm_dict.get("fn", 0)
    tp = cm_dict.get("tp", 0)

    z = [[tn, fp], [fn, tp]]
    labels = [
        [f"True Neg (TN)<br><b>{tn:,}</b>", f"False Pos (FP)<br><b>{fp:,}</b>"],
        [f"False Neg (FN)<br><b>{fn:,}</b>", f"True Pos (TP)<br><b>{tp:,}</b>"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=["Predicted Non-Planet", "Predicted Planet"],
            y=["Actual Non-Planet", "Actual Planet"],
            text=labels,
            texttemplate="%{text}",
            colorscale=[[0, CARD_COLOR], [0.5, "#253E6B"], [1, ACCENT_PRIMARY]],
            showscale=False,
        )
    )
    return apply_space_theme(fig, title, height=380)


def plot_dataset_distributions(df: pd.DataFrame) -> Dict[str, go.Figure]:
    """Generate astrophysical parameter distribution charts for command center and data explorer."""
    figs = {}

    # 1. Label distribution
    if "av_training_set" in df.columns:
        counts = df["av_training_set"].value_counts()
        fig_label = px.pie(
            values=counts.values,
            names=counts.index,
            color=counts.index,
            color_discrete_map={"PC": SUCCESS_COLOR, "AFP": DANGER_COLOR, "NTP": WARNING_COLOR, "UNK": TEXT_MUTED},
            hole=0.45,
        )
        fig_label.update_traces(textposition="inside", textinfo="percent+label")
        figs["label_distribution"] = apply_space_theme(fig_label, "NASA Kepler DR24 Label Distribution", height=350)

    # 2. Orbital Period distribution
    if "tce_period" in df.columns:
        fig_p = px.histogram(
            df[df["tce_period"] > 0],
            x="tce_period",
            color="av_training_set" if "av_training_set" in df.columns else None,
            log_x=True,
            nbins=50,
            color_discrete_map={"PC": SUCCESS_COLOR, "AFP": DANGER_COLOR, "NTP": WARNING_COLOR},
        )
        fig_p.update_xaxes(title_text="Orbital Period [Days, Log Scale]")
        fig_p.update_yaxes(title_text="Number of Candidates")
        figs["period_distribution"] = apply_space_theme(fig_p, "Orbital Period Distribution", height=350)

    # 3. Transit Duration distribution
    if "tce_duration" in df.columns:
        fig_d = px.histogram(
            df[df["tce_duration"] > 0],
            x="tce_duration",
            color="av_training_set" if "av_training_set" in df.columns else None,
            nbins=50,
            color_discrete_map={"PC": SUCCESS_COLOR, "AFP": DANGER_COLOR, "NTP": WARNING_COLOR},
        )
        fig_d.update_xaxes(title_text="Transit Duration [Hours]")
        fig_d.update_yaxes(title_text="Number of Candidates")
        figs["duration_distribution"] = apply_space_theme(fig_d, "Transit Duration Distribution", height=350)

    # 4. Transit Depth distribution
    if "tce_depth" in df.columns:
        fig_dp = px.histogram(
            df[df["tce_depth"] > 0],
            x="tce_depth",
            color="av_training_set" if "av_training_set" in df.columns else None,
            log_x=True,
            nbins=50,
            color_discrete_map={"PC": SUCCESS_COLOR, "AFP": DANGER_COLOR, "NTP": WARNING_COLOR},
        )
        fig_dp.update_xaxes(title_text="Transit Depth [ppm, Log Scale]")
        fig_dp.update_yaxes(title_text="Number of Candidates")
        figs["depth_distribution"] = apply_space_theme(fig_dp, "Transit Depth Distribution", height=350)

    return figs

