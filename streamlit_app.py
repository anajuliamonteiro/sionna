import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px

# Streamlit config
st.set_page_config(
    page_title="Sionna Therapeutics",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)
alt.themes.enable("dark")

# CF data
cf_registry_data = [
    ("California", 2566), ("Texas", 2368), ("Florida", 1908), ("New York", 1685),
    ("Pennsylvania", 1713), ("Ohio", 1214), ("North Carolina", 1153), ("Illinois", 1099),
    ("Michigan", 1635), ("Georgia", 919), ("Tennessee", 895), ("Indiana", 855),
    ("Missouri", 821), ("Massachusetts", 834), ("Washington", 784), ("Wisconsin", 729),
    ("Arizona", 604), ("Colorado", 551), ("New Mexico", 551), ("Oregon", 468),
    ("Kansas", 405), ("Iowa", 432), ("Oklahoma", 369), ("Arkansas", 329),
    ("Alabama", 511), ("South Carolina", 505), ("Kentucky", 650), ("Virginia", 859),
    ("Louisiana", 387), ("Mississippi", 269), ("Minnesota", 743), ("Nevada", 230),
    ("Nebraska", 297), ("Utah", 714), ("Idaho", 261), ("Montana", 152),
    ("North Dakota", 80), ("South Dakota", 141), ("Wyoming", 47), ("Maine", 268),
    ("New Hampshire", 139), ("Vermont", 238), ("Rhode Island", 112), ("Connecticut", 378),
    ("New Jersey", 745), ("Delaware", 91), ("Maryland", 571), ("West Virginia", 289),
    ("District of Columbia", 43), ("Alaska", 57), ("Hawaii", 14)
]
df_cf = pd.DataFrame(cf_registry_data, columns=["State", "CF Patients"])

# Add state abbreviations for mapping
state_abbr = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "District of Columbia": "DC"
}
df_cf["State Code"] = df_cf["State"].map(state_abbr)

# Create choropleth
fig = px.choropleth(
    df_cf,
    locations="State Code",
    locationmode="USA-states",
    color="CF Patients",
    hover_name="State",
    scope="usa",
    color_continuous_scale="Viridis"
)
fig.update_layout(template="plotly_dark", height=600, margin=dict(l=0, r=0, t=0, b=0))

# Sort table by highest CF patient count
df_cf = df_cf.sort_values(by="CF Patients", ascending=False)

# Streamlit layout
tab1, tab2 = st.tabs(["CF Market Outlook", "Revenue Forecast"])

with tab1:
    col = st.columns((1.5, 4.5, 2), gap='medium')

    with col[0]:
        st.markdown('#### CF Market')
        st.metric(label="Patients in the **U.S.**", value="40,000", delta="1000")
        st.metric(label="Patients **Globally**", value="105,000", delta="14.2%")
        st.metric(label="U.S. Patients w/ **F508del** Mutation", value="~28,000")

    with col[1]:
        st.plotly_chart(fig, use_container_width=True)

    with col[2]:
        st.markdown("#### Patients per State")
        st.dataframe(
            df_cf.sort_values("CF Patients", ascending=False),
            column_order=("State", "CF Patients"),
            hide_index=True,
            use_container_width=True,
            column_config={
                "State": st.column_config.TextColumn("State"),
                "CF Patients": st.column_config.ProgressColumn(
                    "CF Patients",
                    format="%d",
                    min_value=0,
                    max_value=2600
                )
            }
        )

with tab2:
    st.markdown("### Revenue Forecast (Editable)")

    col1, col2 = st.columns((1.5, 5.5), gap='medium')

    with col1:
        st.markdown("#### Inputs")
        price_per_patient = st.number_input("Price per Patient (USD)", min_value=100_000, max_value=400_000, value=330_000, step=10_000)
        start_penetration = st.number_input("Penetration in Year 5 (2030) (%)", min_value=0.0, max_value=5.0, value=1.0, step=0.1)
        end_penetration = st.number_input("Penetration in Year 10 (2035) (%)", min_value=0.0, max_value=10.0, value=5.0, step=0.1)

    with col2:
        years = list(range(2026, 2036))
        eligible_patients = [28000, 28700, 29400, 30100, 30800, 31500, 32200, 32900, 33600, 34300]

        penetration_curve = [0.0] * 4  # 2026–2029
        for i in range(6):  # 2030–2035
            pct = start_penetration + (end_penetration - start_penetration) * i / 5
            penetration_curve.append(pct / 100)

        revenue_data = []
        for year, eligible, pen in zip(years, eligible_patients, penetration_curve):
            patients = eligible * pen
            revenue = patients * price_per_patient
            revenue_data.append({"Year": year, "Patients": int(patients), "Revenue (USD)": revenue})

        df_revenue = pd.DataFrame(revenue_data)

        revenue_chart = alt.Chart(df_revenue).mark_bar(color="#FF4B4B").encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Revenue (USD):Q", title="Annual Revenue (USD)"),
            tooltip=["Year", "Patients", "Revenue (USD)"]
        ).properties(height=420)

        st.altair_chart(revenue_chart, use_container_width=True)
