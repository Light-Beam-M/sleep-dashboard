import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os

# ============================================================================
# DATA PREPARATION
# ============================================================================

# Create sample data if the CSV doesn't exist
try:
    df = pd.read_csv("sleep_health_cleaned_for_dashboard.csv")
except FileNotFoundError:
    # Create a sample dataframe with random data
    import numpy as np
    np.random.seed(42)
    
    # Create sample data
    n_samples = 500
    genders = ['Male', 'Female', 'Non-binary']
    bmi_categories = ['Underweight', 'Normal', 'Overweight', 'Obese']
    sleep_disorders = ['None', 'Insomnia', 'Sleep Apnea']
    
    df = pd.DataFrame({
        'gender': np.random.choice(genders, n_samples),
        'age': np.random.randint(18, 80, n_samples),
        'sleep_duration': np.random.normal(7, 1.5, n_samples).clip(3, 12),
        'quality_of_sleep': np.random.randint(1, 11, n_samples),
        'physical_activity_level': np.random.randint(10, 100, n_samples),
        'stress_level': np.random.randint(1, 11, n_samples),
        'bmi_category': np.random.choice(bmi_categories, n_samples),
        'heart_rate': np.random.randint(60, 100, n_samples),
        'daily_steps': np.random.randint(2000, 20000, n_samples),
        'sleep_disorder': np.random.choice(sleep_disorders, n_samples),
    })
    
    # Add correlation effects
    df.loc[df['stress_level'] > 7, 'sleep_duration'] *= 0.8
    df.loc[df['physical_activity_level'] > 70, 'sleep_duration'] *= 1.1
    df.loc[df['sleep_disorder'] == 'Insomnia', 'sleep_duration'] *= 0.7
    df.loc[df['sleep_disorder'] == 'Sleep Apnea', 'sleep_duration'] *= 0.8
    df.loc[df['daily_steps'] > 12000, 'quality_of_sleep'] += 1
    
    # Ensure values are within realistic ranges
    df['sleep_duration'] = df['sleep_duration'].clip(3, 12)
    df['quality_of_sleep'] = df['quality_of_sleep'].clip(1, 10)
    
    # Save the dataframe to a CSV file
    df.to_csv("sleep_health_cleaned_for_dashboard.csv", index=False)

# Colorblind-friendly color palette with health-themed colors
colors = ["#3498db", "#2ecc71", "#9b59b6", "#e74c3c", "#f39c12", "#1abc9c"]

# ============================================================================
# APP INITIALIZATION
# ============================================================================

# Initialize the app with custom styling
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
app.title = "Sleep Health Analysis Dashboard"

# This is needed for Gunicorn to find the server
server = app.server

# Define reusable styles
CONTENT_STYLE = {
    "max-width": "1400px",
    "margin": "0 auto",
    "padding": "1rem",
}

CARD_STYLE = {
    "background-color": "#ffffff",
    "border-radius": "10px",
    "padding": "1.5rem",
    "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
    "margin-bottom": "1.5rem",
    "border-left": "5px solid #3498db",
}

HEADER_STYLE = {
    "textAlign": "center",
    "color": "#2c3e50",
    "margin-bottom": "1.5rem",
    "padding-bottom": "1rem",
    "border-bottom": "3px solid #3498db"
}

INFO_BOX_STYLE = {
    "background-color": "#f8f9fa",
    "border-radius": "8px",
    "padding": "1rem",
    "border-left": "4px solid #2ecc71",
    "margin-top": "1rem",
    "font-size": "0.9rem",
}

# ============================================================================
# APP LAYOUT
# ============================================================================

