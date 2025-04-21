import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from flask import Flask
import os

# ============================================================================
# DATA PREPARATION
# ============================================================================

# Load data
# Load data - adjust path for Render deployment
data_path = "sleep_health_cleaned_for_dashboard.csv"
if not os.path.exists(data_path):
    # If not in current directory, check if it's in a data folder
    data_path = os.path.join("data", "sleep_health_cleaned_for_dashboard.csv")

try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    # Create dummy data if file not found (for testing purposes)
    print("Warning: Data file not found. Creating sample data for testing.")
    # Generate sample data with relevant columns
    np.random.seed(42)
    n_samples = 200
    
    occupations = ['Software Engineer', 'Doctor', 'Nurse', 'Teacher', 'Accountant', 'Lawyer', 'Sales Representative']
    
    df = pd.DataFrame({
        'age': np.random.randint(18, 70, n_samples),
        'gender': np.random.choice(['Male', 'Female'], n_samples),
        'occupation': np.random.choice(occupations, n_samples),
        'sleep_duration': np.random.normal(7, 1.5, n_samples).clip(4, 10),
        'quality_of_sleep': np.random.randint(1, 11, n_samples),
        'stress_level': np.random.randint(1, 11, n_samples),
        'physical_activity_level': np.random.randint(10, 100, n_samples),
        'heart_rate': np.random.normal(70, 8, n_samples).clip(50, 95).astype(int),
        'daily_steps': np.random.randint(2000, 15000, n_samples),
        'sleep_disorder': np.random.choice(['None', 'Insomnia', 'Sleep Apnea'], n_samples, p=[0.7, 0.2, 0.1]),
        'bmi_category': np.random.choice(['Underweight', 'Normal', 'Overweight', 'Obese'], n_samples, p=[0.2, 0.5, 0.2, 0.1])
    })

# Create age groups for filtering
df['age_group'] = pd.cut(df['age'], bins=[0, 30, 40, 50, 60, 100], 
                         labels=['Under 30', '30-40', '40-50', '50-60', 'Over 60'])

# Define color themes
light_theme = {
    'background': '#f8fafc',
    'card': '#ffffff',
    'text': '#334155',
    'accent1': '#0072B2',  
    'accent2': '#009E73',    
    'accent3': '#CC79A7',  
    'accent4': '#E69F00',  
    'accent5': '#56B4E9',  
    'muted': '#94a3b8',
    'chart_colors': ["#0072B2", "#009E73", "#D55E00", "#CC79A7", "#F0E442", "#56B4E9"]
}

dark_theme = {
    'background': '#1e293b',
    'card': '#334155',
    'text': '#f1f5f9',
    'accent1': '#56B4E9',  
    'accent2': '#009E73',  
    'accent3': '#CC79A7',  
    'accent4': '#F0E442',  
    'accent5': '#D55E00',  
    'muted': '#cbd5e1',
    'chart_colors': ["#56B4E9", "#009E73", "#D55E00", "#CC79A7", "#F0E442", "#0072B2"]
}

current_theme = light_theme

# ============================================================================
# APP INITIALIZATION
# ============================================================================

# สร้าง Flask server ก่อน
from flask import Flask
server = Flask(__name__)

# จากนั้นเริ่มต้น Dash app
app = dash.Dash(
    __name__,
    server=server,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
app.title = "Sleep Health Analysis Dashboard"

# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

def create_card(title, value, icon, color, description=None):
    return html.Div([
        html.Div([
            html.Div([
                html.Span(icon, style={"fontSize": "1.5rem", "marginRight": "0.5rem"}),
                html.H3(title, style={"margin": "0", "fontSize": "1rem", "color": "var(--muted)"})
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div(value, 
                    style={"fontSize": "2rem", "fontWeight": "bold", "color": color, "margin": "0.5rem 0"}),
            html.P(description, style={"margin": "0", "fontSize": "0.8rem", "color": "var(--muted)"}) if description else None
        ], style={
            "backgroundColor": "var(--card)", 
            "borderRadius": "10px", 
            "padding": "1rem",
            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.05)",
            "height": "100%",
            "borderLeft": f"4px solid {color}"
        })
    ], className="three columns", style={"marginBottom": "1rem"})

def create_filter_section():
    return html.Div([
        html.Div([
            html.H3("Dashboard Filters", style={"color": "var(--text)", "marginTop": "0"}),
            html.Div([
                html.Div([
                    html.Label("Gender:", style={"fontWeight": "600", "color": "var(--text)"}),
                    dcc.Dropdown(
                        options=[{"label": "All Genders", "value": "All"}] + 
                               [{"label": g, "value": g} for g in df['gender'].unique()],
                        value="All",
                        id='gender-filter',
                        style={"width": "100%", "color": "#334155"}
                    ),
                ], className="three columns"),
                html.Div([
                    html.Label("Age Group:", style={"fontWeight": "600", "color": "var(--text)"}),
                    dcc.Dropdown(
                        options=[{"label": "All Ages", "value": "All"}] + 
                               [{"label": g, "value": g} for g in df['age_group'].unique()],
                        value="All",
                        id='age-filter',
                        style={"width": "100%", "color": "#334155"}
                    ),
                ], className="three columns"),
                html.Div([
                    html.Label("Occupation:", style={"fontWeight": "600", "color": "var(--text)"}),
                    dcc.Dropdown(
                        options=[{"label": "All Occupations", "value": "All"}] + 
                               [{"label": o, "value": o} for o in df['occupation'].unique()],
                        value="All",
                        id='occupation-filter',
                        style={"width": "100%", "color": "#334155"}
                    ),
                ], className="three columns"),
                html.Div([
                    html.Label("Sleep Disorder:", style={"fontWeight": "600", "color": "var(--text)"}),
                    dcc.Dropdown(
                        options=[{"label": "All", "value": "All"}] + 
                               [{"label": s, "value": s} for s in df['sleep_disorder'].unique()],
                        value="All",
                        id='disorder-filter',
                        style={"width": "100%", "color": "#334155"}
                    ),
                ], className="three columns"),
            ], className="row"),
        ], style={
            "backgroundColor": "var(--card)", 
            "borderRadius": "10px", 
            "padding": "1.5rem",
            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.05)",
            "marginBottom": "1.5rem"
        })
    ])

# ============================================================================
# APP LAYOUT
# ============================================================================

app.layout = html.Div(id="app-container", children=[
    # Theme toggle
    html.Div([
        html.Button(
            "🌙 Dark Mode", 
            id="theme-toggle", 
            style={
                "position": "absolute", 
                "top": "1rem", 
                "right": "1rem",
                "padding": "0.5rem 1rem",
                "borderRadius": "20px",
                "border": "none",
                "backgroundColor": "var(--accent1)",
                "color": "white",
                "cursor": "pointer"
            }
        )
    ]),
    
    # Header section
    html.Div([
        html.H1("Sleep Health Analysis Dashboard", 
                style={"color": "var(--accent1)", "marginBottom": "0.5rem"}),
        html.P("Analyze sleep patterns and their impact on overall health and wellness", 
               style={"color": "var(--muted)", "fontStyle": "italic"})
    ], style={"textAlign": "center", "marginBottom": "2rem", "paddingTop": "1rem"}),
    
    # Main content container
    html.Div([
        # Filters section
        create_filter_section(),
        
        # Dashboard Summary Cards
        html.Div([
            html.H2("Sleep Health Overview", style={"color": "var(--text)", "marginBottom": "1rem"}),
            html.Div([
                # Cards will be populated by callback
                html.Div(id="summary-cards", className="row"),
            ]),
        ], style={
            "backgroundColor": "var(--card)", 
            "borderRadius": "10px", 
            "padding": "1.5rem",
            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.05)",
            "marginBottom": "1.5rem"
        }),
        
        # Sleep Duration Section
        html.Div([
            html.Div([
                html.H2("Sleep Pattern Analysis", style={"color": "var(--text)", "marginBottom": "1rem"}),
                html.Div([
                    # Left column
                    html.Div([
                        dcc.Graph(id='histogram-duration'),
                    ], className="six columns"),
                    
                    # Right column
                    html.Div([
                        dcc.Graph(id='sleep-quality-by-duration'),
                    ], className="six columns"),
                ], className="row"),
            ], style={
                "backgroundColor": "var(--card)", 
                "borderRadius": "10px", 
                "padding": "1.5rem",
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.05)",
                "marginBottom": "1.5rem"
            }),
        ]),
        
        # Factors Affecting Sleep Section
        html.Div([
            html.Div([
                html.H2("Factors Affecting Sleep", style={"color": "var(--text)", "marginBottom": "1rem"}),
                
                # Tabs for different factors
                dcc.Tabs(id="factor-tabs", value="stress", children=[
                    dcc.Tab(label="Stress & Sleep", value="stress", style={"color": "var(--text)"}),
                    dcc.Tab(label="Physical Activity", value="activity", style={"color": "var(--text)"}),
                    dcc.Tab(label="BMI & Health", value="bmi", style={"color": "var(--text)"}),
                ], style={"color": "var(--text)"}, colors={
                    "border": "var(--accent1)",
                    "primary": "var(--accent1)",
                    "background": "var(--card)"
                }),
                
                html.Div(id="factor-content", style={"marginTop": "1rem"}),
            ], style={
                "backgroundColor": "var(--card)", 
                "borderRadius": "10px", 
                "padding": "1.5rem",
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.05)",
                "marginBottom": "1.5rem"
            }),
        ]),

        
        # Personalized Insights Section
        html.Div([
            html.Div([
                html.H2("Sleep Health Insights", style={"color": "var(--text)", "marginBottom": "1rem"}),
                html.Div(id="personalized-insights"),
            ], style={
                "backgroundColor": "var(--card)", 
                "borderRadius": "10px", 
                "padding": "1.5rem",
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.05)",
                "marginBottom": "1.5rem"
            }),
        ]),
        
    ], style={"maxWidth": "1400px", "margin": "0 auto", "padding": "1rem"}),
    
    # Store the current theme
    dcc.Store(id='theme-store', data='light'),
    
    # Footer
    html.Footer([
        html.P("Sleep Health Analysis Dashboard | Created with Dash & Plotly", 
              style={"textAlign": "center", "fontStyle": "italic", "color": "var(--muted)"}),
        html.P("Data updated: April 2025", 
              style={"textAlign": "center", "fontSize": "0.8rem", "color": "var(--muted)"})
    ], style={"padding": "1rem", "borderTop": "1px solid var(--muted)", "marginTop": "2rem"})
], style={
    "backgroundColor": "var(--background)",
    "color": "var(--text)",
    "minHeight": "100vh",
    "transition": "all 0.3s ease",
    "--background": light_theme["background"],
    "--card": light_theme["card"],
    "--text": light_theme["text"],
    "--accent1": light_theme["accent1"],
    "--accent2": light_theme["accent2"],
    "--accent3": light_theme["accent3"],
    "--accent4": light_theme["accent4"],
    "--accent5": light_theme["accent5"],
    "--muted": light_theme["muted"],
})

# ============================================================================
# CALLBACKS
# ============================================================================

# Toggle theme callback
@app.callback(
    [Output('app-container', 'style'),
     Output('theme-store', 'data'),
     Output('theme-toggle', 'children')],
    [Input('theme-toggle', 'n_clicks')],
    [State('theme-store', 'data')]
)
def toggle_theme(n_clicks, current):
    if n_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update
    
    if current == 'light':
        theme = dark_theme
        new_theme = 'dark'
        button_text = "☀️ Light Mode"
    else:
        theme = light_theme
        new_theme = 'light'
        button_text = "🌙 Dark Mode"
    
    return {
        "backgroundColor": theme["background"],
        "color": theme["text"],
        "minHeight": "100vh",
        "transition": "all 0.3s ease",
        "--background": theme["background"],
        "--card": theme["card"],
        "--text": theme["text"],
        "--accent1": theme["accent1"],
        "--accent2": theme["accent2"],
        "--accent3": theme["accent3"],
        "--accent4": theme["accent4"],
        "--accent5": theme["accent5"],
        "--muted": theme["muted"],
    }, new_theme, button_text

# Filter data callback
@app.callback(
    Output('summary-cards', 'children'),
    [Input('gender-filter', 'value'),
     Input('age-filter', 'value'),
     Input('occupation-filter', 'value'),
     Input('disorder-filter', 'value'),
     Input('theme-store', 'data')]
)
def update_summary_cards(gender, age_group, occupation, disorder, theme):
    # Select theme colors
    theme_colors = dark_theme if theme == 'dark' else light_theme
    
    # Filter data
    filtered_df = df.copy()
    if gender != "All":
        filtered_df = filtered_df[filtered_df['gender'] == gender]
    if age_group != "All":
        filtered_df = filtered_df[filtered_df['age_group'] == age_group]
    if occupation != "All":
        filtered_df = filtered_df[filtered_df['occupation'] == occupation]
    if disorder != "All":
        filtered_df = filtered_df[filtered_df['sleep_disorder'] == disorder]
    
    # Calculate metrics
    avg_sleep = filtered_df['sleep_duration'].mean()
    avg_quality = filtered_df['quality_of_sleep'].mean()
    avg_stress = filtered_df['stress_level'].mean()
    avg_activity = filtered_df['physical_activity_level'].mean()
    
    # Create summary cards
    cards = [
        create_card("Average Sleep Duration", f"{avg_sleep:.1f} hrs", "😴", theme_colors["accent1"], 
                   "Recommended: 7-9 hours"),
        create_card("Average Sleep Quality", f"{avg_quality:.1f}/10", "✨", theme_colors["accent2"], 
                   "Higher is better"),
        create_card("Average Stress Level", f"{avg_stress:.1f}/10", "😓", theme_colors["accent4"], 
                   "Lower is better"),
        create_card("Physical Activity", f"{avg_activity:.0f}/100", "🏃", theme_colors["accent3"], 
                   "Aim for >60")
    ]
    
    return cards

