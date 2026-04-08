"""Chart builders for match visualizations."""
import plotly.graph_objects as go


def match_radar_chart(scores: dict, title: str = "") -> go.Figure:
    """Create a radar chart showing match score breakdown."""
    categories = ["Embedding", "Audience", "Budget", "Values"]
    values = [
        scores.get("embedding_score", 0),
        scores.get("audience_score", 0),
        scores.get("budget_score", 0),
        scores.get("values_score", 0),
    ]
    values.append(values[0])  # close the polygon
    categories.append(categories[0])

    fig = go.Figure(data=go.Scatterpolar(
        r=values, theta=categories, fill="toself",
        name="Match Scores",
        line_color="#6366f1",
        fillcolor="rgba(99, 102, 241, 0.3)",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        title=title,
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def score_bar_chart(matches: list[dict]) -> go.Figure:
    """Create a horizontal bar chart of match scores."""
    names = [m.get("partner_name", m.get("id", "")[:8]) for m in matches]
    scores = [m.get("weighted_score", 0) for m in matches]

    fig = go.Figure(go.Bar(
        x=scores, y=names, orientation="h",
        marker_color="#6366f1",
        text=[f"{s:.1%}" for s in scores],
        textposition="auto",
    ))
    fig.update_layout(
        title="Match Rankings",
        xaxis_title="Weighted Score",
        yaxis=dict(autorange="reversed"),
        height=max(200, len(matches) * 50),
        margin=dict(l=120, r=20, t=50, b=40),
    )
    return fig


def audience_gauge(score: float, threshold: float = 0.35) -> go.Figure:
    """Create a gauge chart for audience acceptance score."""
    color = "#22c55e" if score >= threshold else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "", "valueformat": ".2f"},
        gauge=dict(
            axis=dict(range=[0, 1]),
            bar=dict(color=color),
            threshold=dict(line=dict(color="orange", width=3), thickness=0.8, value=threshold),
            steps=[
                dict(range=[0, 0.3], color="#fee2e2"),
                dict(range=[0.3, 0.5], color="#fef9c3"),
                dict(range=[0.5, 0.7], color="#dcfce7"),
                dict(range=[0.7, 1.0], color="#bbf7d0"),
            ],
        ),
        title=dict(text="Audience Score"),
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig
