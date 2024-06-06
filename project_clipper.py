import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Load the dataset with a different encoding
file_path = '/Users/linyun/Downloads/netflix_titles 2.csv'
df = pd.read_csv(file_path, encoding='latin1')

# Initialize the Dash app
app = dash.Dash(__name__)

# Ensure there are no null values in the 'rating' column to avoid errors
df['rating'].fillna('Unknown', inplace=True)

# Handle NaN values in the duration column
df['duration'].fillna('Unknown', inplace=True)

# Separate the duration into minutes and seasons
df['duration_minutes'] = df['duration'].apply(lambda x: int(x.split()[0]) if 'min' in x else None)
df['duration_seasons'] = df['duration'].apply(lambda x: int(x.split()[0]) if 'Season' in x else None)

# Layout of the Dashboard
app.layout = html.Div([
    html.H1("Netflix Titles Dashboard"),
    
    html.Div([
        dcc.Graph(id='year-graph'),
        dcc.Graph(id='rating-graph'),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'padding': '10px'}),

    html.Div([
        dcc.Graph(id='duration-scatter'),
    ], style={'padding': '10px'}),

    html.Div([
        dcc.RadioItems(
            id='type-radio',
            options=[
                {'label': 'Movies', 'value': 'Movie'},
                {'label': 'TV Shows', 'value': 'TV Show'}
            ],
            value='Movie',
            labelStyle={'display': 'inline-block', 'margin-right': '20px'}
        ),
        dcc.Dropdown(
            id='rating-dropdown',
            options=[{'label': rating, 'value': rating} for rating in df['rating'].unique()],
            value='TV-MA',
            style={'width': '150px', 'display': 'inline-block', 'margin-left': '20px'}
        ),
    ], style={'display': 'flex', 'justify-content': 'center', 'padding': '10px'}),

    html.Div([
        dcc.Graph(id='title-table')
    ], style={'padding': '10px'})
])

# Callback to update the year graph
@app.callback(
    Output('year-graph', 'figure'),
    [Input('rating-dropdown', 'value')]
)
def update_year_graph(selected_rating):
    filtered_df = df[df['rating'] == selected_rating]
    fig = px.histogram(filtered_df, x='release_year', nbins=30, title='Number of Titles Released per Year')
    return fig

# Callback to update the rating graph
@app.callback(
    Output('rating-graph', 'figure'),
    [Input('rating-dropdown', 'value')]
)
def update_rating_graph(selected_rating):
    fig = px.pie(df, names='rating', title='Distribution of Titles by Rating')
    return fig

# Callback to update the scatter plot of duration vs release year
@app.callback(
    Output('duration-scatter', 'figure'),
    [Input('rating-dropdown', 'value'), Input('type-radio', 'value')]
)
def update_scatter_plot(selected_rating, selected_type):
    filtered_df = df[(df['rating'] == selected_rating) & (df['type'] == selected_type)]
    if selected_type == 'Movie':
        y_axis = 'duration_minutes'
        title = f'Duration in Minutes vs Release Year for Rating: {selected_rating} (Movies)'
    else:
        y_axis = 'duration_seasons'
        title = f'Duration in Seasons vs Release Year for Rating: {selected_rating} (TV Shows)'
    fig = px.scatter(filtered_df, x='release_year', y=y_axis, color='type', title=title)
    return fig

# Callback to update the table
@app.callback(
    Output('title-table', 'figure'),
    [Input('rating-dropdown', 'value'), Input('type-radio', 'value')]
)
def update_table(selected_rating, selected_type):
    filtered_df = df[(df['rating'] == selected_rating) & (df['type'] == selected_type)]
    if selected_type == 'Movie':
        duration_column = filtered_df['duration_minutes']
        duration_label = 'Duration (Minutes)'
    else:
        duration_column = filtered_df['duration_seasons']
        duration_label = 'Duration (Seasons)'

    fig = go.Figure(data=[go.Table(
        header=dict(values=['Title', 'Director', 'Release Year', 'Rating', duration_label],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[filtered_df.title, filtered_df.director, filtered_df.release_year, filtered_df.rating,
                           duration_column],
                   fill_color='lavender',
                   align='left'))
    ])
    fig.update_layout(title=f'Detailed Information for Rating: {selected_rating} ({selected_type}s)')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