# Update histogram callback
@app.callback(
    [Output('histogram-duration', 'figure'),
     Output('sleep-quality-by-duration', 'figure')],
    [Input('gender-filter', 'value'),
     Input('age-filter', 'value'),
     Input('occupation-filter', 'value'),
     Input('disorder-filter', 'value'),
     Input('theme-store', 'data')]
)
def update_sleep_patterns(gender, age_group, occupation, disorder, theme):
    # Select theme colors
    theme_colors = dark_theme if theme == 'dark' else light_theme
    bg_color = theme_colors["background"]
    text_color = theme_colors["text"]
    
    # Filter data
    filtered_df = df.copy()
    if gender != "All":
        filtered_df = filtered_df[filtered_df['gender'] == gender]
    if age_group != "All":
        filtered_df = filtered_df[filtered_df['age_group'] == age_group]
    if occupation != "All":
        filtered_df = filtered_df[filtered_df['occupation'] == occupation]
    if disorder != "All":
        filtered_df = filtered_df[filtered_df['sleep_disorder'] == disorder]
    
    # Create histogram
    fig1 = px.histogram(
        filtered_df, 
        x='sleep_duration', 
        nbins=20,
        color_discrete_sequence=[theme_colors["accent1"]],
        opacity=0.7,
        labels={'sleep_duration': 'Sleep Duration (hours)'}
    )
    
    # Add reference zones for healthy sleep
    fig1.add_vrect(
        x0=7, x1=9,
        fillcolor=theme_colors["accent2"], opacity=0.15,
        layer="below", line_width=0,
        annotation_text="Recommended Sleep Range",
        annotation_position="top right"
    )
    
    # Update layout
    fig1.update_layout(
        title="Sleep Duration Distribution",
        template="plotly_dark" if theme == 'dark' else "plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor=theme_colors["card"],
        paper_bgcolor=theme_colors["card"],
        font=dict(color=text_color),
        height=350
    )
    
    # Create quality by duration scatter
    fig2 = px.scatter(
        filtered_df,
        x='sleep_duration',
        y='quality_of_sleep',
        color='gender',
        size='physical_activity_level',
        color_discrete_sequence=theme_colors["chart_colors"],
        labels={
            'sleep_duration': 'Sleep Duration (hours)',
            'quality_of_sleep': 'Sleep Quality (1-10)',
            'physical_activity_level': 'Activity Level'
        },
        opacity=0.8
    )
    
    # Update layout
    fig2.update_layout(
        title="Sleep Quality vs. Duration",
        template="plotly_dark" if theme == 'dark' else "plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor=theme_colors["card"],
        paper_bgcolor=theme_colors["card"],
        font=dict(color=text_color),
        height=350
    )
    
    return fig1, fig2

