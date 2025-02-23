import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dash_table import DataTable
import plotly.io as pio

# Load your CSV data
df = pd.read_csv('data/sales_data_with_clusters.csv')

# Clean the data if needed (Handle missing values)
df['Total Amount'] = df['Total Amount'].fillna(0)
df['Age'] = df['Age'].fillna(df['Age'].median())  # Example: Fill missing age with median age

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout for the app
app.layout = html.Div([
    html.H1("Sales Dashboard", style={'textAlign': 'center', 'font-size': '40px'}),
    
    # Dropdowns for Product Category and Age Group Filters
    html.Div([
        dcc.Dropdown(
            id='product-category-dropdown',
            options=[{'label': category, 'value': category} for category in df['Product Category'].unique()],
            value='Beauty',
            style={'width': '30%', 'margin': '20px'}
        ),
        dcc.Dropdown(
            id='age-group-dropdown',
            options=[{'label': f'{age}', 'value': age} for age in df['Age'].unique()],
            value=30,
            style={'width': '30%', 'margin': '20px'}
        ),
    ], style={'display': 'flex', 'justify-content': 'center'}),
    
    # Graph for Total Sales by Product Category
    dcc.Graph(id='total-sales-product-category'),
    
    # Graph for Total Sales by Gender
    dcc.Graph(id='total-sales-gender'),
    
    # DataTable to display Top 5 Customers by Total Spending
    html.Div([DataTable(id='top-customers-table')], style={'margin': '30px'}),
    
    # Graph for Average Sales per Product Category
    dcc.Graph(id='average-sales-product-category'),
    
    # Download Link for Filtered Data
    html.A("Download Filtered Data", id="download-link", download="filtered_data.csv", href=""),
    
    # Graph for Monthly Sales Trends
    dcc.Graph(id='monthly-sales-trends')
])

# Callback for Total Sales by Product Category
@app.callback(
    Output('total-sales-product-category', 'figure'),
    [Input('product-category-dropdown', 'value')]
)
def update_total_sales_by_product_category(selected_category):
    filtered_df = df[df['Product Category'] == selected_category]
    total_sales = filtered_df.groupby('Product Category')['Total Amount'].sum().reset_index()
    
    fig = px.bar(total_sales, x='Product Category', y='Total Amount', 
                 title="Total Sales by Product Category", 
                 labels={'Total Amount': 'Total Sales'})
    return fig

# Callback for Total Sales by Gender
@app.callback(
    Output('total-sales-gender', 'figure'),
    [Input('product-category-dropdown', 'value')]
)
def update_total_sales_by_gender(selected_category):
    filtered_df = df[df['Product Category'] == selected_category]
    total_sales_gender = filtered_df.groupby('Gender')['Total Amount'].sum().reset_index()
    
    fig = px.bar(total_sales_gender, x='Gender', y='Total Amount', 
                 title="Total Sales by Gender", 
                 labels={'Total Amount': 'Total Sales'})
    return fig

# Callback for Top 5 Customers by Total Spending
@app.callback(
    Output('top-customers-table', 'data'),
    [Input('product-category-dropdown', 'value')]
)
def update_top_customers_table(selected_category):
    filtered_df = df[df['Product Category'] == selected_category]
    top_customers = filtered_df.groupby('Customer ID')['Total Amount'].sum().reset_index()
    top_customers = top_customers.sort_values(by='Total Amount', ascending=False).head(5)
    
    return top_customers.to_dict('records')

# Callback for Average Sales per Product Category
@app.callback(
    Output('average-sales-product-category', 'figure'),
    [Input('product-category-dropdown', 'value')]
)
def update_average_sales(selected_category):
    filtered_df = df[df['Product Category'] == selected_category]
    avg_sales = filtered_df.groupby('Product Category')['Total Amount'].mean().reset_index()
    
    fig = px.bar(avg_sales, x='Product Category', y='Total Amount', 
                 title="Average Sales per Product Category", 
                 labels={'Total Amount': 'Average Sales'})
    return fig

# Callback for Monthly Sales Trends
@app.callback(
    Output('monthly-sales-trends', 'figure'),
    [Input('product-category-dropdown', 'value')]
)
def update_monthly_sales_trends(selected_category):
    filtered_df = df[df['Product Category'] == selected_category]
    monthly_sales = filtered_df.groupby('Month')['Total Amount'].sum().reset_index()
    
    fig = px.line(monthly_sales, x='Month', y='Total Amount', 
                  title="Monthly Sales Trends", 
                  labels={'Total Amount': 'Sales Amount'})
    return fig

# Callback to enable downloading filtered data
@app.callback(
    Output("download-link", "href"),
    [Input('product-category-dropdown', 'value'),
     Input('age-group-dropdown', 'value')]
)
def generate_csv(selected_category, selected_age_group):
    filtered_df = df[(df['Product Category'] == selected_category) & (df['Age'] == selected_age_group)]
    return dcc.send_data_frame(filtered_df.to_csv, "filtered_data.csv")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
