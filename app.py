import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt


# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("cleaned_amazon_products.csv")
#st.write("Dataset Loaded Successfully")

# Load Similarity Matrix
with open("similarity.pkl", "rb") as f:
    cosine_sim = pickle.load(f)
#st.write("Similarity Loaded")

# Load Product Indices
with open("indices.pkl", "rb") as f:
    indices = pickle.load(f)
#st.write("Indices Loaded")

# Initialize session state
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = None


# -----------------------------
# Recommendation Function
# -----------------------------

def recommend_products(search_text):

    matches = df[df["name"].str.contains(search_text, case=False, na=False)]

    if matches.empty:
        return None

    selected_product = matches.iloc[0]["name"]
    idx = indices[selected_product]

    sim_scores = list(enumerate(cosine_sim[idx]))

    # Highest similarity first
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Skip selected product itself
    sim_scores = sim_scores[1:6]

    product_indices = [i[0] for i in sim_scores]

    result = df.iloc[product_indices][
        ["name", "ratings", "discount_price", "actual_price", "link"]
    ]

    return result

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="AI AC Recommendation System", layout="wide")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🤖 AI AC Recommendation")

st.sidebar.info("""
### Technologies Used
- Python
- Streamlit
- Pandas
- Scikit-learn
- Content-Based Filtering
- Cosine Similarity
""")

st.sidebar.success(f"Total Products: {len(df)}")

# -----------------------------
# Main UI
# -----------------------------
st.title("🤖 AI-Based Smart Air Conditioner Recommendation System")

st.markdown("""
Welcome to the **AI-Based Smart Air Conditioner Recommendation System**.

This application recommends similar Air Conditioners based on
**Content-Based Filtering** and **Cosine Similarity**.

Simply enter an AC brand or product name below to get the top 5 recommendations.
""")

st.info(
    "This system recommends products based on feature similarity. "
    "Recommendations may include different brands with similar specifications."
)

product = st.text_input("🔍 Enter Product Name")

if st.button("Recommend"):

    recommendations = recommend_products(product)

    if recommendations is None:
        st.error("No product found.")
        st.session_state["recommendations"] = None

    else:
        st.session_state["recommendations"] = recommendations


if st.session_state["recommendations"] is not None:

    recommendations = st.session_state["recommendations"]

    st.success("Top 5 Recommended Products")
    st.metric("Recommended Products", len(recommendations))
    st.dataframe(recommendations)

    # -----------------------------
    # Product Comparison Feature
    # -----------------------------

    st.subheader("⚖️ Compare AC Products")

    selected_compare = st.multiselect(
        "Select products to compare",
        recommendations["name"].tolist(),
        max_selections=3
    )


    if selected_compare:

        compare_df = recommendations[
            recommendations["name"].isin(selected_compare)
        ].copy()


        st.write("### Comparison Table")


        st.table(
            compare_df[
                ["name", "ratings", "discount_price", "actual_price"]
            ].set_index("name").T
        )


        compare_df["ratings"] = pd.to_numeric(
            compare_df["ratings"],
            errors="coerce"
        )


        if compare_df["ratings"].notna().any():

            winner = compare_df.loc[
                compare_df["ratings"].idxmax()
            ]

            st.success(
                f"🏆 AI Winner: {winner['name']}\n\n"
                f"⭐ Rating: {winner['ratings']}"
            )


    # -----------------------------
    # Buy Now Links
    # -----------------------------

    st.subheader("🛒 Buy Now")

    for i, row in recommendations.iterrows():

        st.write(f"### {row['name']}")
        st.write(f"⭐ Rating: {row['ratings']}")
        st.write(f"💰 Price: {row['discount_price']}")
        st.markdown(f"[🛍 Buy Now on Amazon]({row['link']})")
        st.write("---")


    # -----------------------------
    # Charts
    # -----------------------------

    chart_data = recommendations.copy()

    chart_data["ratings"] = pd.to_numeric(
        chart_data["ratings"],
        errors="coerce"
    )


    chart_data["discount_price"] = (
        chart_data["discount_price"]
        .astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
    )


    chart_data["discount_price"] = pd.to_numeric(
        chart_data["discount_price"],
        errors="coerce"
    )


    st.subheader("⭐ Ratings Comparison")
    st.bar_chart(
        chart_data.set_index("name")["ratings"]
    )


    st.subheader("💰 Price Comparison")
    st.bar_chart(
        chart_data.set_index("name")["discount_price"]
    )


    # -----------------------------
    # Pie Chart
    # -----------------------------

    st.subheader("🥧 Brand Distribution")


    fig, ax = plt.subplots()


    brand_count = (
        recommendations["name"]
        .str.split()
        .str[0]
        .value_counts()
    )


    ax.pie(
        brand_count,
        labels=brand_count.index,
        autopct="%1.1f%%"
    )


    ax.set_title("Brand Distribution")


    st.pyplot(fig)