app.layout = html.Div([
    # Header section with health-themed design
    html.Div([
        html.Div([
            html.H1("Sleep Health Analysis", style={"display": "inline-block"})
        ], style={"display": "flex", "alignItems": "center", "justifyContent": "center"}),
        
        html.P("Analyze sleep patterns and their impact on overall health and wellness", 
               style={"textAlign": "center", "font-style": "italic", "color": "#7f8c8d"})
    ], style={"textAlign": "center", "margin-bottom": "2rem"}),
    
    # Filters section
    html.Div([
        html.Label("Filter Dashboard by Gender:", style={"font-weight": "600", "color": "#2c3e50"}),
        dcc.Dropdown(
            options=[{"label": "All Genders", "value": "All"}] + 
                   [{"label": g, "value": g} for g in df['gender'].unique()],
            value="All",
            id='gender-filter',
            placeholder="Select Gender",
            multi=False,
            style={"width": "100%", "border-radius": "5px"}
        ),
    ], style={"width": "300px", "margin": "1rem auto", "padding": "1rem", 
              "background-color": "#ffffff", "border-radius": "10px", 
              "box-shadow": "0 2px 8px rgba(0, 0, 0, 0.1)"}),
    
    # Main content area
    html.Div([
        # Sleep Duration Overview Section
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H2("Sleep Duration Overview", 
                               style={"color": "#3498db", "margin-bottom": "0.8rem"}),
                        html.Div([
                            html.Span("ℹ️", style={"font-size": "1.2rem", "margin-right": "0.5rem"}),
                            html.Span("Understanding your sleep patterns")
                        ], style={"color": "#7f8c8d", "font-size": "0.9rem"})
                    ]),
                    dcc.Graph(id='histogram-duration'),
                    html.Div([
                        html.P([
                            html.Strong("What this shows: "),
                            "This histogram displays the distribution of sleep duration across the dataset. " 
                            "Most health experts recommend adults get 7-9 hours of sleep per night for optimal health."
                        ])
                    ], style=INFO_BOX_STYLE)
                ], style=CARD_STYLE, className="twelve columns")
            ], className="row"),
        ]),
        
        # Two-column layout for charts
        html.Div([
            # Left column
            html.Div([
                # Stress vs Sleep Duration
                html.Div([
                    html.Div([
                        html.H2("Stress & Sleep", 
                               style={"color": "#e74c3c", "margin-bottom": "0.8rem"}),
                        html.Div([
                            html.Span("😴", style={"font-size": "1.2rem", "margin-right": "0.5rem"}),
                            html.Span("Impact of stress on sleep quality")
                        ], style={"color": "#7f8c8d", "font-size": "0.9rem"})
                    ]),
                    dcc.Graph(id='scatter-stress'),
                    html.Div([
                        html.P([
                            html.Strong("What this shows: "),
                            "This scatter plot reveals the relationship between stress levels and sleep duration. "
                            "Color indicates sleep quality, showing how higher stress typically correlates with reduced sleep quality and duration."
                        ])
                    ], style=INFO_BOX_STYLE)
                ], style={**CARD_STYLE, "border-left": "5px solid #e74c3c"}),
                
                # Sleep by Gender
                html.Div([
                    html.Div([
                        html.H2("Sleep Patterns by Gender", 
                               style={"color": "#9b59b6", "margin-bottom": "0.8rem"}),
                        html.Div([
                            html.Span("👫", style={"font-size": "1.2rem", "margin-right": "0.5rem"}),
                            html.Span("How gender affects sleep duration")
                        ], style={"color": "#7f8c8d", "font-size": "0.9rem"})
                    ]),
                    dcc.Graph(id='box-gender'),
                    html.Div([
                        html.P([
                            html.Strong("What this shows: "),
                            "This box plot compares sleep duration across different genders. "
                            "Research suggests biological and social factors can influence sleep patterns between genders."
                        ])
                    ], style=INFO_BOX_STYLE)
                ], style={**CARD_STYLE, "border-left": "5px solid #9b59b6"}),
            ], className="six columns"),
            
            # Right column
            html.Div([
                # Steps vs Sleep Duration
                html.Div([
                    html.Div([
                        html.H2("Physical Activity & Sleep", 
                               style={"color": "#2ecc71", "margin-bottom": "0.8rem"}),
                        html.Div([
                            html.Span("🏃", style={"font-size": "1.2rem", "margin-right": "0.5rem"}),
                            html.Span("How daily movement affects sleep")
                        ], style={"color": "#7f8c8d", "font-size": "0.9rem"})
                    ]),
                    dcc.Graph(id='scatter-steps'),
                    html.Div([
                        html.P([
                            html.Strong("What this shows: "),
                            "This visualization shows the relationship between daily steps and sleep duration. "
                            "The size of points represents physical activity level, while color shows heart rate."
                        ])
                    ], style=INFO_BOX_STYLE)
                ], style={**CARD_STYLE, "border-left": "5px solid #2ecc71"}),
                
                # Sleep by Health Factors Section (BMI & Sleep Disorders)
                html.Div([
                    html.Div([
                        html.H2("Health Factors & Sleep", 
                               style={"color": "#f39c12", "margin-bottom": "0.8rem"}),
                        html.Div([
                            html.Span("🩺", style={"font-size": "1.2rem", "margin-right": "0.5rem"}),
                            html.Span("How health conditions affect sleep")
                        ], style={"color": "#7f8c8d", "font-size": "0.9rem"})
                    ]),
                    html.Div([
                        # BMI Tab
                        html.Div([
                            html.H3("Sleep by BMI Category", style={"fontSize": "1rem", "color": "#7f8c8d"}),
                            dcc.Graph(id='box-bmi'),
                        ], style={"margin-bottom": "1.5rem"}),
                        
                        # Sleep Disorder Tab
                        html.Div([
                            html.H3("Sleep by Disorder Type", style={"fontSize": "1rem", "color": "#7f8c8d"}),
                            dcc.Graph(id='box-disorder'),
                        ]),
                    ]),
                    html.Div([
                        html.P([
                            html.Strong("What this shows: "),
                            "These visualizations display how BMI category and sleep disorders relate to sleep duration. "
                            "Both factors can significantly impact sleep quality and quantity, with certain conditions requiring specialized attention."
                        ])
                    ], style=INFO_BOX_STYLE)
                ], style={**CARD_STYLE, "border-left": "5px solid #f39c12"}),
            ], className="six columns"),
        ], className="row"),
        
        # Health Tips Section
        html.Div([
            html.Div([
                html.H2("Sleep Health Tips", style={"color": "#1abc9c", "margin-bottom": "1rem"}),
                html.Div([
                    html.Div([
                        html.H4("Consistency Matters", style={"color": "#2c3e50"}),
                        html.P("Maintain a regular sleep schedule, even on weekends. This helps regulate your body's internal clock."),
                    ], className="three columns", style={"padding": "1rem", "background-color": "#f8f9fa", "border-radius": "8px"}),
                    
                    html.Div([
                        html.H4("Stress Management", style={"color": "#2c3e50"}),
                        html.P("Practice relaxation techniques like deep breathing, meditation or gentle stretching before bedtime."),
                    ], className="three columns", style={"padding": "1rem", "background-color": "#f8f9fa", "border-radius": "8px"}),
                    
                    html.Div([
                        html.H4("Physical Activity", style={"color": "#2c3e50"}),
                        html.P("Regular exercise can help you fall asleep faster and enjoy deeper sleep, but not too close to bedtime."),
                    ], className="three columns", style={"padding": "1rem", "background-color": "#f8f9fa", "border-radius": "8px"}),
                    
                    html.Div([
                        html.H4("Healthy Environment", style={"color": "#2c3e50"}),
                        html.P("Keep your bedroom cool, quiet, and dark. Consider using earplugs, eye shades, or white noise machines."),
                    ], className="three columns", style={"padding": "1rem", "background-color": "#f8f9fa", "border-radius": "8px"}),
                ], className="row", style={"margin-top": "1rem"}),
            ], style={**CARD_STYLE, "border-left": "5px solid #1abc9c"}),
        ]),
    ], style=CONTENT_STYLE),
    
    # Footer
    html.Footer([
        html.Div([
            html.P("Sleep Health Analysis Dashboard | Created with Dash & Plotly", 
                  style={"textAlign": "center", "font-style": "italic", "color": "#7f8c8d"}),
            html.P("Data updated: April 2025", 
                  style={"textAlign": "center", "fontSize": "0.8rem", "color": "#95a5a6"})
        ], style={"padding": "1rem", "borderTop": "1px solid #ecf0f1"})
    ])
])

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    [
        Output('histogram-duration', 'figure'),
        Output('scatter-stress', 'figure'),
        Output('scatter-steps', 'figure'),
        Output('box-gender', 'figure'),
        Output('box-bmi', 'figure'),
        Output('box-disorder', 'figure'),
    ],
    [Input('gender-filter', 'value')]
)
def update_dashboard(gender):
    # Filter data based on selection
    filtered_df = df if gender in (None, "All") else df[df['gender'] == gender]
    
    # Common figure layout settings with health theme
    layout_settings_main = {
        "template": "plotly_white",
        "margin": dict(l=40, r=40, t=30, b=30),
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        "height": 380,
    }
    
    # For smaller graphs
    layout_settings_smaller = {
        "template": "plotly_white",
        "margin": dict(l=40, r=40, t=30, b=30),
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        "height": 340,
    }
    
    # Create histogram with health theme
    fig1 = px.histogram(
        filtered_df, 
        x='sleep_duration', 
        nbins=20,
        title=None,
        color_discrete_sequence=["#3498db"],
        opacity=0.7,
        labels={'sleep_duration': 'Sleep Duration (hours)'}
    )
    
    # Add reference zones for healthy sleep
    fig1.add_vrect(
        x0=7, x1=9,
        fillcolor="#2ecc71", opacity=0.15,
        layer="below", line_width=0,
        annotation_text="Recommended Sleep Range",
        annotation_position="top right"
    )
    
    fig1.add_annotation(
        x=8, y=0,
        text="Healthy Range: 7-9 hours",
        showarrow=False,
        font=dict(size=12, color="#2ecc71"),
        yshift=10
    )
    
    fig1.update_layout(**layout_settings_main)
    
    # Create scatter plot for stress vs sleep with health theme
    fig2 = px.scatter(
        filtered_df, 
        x='stress_level', 
        y='sleep_duration',
        color='quality_of_sleep',
        title=None,
        color_continuous_scale=['#e74c3c', '#f39c12', '#2ecc71'],
        labels={
            'stress_level': 'Stress Level (1-10)',
            'sleep_duration': 'Sleep Duration (hours)',
            'quality_of_sleep': 'Sleep Quality'
        }
    )
    
    # Add stress level zones
    fig2.add_hrect(
        y0=7, y1=9,
        fillcolor="#2ecc71", opacity=0.15,
        layer="below", line_width=0,
    )
    
    fig2.update_layout(**layout_settings_main)
    
    # Create scatter plot for steps vs sleep with health theme
    fig3 = px.scatter(
        filtered_df, 
        x='daily_steps', 
        y='sleep_duration',
        size='physical_activity_level',
        color='heart_rate',
        title=None,
        color_continuous_scale=['#2ecc71', '#f39c12', '#e74c3c'],
        labels={
            'daily_steps': 'Daily Steps',
            'sleep_duration': 'Sleep Duration (hours)',
            'physical_activity_level': 'Activity Level',
            'heart_rate': 'Heart Rate (bpm)'
        }
    )
    
    # Add reference line for recommended steps
    fig3.add_vline(
        x=10000, line_width=2, line_dash="dash", line_color="#3498db",
        annotation_text="10,000 steps goal", annotation_position="top right"
    )
    
    # Add sleep recommendation zone
    fig3.add_hrect(
        y0=7, y1=9,
        fillcolor="#2ecc71", opacity=0.15,
        layer="below", line_width=0,
    )
    
    fig3.update_layout(**layout_settings_main)
    
    # Create box plot by gender with health theme
    fig4 = px.box(
        filtered_df, 
        x='gender', 
        y='sleep_duration', 
        color='gender',
        color_discrete_sequence=colors,
        title=None,
        labels={'sleep_duration': 'Sleep Duration (hours)'}
    )
    
    # Add healthy sleep range
    fig4.add_hrect(
        y0=7, y1=9,
        fillcolor="#2ecc71", opacity=0.15,
        layer="below", line_width=0,
        annotation_text="Healthy Range",
        annotation_position="top right"
    )
    
    fig4.update_layout(**layout_settings_main)
    
    # Create box plot by BMI category with health theme
    fig5 = px.box(
        filtered_df, 
        x='bmi_category', 
        y='sleep_duration', 
        color='bmi_category',
        color_discrete_sequence=colors,
        title=None,
        category_orders={"bmi_category": ["Underweight", "Normal", "Overweight", "Obese"]},
        labels={'sleep_duration': 'Sleep Duration (hours)'}
    )
    
    # Add healthy sleep range
    fig5.add_hrect(
        y0=7, y1=9,
        fillcolor="#2ecc71", opacity=0.15,
        layer="below", line_width=0,
    )
    
    fig5.update_layout(**layout_settings_smaller)
    
    # Create box plot by sleep disorder with health theme
    fig6 = px.box(
        filtered_df, 
        x='sleep_disorder', 
        y='sleep_duration', 
        color='sleep_disorder',
        color_discrete_sequence=colors,
        title=None,
        labels={'sleep_duration': 'Sleep Duration (hours)'}
    )
    
    # Add healthy sleep range
    fig6.add_hrect(
        y0=7, y1=9,
        fillcolor="#2ecc71", opacity=0.15,
        layer="below", line_width=0,
    )
    
    fig6.update_layout(**layout_settings_smaller)

    return fig1, fig2, fig3, fig4, fig5, fig6

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=False, host='0.0.0.0', port=port)