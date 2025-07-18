import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io
import seaborn as sns

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
st.set_page_config(page_title="iOutlet Education Expansion Dashboard", layout="wide")
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

# First row with 4 columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"£{total_revenue:,.2f}")
col2.metric("🎓 Education Revenue", f"£{edu_revenue:,.2f}")
col3.metric("📦 Units Sold", f"{int(total_units):,}")
col4.metric("🏫 Schools Reached", f"{schools_reached}")

# Second row with 4 columns
col5, col6, col7, col8 = st.columns(4)
col5.metric("⚖️ Repeat Orders %", f"{repeat_order_rate:.1f}%")
col6.metric("🏫 Unique School Types", f"{total_schools_by_school_type}")
col7.metric("🏷️ Unique Types", f"{total_schools_by_type}")
col8.metric("🤝 Trust Matched Sales", f"{total_trust_matched_sales}")


# Optionally display unique trust schools count too (you can add as metric or text)
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
# School Segmentation
# --------------------------

st.markdown("### 🏫 Orders by School Type")

school_types = edu_df["School Type"].dropna().value_counts()



regions = edu_df["Region"].dropna().value_counts()
colA, colB = st.columns([3, 2])
with colA:
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    school_types.plot(kind='bar', color='dodgerblue', ax=ax2)
    ax2.set_title("Orders by School Type")
    st.pyplot(fig2)
    st.markdown("""
This bar chart displays the number of orders placed by different school types, such as primary, secondary, and special education schools.  
It helps us understand which school segments are purchasing most frequently and guides targeted sales strategies.
""")

with colB:
    fig3, ax3 = plt.subplots(figsize=(6, 6))
    regions.plot(kind='pie', autopct='%1.1f%%', ax=ax3, textprops={'fontsize': 8})
    st.markdown("### 🌍 Orders by Region")
    ax3.set_title("Orders by Region")
    ax3.axis('equal')
    st.pyplot(fig3)
    st.markdown("""
The pie chart illustrates the distribution of orders across UK regions.  
This reveals geographical hotspots of demand and potential regions for expansion efforts.
""")
    
# --------------------------
# Regional Sales Breakdown
# --------------------------
st.markdown("### 🌍 Regional Sales Breakdown")
st.markdown("""
This bar chart presents total revenue generated from each UK region.  
It highlights lucrative areas and sales distribution, helping focus marketing and sales efforts.
""")

# Clean and normalize the 'Region' column
edu_df['Region'] = edu_df['Region'].astype(str).str.strip().str.title()

# Filter out invalid or missing regions
valid_regions_df = edu_df[(edu_df['Region'] != '') & (edu_df['Region'].str.lower() != 'nan')]

# Aggregate revenue by region
region_sales = valid_regions_df.groupby('Region')['Item Total'].sum().sort_values(ascending=False)

# Plotting with Seaborn for a nicer style
import matplotlib.ticker as ticker

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=region_sales.values, y=region_sales.index, palette='viridis', ax=ax)

# Format x-axis as £ currency with commas
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'£{int(x):,}'))

ax.set_xlabel("Revenue (£)")
ax.set_ylabel("Region")
ax.set_title("Total Sales Revenue by Region")
ax.grid(axis='x', linestyle='--', alpha=0.7)

# Tight layout for spacing
plt.tight_layout()

st.pyplot(fig)


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
    'Limited Financial Resources': 9,
    'Procurement Seasonality': 7,
    'Technology Access Gaps': 6,
    'Environmental Compliance': 8,
    'Inadequate IT Support Capacity': 6,
    'Complex Procurement Processes': 7,
    'Diverse Institutional Needs': 8
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
    {"Pain Point": "Procurement Seasonality", "Proposed iOutlet Solution": "Plan inventory cycles around academic year peaks and offer pre-order bundles."},
    {"Pain Point": "Technology Access Gaps", "Proposed iOutlet Solution": "Supply large-volume, affordable tablet/laptop bundles to close access gaps in low-income schools."},
    {"Pain Point": "Environmental Compliance", "Proposed iOutlet Solution": "Highlight sustainability credentials, carbon offsetting, and e-waste reduction certifications."},
    {"Pain Point": "Inadequate IT Support Capacity", "Proposed iOutlet Solution": "Provide optional setup support, remote diagnostics, and educational IT care packages."},
    {"Pain Point": "Complex Procurement Processes", "Proposed iOutlet Solution": "Simplify ordering with dedicated account managers and pre-approved tender documentation."},
    {"Pain Point": "Diverse Institutional Needs", "Proposed iOutlet Solution": "Customise offerings by institution type (e.g. MATs, SEN schools) through flexible product and service bundles."}
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
    {"Action": "1. Offer Education-Specific Device Packages", "Details": "- Bundle iPads or MacBooks with cases, charging carts, and pre-installed software.\n- Enhances usability and aligns with school tech needs."},
    {"Action": "2. Provide Financial Flexibility Through Leasing and Trade-In Programs", "Details": "- Introduce leasing, trade-in and subscription plans to support affordability and device refresh."},
    {"Action": "3. Champion Environmental Sustainability in B2B Outreach", "Details": "- Highlight carbon reductions, certified refurbishing, and tree planting schemes."},
    {"Action": "4. Launch a Tailored Procurement Platform for Schools", "Details": "- Create a dedicated interface with quotes, framework tools, and education-specific pricing."},
    {"Action": "5. Introduce Technical Support and Training Services", "Details": "- Offer onboarding, remote IT help, and training with education bulk orders."},
    {"Action": "6. Pursue Consortia and Framework Inclusion", "Details": "- Join Crown Commercial Services and MAT-level procurement groups."},
    {"Action": "7. Utilise Analytical Dashboards to Guide Sales Strategy", "Details": "- Apply dashboard insights to segment school types and regional demand."}
]