# Update factors tab content
@app.callback(
    Output('factor-content', 'children'),
    [Input('factor-tabs', 'value'),
     Input('gender-filter', 'value'),
     Input('age-filter', 'value'),
     Input('occupation-filter', 'value'),
     Input('disorder-filter', 'value'),
     Input('theme-store', 'data')]
)
def update_factor_content(tab, gender, age_group, occupation, disorder, theme):
    # Select theme colors
    theme_colors = dark_theme if theme == 'dark' else light_theme
    bg_color = theme_colors["background"]
    text_color = theme_colors["text"]
    
    # Filter data
    filtered_df = df.copy()
    if gender != "All":
        filtered_df = filtered_df[filtered_df['gender'] == gender]
    if age_group != "All":
        filtered_df = filtered_df[filtered_df['age_group'] == age_group]
    if occupation != "All":
        filtered_df = filtered_df[filtered_df['occupation'] == occupation]
    if disorder != "All":
        filtered_df = filtered_df[filtered_df['sleep_disorder'] == disorder]
    
    template = "plotly_dark" if theme == 'dark' else "plotly_white"
    
    if tab == "stress":
        # Create stress scatter plot
        fig = px.scatter(
            filtered_df, 
            x='stress_level', 
            y='sleep_duration',
            color='quality_of_sleep',
            color_continuous_scale=[theme_colors["accent4"], theme_colors["accent5"], theme_colors["accent2"]],
            labels={
                'stress_level': 'Stress Level (1-10)',
                'sleep_duration': 'Sleep Duration (hours)',
                'quality_of_sleep': 'Sleep Quality'
            },
            height=450
        )
        
        # Add stress level zones
        fig.add_hrect(
            y0=7, y1=9,
            fillcolor=theme_colors["accent2"], opacity=0.15,
            layer="below", line_width=0,
        )
        
        fig.update_layout(
            template=template,
            plot_bgcolor=theme_colors["card"],
            paper_bgcolor=theme_colors["card"],
            font=dict(color=text_color),
        )
        
        content = html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig),
                ], className="eight columns"),
                html.Div([
                    html.H3("Stress Management Tips", style={"color": theme_colors["accent1"]}),
                    html.Div([
                        html.Div([
                            html.H4("Deep Breathing", style={"color": text_color}),
                            html.P("Take 5 deep breaths before bed to activate your parasympathetic nervous system.")
                        ], style={"marginBottom": "1rem"}),
                        html.Div([
                            html.H4("Digital Detox", style={"color": text_color}),
                            html.P("Avoid screens 1 hour before bedtime to reduce stress and improve sleep quality.")
                        ], style={"marginBottom": "1rem"}),
                        html.Div([
                            html.H4("Meditation", style={"color": text_color}),
                            html.P("Regular meditation practice can lower baseline stress levels and improve sleep.")
                        ]),
                    ], style={"backgroundColor": bg_color, "padding": "1rem", "borderRadius": "8px"})
                ], className="four columns"),
            ], className="row")
        ])
        
    elif tab == "activity":
        # Create physical activity scatter plot
        fig = px.scatter(
            filtered_df, 
            x='daily_steps', 
            y='sleep_duration',
            size='physical_activity_level',
            color='heart_rate',
            color_continuous_scale=[theme_colors["accent2"], theme_colors["accent5"], theme_colors["accent4"]],
            labels={
                'daily_steps': 'Daily Steps',
                'sleep_duration': 'Sleep Duration (hours)',
                'physical_activity_level': 'Activity Level',
                'heart_rate': 'Heart Rate (bpm)'
            },
            height=450
        )
        
        # Add reference line for recommended steps
        fig.add_vline(
            x=10000, line_width=2, line_dash="dash", line_color=theme_colors["accent1"],
            annotation_text="10,000 steps goal", annotation_position="top right"
        )
        
        fig.update_layout(
            template=template,
            plot_bgcolor=theme_colors["card"],
            paper_bgcolor=theme_colors["card"],
            font=dict(color=text_color),
        )
        
        content = html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig),
                ], className="eight columns"),
                html.Div([
                    html.H3("Activity Recommendations", style={"color": theme_colors["accent1"]}),
                    html.Div([
                        html.Div([
                            html.H4("Timing Matters", style={"color": text_color}),
                            html.P("Exercise earlier in the day for better sleep. Avoid vigorous activity 2-3 hours before bed.")
                        ], style={"marginBottom": "1rem"}),
                        html.Div([
                            html.H4("Step Goal", style={"color": text_color}),
                            html.P("Aim for 7,000-10,000 steps daily for improved sleep quality and overall health.")
                        ], style={"marginBottom": "1rem"}),
                        html.Div([
                            html.H4("Consistency", style={"color": text_color}),
                            html.P("Regular moderate exercise is better for sleep than occasional intense workouts.")
                        ]),
                    ], style={"backgroundColor": bg_color, "padding": "1rem", "borderRadius": "8px"})
                ], className="four columns"),
            ], className="row")
        ])
        
    else:  # BMI tab
        # Create two plots for BMI section

        filtered_df['bmi_category'] = filtered_df['bmi_category'].replace({
        'Normal': 'Underweight',
        'Normal Weight': 'Normal'
        })

        fig1 = px.box(
        filtered_df, 
        x='bmi_category', 
        y='sleep_duration', 
        color='bmi_category',
        color_discrete_sequence=theme_colors["chart_colors"],
        category_orders={"bmi_category": ["Obese", "Overweight", "Normal", "Underweight"]},
        labels={'sleep_duration': 'Sleep Duration (hours)', 'bmi_category': 'BMI Category'},
        height=350
        )
        
        fig1.update_layout(
            title="Sleep Duration by BMI Category",
            template=template,
            plot_bgcolor=theme_colors["card"],
            paper_bgcolor=theme_colors["card"],
            font=dict(color=text_color),
            showlegend=False
        )
        
        fig2 = px.scatter(
            filtered_df,
            x='bmi_category',
            y='quality_of_sleep',
            color='bmi_category',
            size='physical_activity_level',
            color_discrete_sequence=theme_colors["chart_colors"],
            category_orders={"bmi_category": ["Obese", "Overweight", "Normal", "Underweight"]},
            labels={'quality_of_sleep': 'Sleep Quality (1-10)', 'bmi_category': 'BMI Category'},
            height=350
        )
        
        fig2.update_layout(
            title="Sleep Quality by BMI Category",
            template=template,
            plot_bgcolor=theme_colors["card"],
            paper_bgcolor=theme_colors["card"],
            font=dict(color=text_color),
            showlegend=False
        )
        
        content = html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig1),
                ], className="six columns"),
                html.Div([
                    dcc.Graph(figure=fig2),
                ], className="six columns"),
            ], className="row"),
            html.Div([
                html.H3("BMI Impact on Sleep", style={"color": theme_colors["accent1"], "marginTop": "1rem"}),
                html.P([
                    "BMI categories can significantly impact sleep quality and duration. ",
                    "Those with higher BMI values often experience sleep apnea and other disorders. ",
                    "Maintaining a healthy weight through balanced diet and regular exercise can improve sleep patterns."
                ], style={"color": text_color})
            ])
        ])
    
    return content

