from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import dash_mantine_components as dmc
import os

# Cargar datos
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Inicializar app
app = Dash(__name__, suppress_callback_exceptions=True)

# Layout general
app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    children=dmc.AppShell(
        padding="md",
        navbar=dmc.Navbar(
            style={"width": "250px"},
            p="xs",
            children=[
                dmc.NavLink(label="Inicio", href="/", active=True),
                dmc.NavLink(label="Tabla", href="/table"),
                dmc.NavLink(label="Gráfico", href="/graph"),
                dmc.NavLink(label="Bubble Plot", href="/bubble"),
                dmc.NavLink(label="Distribuciones", href="/distribution"),
                dmc.NavLink(label="Scatter Plot", href="/scatter"),
            ]
        ),
        footer=dmc.Footer(height=40, p="md", children="© 2025 Dashboard Pro"),
        children=[
            dcc.Location(id="url"),
            html.Div(id="page-content")
        ]
    )
)

# Páginas
inicio_layout = dmc.Container([
    dmc.Image(src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Gapminder_logo.svg/512px-Gapminder_logo.svg.png", width=200, mx="auto"),
    dmc.Title("Dashboard Profesional - Gapminder 2007", align="center", color="blue"),
    dmc.Space(h=20),
    dmc.Grid([
        dmc.Col(dmc.Paper(dmc.Stack([
            dmc.Text("Esperanza de vida promedio", weight=700),
            dmc.Text(f"{df['lifeExp'].mean():.2f} años", size="xl")
        ]), p="md", shadow="sm"), span=4),
        dmc.Col(dmc.Paper(dmc.Stack([
            dmc.Text("Población total", weight=700),
            dmc.Text(f"{df['pop'].sum()/1e9:.2f} B", size="xl")
        ]), p="md", shadow="sm"), span=4),
        dmc.Col(dmc.Paper(dmc.Stack([
            dmc.Text("PIB per cápita promedio", weight=700),
            dmc.Text(f"${df['gdpPercap'].mean():,.0f}", size="xl")
        ]), p="md", shadow="sm"), span=4),
    ], gutter="md"),
    dmc.Space(h=30),
    dmc.Text("Explore los indicadores clave de desarrollo humano por continente y país.", size="md")
])

table_layout = dmc.Container([
    dmc.Title("Tabla de Datos"),
    dash_table.DataTable(data=df.to_dict('records'), page_size=12, style_table={'overflowX': 'auto'})
])

graph_layout = dmc.Container([
    dmc.Title("Promedios por Continente"),
    dmc.Grid([
        dmc.Col([
            dmc.Select(label="Variable", id="var-select", data=[{"label": i, "value": i} for i in ['pop', 'lifeExp', 'gdpPercap']], value="lifeExp")
        ], span=4),
        dmc.Col([
            dcc.Graph(id="main-graph"),
            html.Div(id="graph-description")
        ], span=8)
    ])
])

bubble_layout = dmc.Container([
    dmc.Title("Bubble Plot: PIB vs Esperanza de Vida"),
    dcc.Graph(figure=px.scatter(df, x='gdpPercap', y='lifeExp', size='pop', color='continent', hover_name='country', log_x=True, template="plotly_white", title="Bubble Plot")),
    dmc.Text("Los países con mayor PIB per cápita tienden a tener mayor esperanza de vida.")
])

distribution_layout = dmc.Container([
    dmc.Title("Distribuciones por País"),
    dmc.Select(label="Seleccione un país", id="country-select", data=[{"label": c, "value": c} for c in df.country], value="Canada"),
    dmc.Grid([
        dmc.Col(dcc.Graph(id='dist-lifeExp'), span=4),
        dmc.Col(dcc.Graph(id='dist-pop'), span=4),
        dmc.Col(dcc.Graph(id='dist-gdp'), span=4),
    ]),
    dmc.Text("Las líneas rojas indican los valores del país seleccionado.")
])

scatter_layout = dmc.Container([
    dmc.Title("Scatter Plot Interactivo"),
    dmc.Select(label="Seleccione continente", id="continent-select", data=[{"label": c, "value": c} for c in df.continent.unique()] + [{"label": "Todos", "value": "Todos"}], value="Todos"),
    dcc.Graph(id="scatter-plot")
])

# Navegación
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(path):
    return {
        "/": inicio_layout,
        "/table": table_layout,
        "/graph": graph_layout,
        "/bubble": bubble_layout,
        "/distribution": distribution_layout,
        "/scatter": scatter_layout,
    }.get(path, inicio_layout)

# Callbacks
@app.callback(
    Output("main-graph", "figure"),
    Output("graph-description", "children"),
    Input("var-select", "value")
)
def update_main_graph(var):
    fig = px.bar(df.groupby("continent")[var].mean().reset_index(), x="continent", y=var, text_auto=True, template="simple_white")
    description = {
        "lifeExp": "Europa y América presentan mayores esperanzas de vida.",
        "pop": "Asia lidera con mayor población promedio.",
        "gdpPercap": "Europa y América tienen el mayor PIB per cápita promedio."
    }[var]
    return fig, dmc.Text(description, size="sm")

@app.callback(
    Output("dist-lifeExp", "figure"),
    Output("dist-pop", "figure"),
    Output("dist-gdp", "figure"),
    Input("country-select", "value")
)
def update_distributions(country):
    figs = []
    for col in ["lifeExp", "pop", "gdpPercap"]:
        fig = px.histogram(df, x=col, nbins=20, template="plotly_white")
        val = df[df.country == country][col].values[0]
        fig.add_vline(x=val, line_color="red")
        figs.append(fig)
    return figs

@app.callback(Output("scatter-plot", "figure"), Input("continent-select", "value"))
def update_scatter(cont):
    data = df if cont == "Todos" else df[df.continent == cont]
    return px.scatter(data, x='gdpPercap', y='lifeExp', size='pop', color='continent', hover_name='country', template="plotly_white")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port)
