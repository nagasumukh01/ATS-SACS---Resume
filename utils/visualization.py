import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, List, Any

# Custom Color Palette
BG_COLOR = "#1E2235"
PRIMARY_COLOR = "#6C63FF"
SECONDARY_COLOR = "#00F2FE"
SUCCESS_COLOR = "#48BB78"
WARNING_COLOR = "#ED8936"
DANGER_COLOR = "#F56565"

def plot_sacs_gauge(score: float) -> go.Figure:
    """Renders a beautiful circular gauge chart representing the SACS score."""
    # Determine color based on score
    if score >= 75:
        color = SUCCESS_COLOR
    elif score >= 50:
        color = WARNING_COLOR
    else:
        color = DANGER_COLOR
        
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Semantic ATS Compatibility Score (SACS)", 'font': {'size': 20, 'color': '#FFFFFF', 'family': 'Outfit, sans-serif'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#A0AEC0"},
            'bar': {'color': color},
            'bgcolor': "rgba(255, 255, 255, 0.05)",
            'borderwidth': 2,
            'bordercolor': "rgba(255, 255, 255, 0.1)",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(245, 101, 101, 0.1)'},
                {'range': [50, 75], 'color': 'rgba(236, 137, 54, 0.1)'},
                {'range': [75, 100], 'color': 'rgba(72, 187, 120, 0.1)'}
            ],
            'threshold': {
                'line': {'color': "#FFFFFF", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFFFFF'},
        height=320,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig

def plot_radar_chart(component_scores: Dict[str, float]) -> go.Figure:
    """Renders a polar radar chart of the SACS scoring components."""
    categories = [c.replace('_', ' ').title() for c in component_scores.keys()]
    scores = list(component_scores.values())
    
    # Close the radar loop
    categories.append(categories[0])
    scores.append(scores[0])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        fillcolor='rgba(108, 99, 255, 0.25)',
        line=dict(color=PRIMARY_COLOR, width=2),
        marker=dict(color=SECONDARY_COLOR, size=6),
        name='Resume Profile'
    ))
    
    # Add a benchmark trace
    benchmark_scores = [80] * len(scores)
    fig.add_trace(go.Scatterpolar(
        r=benchmark_scores,
        theta=categories,
        line=dict(color='rgba(255,255,255,0.3)', width=1, dash='dash'),
        name='Ideal Target'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.1)",
                tickfont=dict(color="#A0AEC0")
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.1)",
                tickfont=dict(color="#FFFFFF", size=10)
            ),
            bgcolor="rgba(30, 34, 53, 0.4)"
        ),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(font=dict(color='#FFFFFF'), orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height=380,
        margin=dict(l=40, r=40, t=30, b=40)
    )
    return fig

def plot_feature_importance(importance: Dict[str, float]) -> go.Figure:
    """Renders a horizontal bar chart illustrating SACS component point contribution."""
    sorted_items = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    categories = [item[0].replace('_', ' ').title() for item in sorted_items]
    values = [item[1] for item in sorted_items]
    
    colors = [PRIMARY_COLOR if v > 5 else SECONDARY_COLOR for v in values]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker=dict(color=colors, line=dict(color='rgba(255,255,255,0.1)', width=1)),
        text=[f"+{v:.1f} pts" for v in values],
        textposition='outside',
        textfont=dict(color='#FFFFFF')
    ))
    
    fig.update_layout(
        title={'text': "SACS Score Contribution Breakdown", 'font': {'color': '#FFFFFF'}},
        xaxis=dict(title="Absolute Contribution Points (out of 100)", gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="#A0AEC0"), title_font=dict(color="#A0AEC0")),
        yaxis=dict(autorange="reversed", tickfont=dict(color="#FFFFFF")),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=380,
        margin=dict(l=20, r=60, t=40, b=20)
    )
    return fig

