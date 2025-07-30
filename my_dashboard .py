import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io
import seaborn as sns
import matplotlib.ticker as ticker
import plotly.express as px

PASSWORD = "theioutlet@1"

# Ask for password input
st.title("🔒 Protected Dashboard")
password = st.text_input("Enter password:", type="password")

if password != PASSWORD:
    st.warning("🚫 Incorrect password. Please try again.")
    st.stop()  # Stop running any further code if wrong password
else:
    st.success("✅ Access granted!")
# --------------------------
# Responsive CSS for better display on all devices
# --------------------------
st.markdown(
    """
    <style>
    /* Allow horizontal scroll on tables */
    .dataframe, .stDataFrame div[data-testid="stTable"] > div {
        overflow-x: auto;
    }

    /* Responsive font sizes and padding */
    @media only screen and (max-width: 600px) {
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.3rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
        .css-1v3fvcr {
            padding-left: 8px !important;
            padding-right: 8px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True
)

# --------------------------
# Project Overview
# --------------------------
st.set_page_config(page_title="The iOutlet Education Expansion Dashboard", layout="wide")
st.title("The iOutlet Strategic Dashboard")
st.markdown("""
**Project Title:** *Maximising Impact: The iOutlet's Strategic Expansion in Education*

**Company:** The iOutlet  
**Website:** [theioutlet.com](https://www.theioutlet.com)

**Project Goal:**  
To develop a data-driven strategy for expanding refurbished tech sales in the education sector, based on analysis of sales trends, school segments, and regional opportunities.
""")

# --------------------------
# Load and Clean Data from SharePoint
# --------------------------
@st.cache_data
def load_data():
    file_url = "https://dmail-my.sharepoint.com/:x:/g/personal/2619506_dundee_ac_uk/EVXCRx9d2fJDsk7QB5XzUUsBhDsV7DsQyxa3FuK6jy9zBg?download=1"
    response = requests.get(file_url)
    bytes_io = io.BytesIO(response.content)
    sales_df = pd.read_excel(bytes_io, sheet_name="Sales")
    schools_df = pd.read_excel(bytes_io, sheet_name="Schools")
    sales_df.columns = sales_df.columns.str.strip()
    sales_df['Order Date'] = pd.to_datetime(sales_df['Order Date'], errors='coerce', dayfirst=True)
    return sales_df, schools_df

sales_df, schools_df = load_data()

# Filter out rows where School Match is blank or empty
edu_df = sales_df[sales_df['School Match'].notna() & (sales_df['School Match'].astype(str).str.strip() != "")]

# --------------------------
# KPIs
# --------------------------
total_revenue = sales_df['Item Total'].sum()
edu_revenue = edu_df['Item Total'].sum()
total_units = sales_df['Quantity'].sum()
schools_reached = edu_df['School Match'].nunique()
repeat_orders = edu_df.groupby('School Match')['Order ID'].nunique()
repeat_order_rate = (repeat_orders[repeat_orders > 1].count() / schools_reached) * 100

# New KPI calculations
total_schools_by_school_type = edu_df['School Type'].nunique()
total_schools_by_type = edu_df['Type'].nunique()
total_trust_matched_sales = edu_df[edu_df['Trust Match'].str.strip().str.lower() == 'trust'].shape[0]
unique_trust_schools = edu_df[edu_df['Trust Match'].str.strip().str.lower() == 'trust']['School Match'].nunique()

# ✅ New: Number of Sales to Schools
num_sales_to_schools = edu_df.shape[0]

# First row with 4 columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"£{total_revenue:,.2f}")
col2.metric("🎓 Education Revenue", f"£{edu_revenue:,.2f}")
col3.metric("📦 Units Sold", f"{int(total_units):,}")
col4.metric("🏫 Schools Reached", f"{schools_reached}")

# Second row with 3 columns
col5, col6, col7 = st.columns(3)
col5.metric("🛒 Sales to Schools", f"{num_sales_to_schools:,}")
col6.metric("🏢 Trust-Matched Sales", f"{total_trust_matched_sales}")
col7.metric("🏘 Unique Trust Schools", f"{unique_trust_schools}")

st.markdown(f"**Unique Schools with Trust Match:** {unique_trust_schools}")

# --------------------------
# Monthly Sales Trends
# --------------------------
st.markdown("### 📈 Monthly Sales Trends")
monthly_sales = sales_df.resample('MS', on='Order Date')['Item Total'].sum()
monthly_edu = edu_df.resample('MS', on='Order Date')['Item Total'].sum()

fig1, ax1 = plt.subplots(figsize=(8, 4))
ax1.plot(monthly_sales.index, monthly_sales.values, label='All Sales', marker='o')
ax1.plot(monthly_edu.index, monthly_edu.values, label='Education Sales', marker='s')
ax1.set_title("Monthly Revenue")
ax1.set_ylabel("£")
ax1.legend()
ax1.grid(True)
st.pyplot(fig1)

st.markdown("""
This line chart shows the total revenue over time, comparing all sales with those specifically from the education sector.  
You can see seasonal peaks and overall growth, helping identify periods of higher demand and sales trends.
""")

# --------------------------
# Regional Sales Breakdown
# --------------------------
st.markdown("### 🌍 Regional Sales Breakdown")
# Clean the Region column: strip whitespace only
sales_df['Region_clean'] = sales_df['Region'].astype(str).str.strip()

# Group revenue by all unique regions including blanks and unusual entries
region_sales_all = sales_df.groupby('Region_clean')['Item Total'].sum().sort_values(ascending=False)

# Plotting
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=region_sales_all.values, y=region_sales_all.index, palette='viridis', ax=ax)

# Format x-axis as £ currency with commas
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'£{int(x):,}'))

ax.set_xlabel("Revenue (£)")
ax.set_ylabel("Region")
ax.set_title("Total Sales Revenue by All Regions (Including All Unique Places)")
ax.grid(axis='x', linestyle='--', alpha=0.7)

plt.tight_layout()
st.pyplot(fig)

st.markdown("""
This bar chart presents total revenue generated from each region (all places listed in the Region column).  
It highlights lucrative areas and sales distribution.
""")
# --------------------------
# School Segmentation
# --------------------------

st.markdown("### 🏫 Orders by School Type and Region")

# Count education orders by school type
school_types = edu_df["Type"].dropna().value_counts()

# Count education orders by Region (direct from edu_df)
orders_by_region = edu_df['Region'].value_counts().reset_index()
orders_by_region.columns = ['Region', 'Orders']

col1, col2 = st.columns([3, 2])

with col1:
    fig, ax = plt.subplots(figsize=(8, 4))
    school_types.plot(kind='bar', color='dodgerblue', ax=ax)
    ax.set_title("Orders by School Type")
    ax.set_xlabel("School Type")
    ax.set_ylabel("Number of Orders")
    st.pyplot(fig)
    st.markdown("""
    This bar chart shows the number of education orders by school type.  
    """)

with col2:
    st.markdown("### 🌍 Education Orders by Region")

    fig2 = px.bar(
        orders_by_region,
        x='Orders',
        y='Region',
        orientation='h',
        color='Orders',
        color_continuous_scale='Viridis',
        title='Education Orders by Region'
    )
    fig2.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=0, r=0, t=40, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("""
    This bar chart shows the number of education orders by each region exactly as they appear in the data.  
    """)


# --------------------------
# Top 10 Schools by Revenue
# --------------------------
st.markdown("### 🏆 Top 10 Schools by Revenue")
st.markdown("""
The table lists the top ten schools by total revenue from purchases.  
This helps identify key accounts for relationship building and tailored offers.
""")
top_schools = edu_df.groupby('School Match')['Item Total'].sum().sort_values(ascending=False).head(10)
st.dataframe(top_schools, use_container_width=True)

# --------------------------
# Product Insights
# --------------------------
st.markdown("### 📦 Top Items Sold in Education Sector")
st.markdown("""
This bar chart shows the most popular product types sold to educational customers, measured by units.  
Understanding product preferences supports inventory and marketing decisions.
""")

top_items = edu_df.groupby("Item Type")["Quantity"].sum().sort_values(ascending=False)

fig4, ax4 = plt.subplots(figsize=(8, 4))
top_items.plot(kind='bar', color='seagreen', ax=ax4)
ax4.set_ylabel("Units")
ax4.set_title("Top Item Types Sold")
st.pyplot(fig4)

# --------------------------
# Pain Points Analysis
# --------------------------
pain_points = {
    "Limited Financial Resources": 9,
    "Environmental Compliance": 8,
    "Diverse Institutional Needs": 8,
    "Procurement Seasonality": 7,
    "Complex Procurement Processes": 7,
    "Technology Access Gaps": 6,
    "Inadequate IT Support Capacity": 6
}

df_pain = pd.DataFrame(list(pain_points.items()), columns=['Pain Point', 'Impact Score'])
df_pain.sort_values('Impact Score', ascending=True, inplace=True)

st.markdown("### 🚧 Pain Points in School Technology Procurement")
st.markdown("""
This bar plot ranks the major challenges schools face when purchasing technology, based on impact scores from 1 (low) to 10 (high).  
Identifying these pain points helps The iOutlet craft solutions that directly address school needs.
""")
st.markdown("This analysis highlights key challenges schools face when acquiring technology, helping tailor The iOutlet's value proposition.")

fig5, ax5 = plt.subplots(figsize=(8, 4))
sns.barplot(x='Impact Score', y='Pain Point', data=df_pain, palette='crest', ax=ax5)
ax5.set_title('Key Pain Points in UK School Technology Procurement')
ax5.set_xlabel('Impact (1 = Low, 10 = High)')
ax5.set_ylabel('')
st.pyplot(fig5)

# --------------------------
# Pain Point to Solution Mapping
# --------------------------
st.markdown("### 🧩 Pain Point–Solution Mapping")
st.markdown("The table below aligns each pain point with a tailored strategy from The iOutlet to maximise market fit and impact.")

pain_solution_data = [
    {"Pain Point": "Limited Financial Resources", "Proposed iOutlet Solution": "Offer cost-effective refurbished devices, bulk education discounts, and financing options."},
    {"Pain Point": "Environmental Compliance", "Proposed iOutlet Solution": "Highlight sustainability credentials, carbon offsetting, and e-waste reduction certifications."},
    {"Pain Point": "Diverse Institutional Needs", "Proposed iOutlet Solution": "Customise offerings by institution type (e.g. MATs, SEN schools) through flexible product and service bundles."},
    {"Pain Point": "Procurement Seasonality", "Proposed iOutlet Solution": "Plan inventory cycles around academic year peaks and offer pre-order bundles."},
    {"Pain Point": "Complex Procurement Processes", "Proposed iOutlet Solution": "Simplify ordering with dedicated account managers and pre-approved tender documentation."},
    {"Pain Point": "Technology Access Gaps", "Proposed iOutlet Solution": "Supply large-volume, affordable tablet/laptop bundles to close access gaps in low-income schools."},
    {"Pain Point": "Inadequate IT Support Capacity", "Proposed iOutlet Solution": "Provide optional setup support, remote diagnostics, and educational IT care packages."}
]

solution_df = pd.DataFrame(pain_solution_data)
st.dataframe(solution_df, use_container_width=True)

# --------------------------
# Strategic Action Plan Dashboard Section
# --------------------------
st.markdown("## 🧭 Strategic Insights & Recommendations")
st.markdown("""
This section outlines evidence-based strategic actions designed to align with schools’ needs and The iOutlet’s commercial and environmental goals.
""")

recommendations = [
    {
        "Action": "1. Build Education-Focused Device Bundles",
        "Details": "- Create multi-tiered bundles including refurbished devices, software, warranties, and setup support.\n- Position as full-service, deployment-ready solutions."
    },
    {
        "Action": "2. Join Key Public Procurement Frameworks",
        "Details": "- Apply to CCS, YPO, and ESPO to gain access to school procurement channels.\n- Highlight framework membership in all sales and marketing touchpoints."
    },
    {
        "Action": "3. Push Clear and Credible Sustainability Messaging",
        "Details": "- Provide schools with impact reports on carbon savings and e-waste reduction.\n- Back claims with third-party audits and include ESG metrics in proposals."
    },
    {
        "Action": "4. Run Seasonal Marketing Campaigns Aligned with School Calendars",
        "Details": "- Target budgeting (March) and procurement (July–August) cycles.\n- Use segmented CRM campaigns and urgency messaging to drive conversions."
    },
    {
        "Action": "5. Target Multi-Academy Trusts (MATs) Strategically",
        "Details": "- Prioritise MATs with centralised purchasing and larger budgets.\n- Assign account managers and tailor messaging around total cost of ownership."
    },
    {
        "Action": "6. Build Strategic Partnerships with ICT and EdTech Providers",
        "Details": "- Collaborate on bundled offerings with training, software, or IT support services.\n- Coordinate on joint campaigns and clearly define partner roles."
    },
    {
        "Action": "7. Track KPIs to Measure Impact and Guide Strategy",
        "Details": "- Use KPIs from each recommendation area to assess progress.\n- Adjust strategy based on real sales data, feedback, and market response."
    }
]


for rec in recommendations:
    with st.expander(rec["Action"]):
        st.markdown(rec["Details"])
# Trustpilot Ratings vs Competitors
# --------------------------
st.markdown("## 🌟 Trustpilot Reputation Comparison")
st.markdown("""
Trustpilot scores highlight how refurbished tech providers perform on customer satisfaction.  
The iOutlet ranks competitively with a 4.7 TrustScore, closely behind The Big Phone Store (4.8) and above many key rivals.  
This positions the brand as a trusted choice in a crowded market.
""")

# Manually collected Trustpilot data
trustpilot_data = {
    "Competitor": [
        "The Big Phone Store", "The iOutlet", "UR", "Reboxed", 
        "4Gadgets", "musicMagpie", "Mazuma Mobile", "Envirofone",
        "WeBuyAnyPhone", "Gadcet", "PhoneBox", "Smart Cellular"
    ],
    "Trustpilot Score": [4.8, 4.7, 4.6, 4.5, 4.4, 4.4, 4.3, 4.2, 4.1, 4.0, 3.9, 3.7],
    "Review Count": [7200, 6000, 7800, 1200, 2400, 322000, 16000, 11000, 1400, 400, 800, 300],
}

trust_df = pd.DataFrame(trustpilot_data).sort_values(by="Trustpilot Score", ascending=False)

# Plot the scores
fig_trust, ax_trust = plt.subplots(figsize=(10, 6))
sns.barplot(
    x="Trustpilot Score", 
    y="Competitor", 
    data=trust_df, 
    hue="Competitor", 
    palette="coolwarm", 
    ax=ax_trust, 
    dodge=False, 
    legend=False
)
ax_trust.set_xlim(0, 5)
ax_trust.set_xlabel("TrustScore (out of 5)")
ax_trust.set_title("Trustpilot Ratings of Refurbished Tech Competitors")
ax_trust.grid(axis='x', linestyle='--', alpha=0.6)
st.pyplot(fig_trust)

    
# --------------------------
# Filters & Export
# --------------------------
st.sidebar.markdown("## 🔍 Filter Options")

# Start with the full dataset
filtered_df = sales_df.copy()

# --- Region Filter ---
region_filter = st.sidebar.selectbox(
    "Select Region", 
    options=['All'] + sorted(filtered_df['Region'].dropna().unique())
)
if region_filter != "All":
    filtered_df = filtered_df[filtered_df['Region'] == region_filter]

# --- School Type Filter ---
school_type_filter = st.sidebar.selectbox(
    "Select School Type (e.g., Academy, Free School)", 
    options=['All'] + sorted(filtered_df['School Type'].dropna().unique())
)
if school_type_filter != "All":
    filtered_df = filtered_df[filtered_df['School Type'] == school_type_filter]

# --- Type Filter (Primary, Secondary, etc.) ---
type_filter = st.sidebar.selectbox(
    "Select Education Level (Primary / Secondary):",
    options=['All'] + sorted(filtered_df['Type'].dropna().unique())
)
if type_filter != "All":
    filtered_df = filtered_df[filtered_df['Type'] == type_filter]

# --- Trust Match Filter (excluding blanks) ---
trust_options = ['All'] + sorted(
    filtered_df['Trust Match']
    .dropna()
    .astype(str)
    .str.strip()
    .loc[lambda x: x != '']
    .unique()
)

trust_filter = st.sidebar.selectbox(
    "Select Trust Match sales", 
    options=trust_options
)

if trust_filter != 'All':
    filtered_df = filtered_df[filtered_df['Trust Match'] == trust_filter]


# --- Sidebar Metric Display ---
filtered_sales_total = filtered_df['Item Total'].sum()
filtered_sales_count = len(filtered_df)

st.sidebar.metric("🎯 Filtered Sales Revenue", f"£{filtered_sales_total:,.2f}")
st.sidebar.metric("🧾 Number of Sales", f"{filtered_sales_count:,}")