# Trend analysis callback
@app.callback(
    [Output('age-trend-graph', 'figure'),
     Output('occupation-analysis', 'figure')],
    [Input('gender-filter', 'value'),
     Input('age-filter', 'value'),
     Input('occupation-filter', 'value'),
     Input('disorder-filter', 'value'),
     Input('theme-store', 'data')]
)
def update_trend_analysis(gender, age_group, occupation, disorder, theme):
    # Select theme colors
    theme_colors = dark_theme if theme == 'dark' else light_theme
    text_color = theme_colors["text"]
    
    # Filter data
    filtered_df = df.copy()
    if gender != "All":
        filtered_df = filtered_df[filtered_df['gender'] == gender]
    if age_group != "All":
        filtered_df = filtered_df[filtered_df['age_group'] == age_group]
    if occupation != "All":
        filtered_df = filtered_df[filtered_df['occupation'] == occupation]
    if disorder != "All":
        filtered_df = filtered_df[filtered_df['sleep_disorder'] == disorder]
    
    template = "plotly_dark" if theme == 'dark' else "plotly_white"
    
    # Age trend analysis
    age_analysis = filtered_df.groupby('age').agg({
        'sleep_duration': 'mean',
        'quality_of_sleep': 'mean',
        'stress_level': 'mean'
    }).reset_index()
    
    # Create age trend figure
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=age_analysis['age'],
        y=age_analysis['sleep_duration'],
        mode='lines+markers',
        name='Sleep Duration',
        line=dict(color=theme_colors["accent1"], width=3),
        marker=dict(size=8)
    ))
    
    fig1.add_trace(go.Scatter(
        x=age_analysis['age'],
        y=age_analysis['quality_of_sleep'],
        mode='lines+markers',
        name='Sleep Quality',
        line=dict(color=theme_colors["accent2"], width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    # Create layout with secondary y-axis
    fig1.update_layout(
        yaxis=dict(
            title="Sleep Duration (hours)",
            titlefont=dict(color=theme_colors["accent1"]),
            tickfont=dict(color=theme_colors["accent1"])
        ),
        yaxis2=dict(
            title="Sleep Quality (1-10)",
            titlefont=dict(color=theme_colors["accent2"]),
            tickfont=dict(color=theme_colors["accent2"]),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        xaxis=dict(title="Age"),
        template=template,
        plot_bgcolor=theme_colors["card"],
        paper_bgcolor=theme_colors["card"],
        font=dict(color=text_color),
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=40, r=40, t=20, b=40),
        height=400
    )
    
    # Occupation analysis
    if len(filtered_df['occupation'].unique()) > 1:
        occupation_analysis = filtered_df.groupby('occupation').agg({
            'quality_of_sleep': 'mean',
            'stress_level': 'mean',
            'sleep_duration': 'mean'
        }).reset_index()
        
        occupation_analysis = occupation_analysis.sort_values('quality_of_sleep', ascending=False)
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            x=occupation_analysis['occupation'],
            y=occupation_analysis['quality_of_sleep'],
            name='Sleep Quality',
            marker_color=theme_colors["accent2"]
        ))
        
        fig2.add_trace(go.Bar(
            x=occupation_analysis['occupation'],
            y=occupation_analysis['stress_level'],
            name='Stress Level',
            marker_color=theme_colors["accent4"]
        ))
    else:
        # If only one occupation is selected, show comparison with average
        selected_occupation = filtered_df['occupation'].iloc[0]
        
        # Get the overall dataset averages
        overall_avg_quality = df['quality_of_sleep'].mean()
        overall_avg_stress = df['stress_level'].mean()
        
        # Get averages for selected occupation
        selected_avg_quality = filtered_df['quality_of_sleep'].mean()
        selected_avg_stress = filtered_df['stress_level'].mean()
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            x=['Selected', 'Overall Average'],
            y=[selected_avg_quality, overall_avg_quality],
            name='Sleep Quality',
            marker_color=theme_colors["accent2"]
        ))
        
        fig2.add_trace(go.Bar(
            x=['Selected', 'Overall Average'],
            y=[selected_avg_stress, overall_avg_stress],
            name='Stress Level',
            marker_color=theme_colors["accent4"]
        ))
    
    fig2.update_layout(
        barmode='group',
        title=f"{'Sleep Quality & Stress by Occupation' if len(filtered_df['occupation'].unique()) > 1 else f'Comparing {selected_occupation} with Average'}",
        template=template,
        plot_bgcolor=theme_colors["card"],
        paper_bgcolor=theme_colors["card"],
        font=dict(color=text_color),
        margin=dict(l=40, r=40, t=60, b=90),
        height=400
    )
    
    # Rotate x-axis labels if needed
    if len(filtered_df['occupation'].unique()) > 3:
        fig2.update_layout(
            xaxis=dict(
                tickangle=45,
            )
        )
    
    return fig1, fig2