def plot_skill_network(
    tech_matches: Dict[str, Dict[str, Any]], 
    soft_matches: Dict[str, Dict[str, Any]]
) -> go.Figure:
    """
    Plots an interactive skill relationship network map using a 2D Scatter plot.
    Positions the target Job description in the center, and radiating links for skills,
    colored by match type.
    """
    skills = list(tech_matches.keys()) + list(soft_matches.keys())
    all_matches = {**tech_matches, **soft_matches}
    
    if not skills:
        # Fallback empty figure with note
        fig = go.Figure()
        fig.add_annotation(text="No skills found to visualize", showarrow=False, font=dict(color='#FFFFFF', size=16))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig

    # Center is at (0, 0)
    x_nodes = [0.0]
    y_nodes = [0.0]
    node_labels = ["Target Job Role"]
    node_colors = ["#FFFFFF"]
    node_sizes = [30]
    node_hovers = ["Target Job Requirement"]
    
    # Calculate angular layout positions for skill nodes
    num_skills = len(skills)
    angle_step = 2 * np.pi / num_skills if num_skills > 0 else 0
    
    edge_x = []
    edge_y = []
    
    for idx, skill in enumerate(skills):
        match = all_matches[skill]
        score = match["score"]
        match_type = match["match_type"]
        weight = match["weight"]
        
        # Radiate outward based on match score (closer is better match)
        radius = 1.8 - (score * 0.8) # matches range [1.0, 1.8]
        angle = idx * angle_step
        
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        
        x_nodes.append(x)
        y_nodes.append(y)
        node_labels.append(skill)
        
        # Color nodes by match type
        if match_type == "Exact":
            node_colors.append(SUCCESS_COLOR)
        elif match_type == "Semantic":
            node_colors.append(SECONDARY_COLOR)
        elif match_type == "Transferable":
            node_colors.append(WARNING_COLOR)
        else:
            node_colors.append(DANGER_COLOR)
            
        node_sizes.append(12 + int(weight * 8)) # Size by weight multiplier
        node_hovers.append(
            f"Skill: {skill}<br>Match Type: {match_type}<br>"
            f"Similarity: {int(score*100)}%<br>Matched with: {match['matched_with']}"
        )
        
        # Add links (edges) from center to skill
        edge_x.extend([0, x, None])
        edge_y.extend([0, y, None])
        
    fig = go.Figure()
    
    # Plot links
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color="rgba(255, 255, 255, 0.15)"),
        hoverinfo='none',
        mode='lines'
    ))
    
    # Plot nodes
    fig.add_trace(go.Scatter(
        x=x_nodes, y=y_nodes,
        mode='markers+text',
        marker=dict(
            color=node_colors,
            size=node_sizes,
            line=dict(color='rgba(0,0,0,0.5)', width=1.5)
        ),
        text=node_labels,
        textposition="bottom center",
        textfont=dict(color='#FFFFFF', size=10),
        hoverinfo='text',
        hovertext=node_hovers
    ))
    
    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig

def plot_skill_gap_heatmap(skills_report: Dict[str, Any]) -> go.Figure:
    """Renders a heatmap/bar chart of JD skills vs their SACS similarity scores."""
    tech_results = skills_report["tech"]
    soft_results = skills_report["soft"]
    
    all_results = {**tech_results, **soft_results}
    if not all_results:
        fig = go.Figure()
        fig.add_annotation(text="No skills found", showarrow=False, font=dict(color='#FFFFFF'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
        
    sorted_skills = sorted(all_results.items(), key=lambda x: x[1]["score"], reverse=True)
    skill_names = [item[0] for item in sorted_skills]
    scores = [item[1]["score"] * 100 for item in sorted_skills]
    match_types = [item[1]["match_type"] for item in sorted_skills]
    
    # Map colors
    colors = []
    for m in match_types:
        if m == "Exact":
            colors.append(SUCCESS_COLOR)
        elif m == "Semantic":
            colors.append(SECONDARY_COLOR)
        elif m == "Transferable":
            colors.append(WARNING_COLOR)
        else:
            colors.append(DANGER_COLOR)

    fig = go.Figure(go.Bar(
        x=scores,
        y=skill_names,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{s:.0f}% ({m})" for s, m in zip(scores, match_types)],
        textposition='inside',
        insidetextanchor='end',
        textfont=dict(color='#1E2235', weight='bold')
    ))
    
    fig.update_layout(
        xaxis=dict(title="Compatibility Similarity (%)", range=[0, 105], gridcolor="rgba(255,255,255,0.08)", tickfont=dict(color="#A0AEC0"), title_font=dict(color="#A0AEC0")),
        yaxis=dict(autorange="reversed", tickfont=dict(color="#FFFFFF")),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=min(600, 100 + len(skill_names)*30),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return fig