for rec in recommendations:
    with st.expander(rec["Action"]):
        st.markdown(rec["Details"])
# --------------------------
# Trustpilot Ratings vs Competitors
# --------------------------
st.markdown("## 🌟 Trustpilot Reputation Comparison")
st.markdown("""
This chart shows how The iOutlet's Trustpilot rating compares to key competitors in the refurbished tech market.
It reflects customer satisfaction based on TrustScore (0–5 scale) and helps assess brand reputation.
""")

# Manually collected Trustpilot data
trustpilot_data = {
    "Competitor": [
        "The iOutlet", "musicMagpie", "The Big Phone Store", "Envirofone",
        "Mazuma Mobile", "UR", "WeBuyAnyPhone", "PhoneBox",
        "4Gadgets", "Reboxed", "Smart Cellular", "Gadcet"
    ],
    "Trustpilot Score": [4.7, 4.4, 4.8, 4.2, 4.3, 4.6, 4.1, 3.9, 4.4, 4.5, 3.7, 4.0],
    "Review Count": [6000, 322000, 7200, 11000, 16000, 7800, 1400, 800, 2400, 1200, 300, 400],
    "URL": [
        "https://uk.trustpilot.com/review/theioutlet.com",
        "https://uk.trustpilot.com/review/www.musicmagpie.co.uk",
        "https://uk.trustpilot.com/review/www.thebigphonestore.co.uk",
        "https://uk.trustpilot.com/review/www.envirofone.com",
        "https://uk.trustpilot.com/review/www.mazumamobile.com",
        "https://uk.trustpilot.com/review/ur.co.uk",
        "https://uk.trustpilot.com/review/webuyanyphone.com",
        "https://uk.trustpilot.com/review/phonebox.co.uk",
        "https://uk.trustpilot.com/review/www.4gadgets.co.uk",
        "https://uk.trustpilot.com/review/reboxed.co",
        "https://uk.trustpilot.com/review/smartcellular.co.uk",
        "https://uk.trustpilot.com/review/gadcet.com"
    ]
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
    legend=False
)
ax_trust.set_xlim(0, 5)
ax_trust.set_xlabel("TrustScore (out of 5)")
ax_trust.set_title("Trustpilot Ratings of Refurbished Tech Competitors")
ax_trust.grid(axis='x', linestyle='--', alpha=0.6)
st.pyplot(fig_trust)

# Optional Table
with st.expander("📋 View Detailed Trustpilot Ratings"):
    st.dataframe(trust_df[['Competitor', 'Trustpilot Score', 'Review Count', 'URL']], use_container_width=True)
    
# --------------------------
# Filters & Export
# --------------------------
st.sidebar.markdown("## 🔍 Filter Options")

# -- Base copy to avoid modifying original --
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

# --- 'Type' Filter (e.g., Primary, Secondary) ---
selected_types = st.sidebar.selectbox(
    "Select School Category (e.g., Primary, Secondary):",
    options=sorted(filtered_df['Type'].dropna().unique()),
    default=sorted(filtered_df['Type'].dropna().unique())
)
if selected_types:
    filtered_df = filtered_df[filtered_df['Type'].isin(selected_types)]

# --- Sidebar Metric Display ---
st.sidebar.metric("🎯 Filtered Sales", f"£{filtered_df['Item Total'].sum():,.2f}")

# --- Download Filtered CSV ---
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Download Filtered Data", csv, "filtered_data.csv", "text/csv")