# Personalized insights callback
@app.callback(
    Output('personalized-insights', 'children'),
    [Input('gender-filter', 'value'),
     Input('age-filter', 'value'),
     Input('occupation-filter', 'value'),
     Input('disorder-filter', 'value'),
     Input('theme-store', 'data')]
)
def update_personalized_insights(gender, age_group, occupation, disorder, theme):
    # Select theme colors
    theme_colors = dark_theme if theme == 'dark' else light_theme
    bg_color = theme_colors["background"]
    text_color = theme_colors["text"]
    
    # Filter data
    filtered_df = df.copy()
    if gender != "All":
        filtered_df = filtered_df[filtered_df['gender'] == gender]
    if age_group != "All":
        filtered_df = filtered_df[filtered_df['age_group'] == age_group]
    if occupation != "All":
        filtered_df = filtered_df[filtered_df['occupation'] == occupation]
    if disorder != "All":
        filtered_df = filtered_df[filtered_df['sleep_disorder'] == disorder]
    
    # Calculate key metrics
    avg_sleep = filtered_df['sleep_duration'].mean()
    avg_quality = filtered_df['quality_of_sleep'].mean()
    sleep_disorders_pct = (filtered_df['sleep_disorder'] != 'None').mean() * 100
    high_stress_pct = (filtered_df['stress_level'] > 7).mean() * 100
    low_activity_pct = (filtered_df['physical_activity_level'] < 50).mean() * 100
    
    # Generate insights
    insights = []
    
    # Sleep duration insights
    if avg_sleep < 6:
        insights.append(html.Div([
            html.H4("⚠️ Sleep Duration Alert", style={"color": theme_colors["accent4"]}),
            html.P(f"The average sleep duration is {avg_sleep:.1f} hours, which is significantly below the recommended 7-9 hours. This can lead to increased stress, reduced cognitive function, and various health issues."),
            html.P("Recommendation: Prioritize sleep by setting a consistent bedtime routine and creating a sleep-friendly environment.")
        ], style={"marginBottom": "1rem"}))
    elif avg_sleep < 7:
        insights.append(html.Div([
            html.H4("⚠️ Sleep Duration Concern", style={"color": theme_colors["accent5"]}),
            html.P(f"The average sleep duration is {avg_sleep:.1f} hours, slightly below the recommended range of 7-9 hours."),
            html.P("Recommendation: Try to add an extra 30-60 minutes to your sleep schedule, especially if you're feeling tired during the day.")
        ], style={"marginBottom": "1rem"}))
    else:
        insights.append(html.Div([
            html.H4("✅ Healthy Sleep Duration", style={"color": theme_colors["accent2"]}),
            html.P(f"The average sleep duration is {avg_sleep:.1f} hours, which falls within the recommended 7-9 hour range."),
            html.P("Recommendation: Maintain your current sleep schedule and focus on sleep quality improvements if needed.")
        ], style={"marginBottom": "1rem"}))
    
    # Sleep quality insights
    if avg_quality < 5:
        insights.append(html.Div([
            html.H4("⚠️ Poor Sleep Quality", style={"color": theme_colors["accent4"]}),
            html.P(f"The average sleep quality rating is {avg_quality:.1f}/10, indicating significant sleep quality issues."),
            html.P("Recommendation: Evaluate your sleep environment, reduce screen time before bed, and consider consulting a healthcare provider.")
        ], style={"marginBottom": "1rem"}))
    elif avg_quality < 7:
        insights.append(html.Div([
            html.H4("⚠️ Moderate Sleep Quality", style={"color": theme_colors["accent5"]}),
            html.P(f"The average sleep quality rating is {avg_quality:.1f}/10, indicating room for improvement."),
            html.P("Recommendation: Try techniques like meditation before bed, temperature regulation, and noise reduction.")
        ], style={"marginBottom": "1rem"}))
    else:
        insights.append(html.Div([
            html.H4("✅ Good Sleep Quality", style={"color": theme_colors["accent2"]}),
            html.P(f"The average sleep quality rating is {avg_quality:.1f}/10, indicating generally good sleep quality."),
            html.P("Recommendation: Continue your healthy bedtime habits and share them with others who may be struggling.")
        ], style={"marginBottom": "1rem"}))
    
    # Other factors insights
    if high_stress_pct > 50:
        insights.append(html.Div([
            html.H4("⚠️ High Stress Levels", style={"color": theme_colors["accent4"]}),
            html.P(f"{high_stress_pct:.1f}% of individuals in this group report high stress levels (>7/10)."),
            html.P("Recommendation: Incorporate stress management techniques like deep breathing, mindfulness, and regular exercise.")
        ], style={"marginBottom": "1rem"}))
    
    if low_activity_pct > 60:
        insights.append(html.Div([
            html.H4("⚠️ Low Physical Activity", style={"color": theme_colors["accent5"]}),
            html.P(f"{low_activity_pct:.1f}% of individuals in this group have lower than recommended physical activity levels."),
            html.P("Recommendation: Aim for at least 30 minutes of moderate exercise daily, which has been shown to improve sleep quality.")
        ], style={"marginBottom": "1rem"}))
    
    if sleep_disorders_pct > 30:
        insights.append(html.Div([
            html.H4("⚠️ Sleep Disorders Present", style={"color": theme_colors["accent4"]}),
            html.P(f"{sleep_disorders_pct:.1f}% of individuals in this group have a diagnosed sleep disorder."),
            html.P("Recommendation: If you experience persistent sleep problems, consider consulting a sleep specialist for proper diagnosis and treatment.")
        ], style={"marginBottom": "1rem"}))
    
    # Key sleep factors
    top_factors = html.Div([
        html.H3("Key Factors for Better Sleep", style={"color": theme_colors["accent1"], "marginTop": "1.5rem"}),
        html.Div([
            html.Div([
                html.Div([
                    html.H4("1. Consistent Schedule", style={"color": text_color}),
                    html.P("Go to bed and wake up at the same time every day, even on weekends.")
                ], style={"marginBottom": "1rem"}),
                html.Div([
                    html.H4("2. Sleep Environment", style={"color": text_color}),
                    html.P("Keep your bedroom dark, quiet, and cool (around 65°F or 18°C).")
                ], style={"marginBottom": "1rem"}),
            ], className="six columns"),
            html.Div([
                html.Div([
                    html.H4("3. Limit Screen Time", style={"color": text_color}),
                    html.P("Avoid screens for at least one hour before bedtime.")
                ], style={"marginBottom": "1rem"}),
                html.Div([
                    html.H4("4. Watch Diet & Exercise", style={"color": text_color}),
                    html.P("Avoid large meals, caffeine, and alcohol before bed. Exercise regularly but not too close to bedtime.")
                ])
            ], className="six columns"),
        ], className="row", style={"backgroundColor": bg_color, "padding": "1rem", "borderRadius": "8px"})
    ])
    
    return html.Div(insights + [top_factors])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run_server(host='0.0.0.0', port=port, debug=False)