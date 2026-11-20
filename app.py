import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config("Illinois State Buildings", layout="wide")
@st.cache_data
def load_data():
    df = pd.read_csv("building_inventory.csv")
    df["Year Constructed"] = df["Year Constructed"].where(df["Year Constructed"] >= 1800)
    df["Decade"] = (df["Year Constructed"] // 10 * 10).astype("Int64")
    df["Usage Description"] = df["Usage Description"].str.strip()
    return df
df = load_data()
st.title("Illinois State Owned Buildings")
st.caption("Source: building_inventory.csv")
st.sidebar.header("filters")
agencies = sorted(df["Agency Name"].unique())
top_agencies = df["Agency Name"].value_counts().head(5).index.tolist()
chosen = st.sidebar.multiselect("Agency", agencies, default = top_agencies)
statuses = st.sidebar.multiselect(
    "building status", sorted(df['Bldg Status'].unique()), defaut = ["in use"]
    
)
year_min, year_max = st.sidebar.slider("year constructed", 1800, 2019, (1800,2019))
f = df[
    df["Agency Name"].isin(chosen)
    & df["Bldg Status"].isin(statuses)
    & df["Year Constructed"].between(year_min,year_max)
    
].dropna(subset=['Year Constructed'])
st.write(f"Showing ** {len(f):,}** buildings")

st.header("visualization 1: when were buildings constructed, and for what use?")
sel = alt.selection_point(fields=["Usage Description"], bind="legend")
chart1 = (
    alt.Chart(f)
    .mark_bar()
    .encode(
        x = alt.X("Decade:O", title= "Decade constructed"),
        y = alt.Y("count()", title="Number of buildings"),
        color = alt.Color("Usage Description:N",title="Usage"),
        opacity = alt.condition(sel,alt.value(1),alt.value(0.2)),
        tooltip = ["Decade:O","Usage Description:N", "count()"],
                                                              
    )
    .add_params(sel)
    .properties(height=400)
)
st.altair_chart(chart1,use_container_width=True)
st.caption("click a legend value to highlight a usage type")

st.header("visualization 2: building size over time")
brush = alt.selection_interval(encodings=["x","y"])
scatter = (
    alt.Chart(f[f["Square Footage"] > 0])
    .mark_circle(size=40)
    .encode(
        x= alt.X("Year Constructed:Q", scale=alt.Scale(zero=False),title= "Year Constructed"),
        y = alt.Y("Square Footage:Q", scale=alt.Scale(type="log"), title= "Square Footage (log)"),
        color = alt.condition(brush,alt.Color("Agency Name:N", legend= None), alt.value("lightgray")),
        tooltip=["Location Name", "Agency Name", "Year Constructed", "Square Footage", "Usage Description"],
                                                                                                           
    )
    .add_params(brush)
    .properties(height=350, width=650)
)
bars = (
    alt.Chart(f[f["Square Footage"] > 0])
    .mark_bar()
    .encode(
        y =alt.Y("Agency Name:N", sort="-x",title=None),
        x = alt.X("count()", title="Buildings in brushed region"),
        color = alt.Color("Agency Name:N", legend= None)
    )
    .transform_filter(brush)
    .properties(height=350, width=300)
)
st.altair_chart(scatter | bars, use_container_width=True)
st.caption("drag a box on the scatterplot. the bar chart updates to selected buildings.")

st.header("write up")
st.subheader("visualization 1")
st.write("For the first viz I chose to highlight how the state's building stock is distrubed across decades. I included what usage types are most common in each era. I made an interactive legend to click a usage type and a sidebar filter for agency, status, and year. For design, I put in bar marks with count aggregation, decades as an ordinal x-axis, colors for usage, opacity for selection, and data cleaning. With more time I'd put smaller usage categories into 'misc' or 'other'. I might normalize the stacking as well.")
st.subheader("visualization 2")
st.write("I chose to highlight the relationship between building age and size, the huge range in size (including how many large buildings there are and how few small buildings there are), and which agencies own which buildings in selected regions. For design I chose to make a scatterplot with a log scale on square footage, as well as brush selection on both axes, gray for unselected points, color encoding in both charts, and tooltips with location, agency, year, size, and usage for detail. If i had more time I'd add transparency for overlapping points. I'd change the chart widths so the layout isn't so cramped and maybe add a geographic view with field locations that I didn't use.")
