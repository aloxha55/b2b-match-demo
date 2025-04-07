import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
import uuid

# In-memory company store (replace with database later)
if "companies" not in st.session_state:
    st.session_state.companies = []

# ----------------------------
# AI Match Scoring Functions
# ----------------------------

def jaccard_similarity(set1, set2):
    set1, set2 = set(set1), set(set2)
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

def compute_match_score(buyer, supplier):
    score = 0
    explanation = []

    weights = {
        'product': 35,
        'sector': 15,
        'geo': 10,
        'certs': 10,
        'size': 5,
        'export': 5,
        'partnership': 10,
        'activity': 10
    }

    prod_score = jaccard_similarity(buyer['needs'], supplier['offers'])
    score += prod_score * weights['product']
    if prod_score > 0:
        explanation.append("They offer what you need.")

    sect_score = jaccard_similarity(buyer['sectors'], supplier['sectors'])
    score += sect_score * weights['sector']
    if sect_score > 0:
        explanation.append("You're in compatible sectors.")

    if supplier['country'] in buyer['targets']:
        score += weights['geo']
        explanation.append(f"They are in your target market: {supplier['country']}.")

    cert_score = jaccard_similarity(buyer['certs'], supplier['certs'])
    score += cert_score * weights['certs']
    if cert_score > 0:
        explanation.append("You share similar certifications.")

    if buyer['size'] == supplier['size']:
        score += weights['size']
        explanation.append("You're similar in size.")

    if buyer['needs_exporter'] and supplier['export_ready']:
        score += weights['export']
        explanation.append("They are export-ready.")

    partner_score = jaccard_similarity(buyer['partner_types'], supplier['partner_types'])
    score += partner_score * weights['partnership']
    if partner_score > 0:
        explanation.append("They're open to the same partnership type.")

    score += weights['activity'] * 0.8
    explanation.append("They are recently active.")

    return round(score, 2), explanation

# ----------------------------
# Page Navigation
# ----------------------------

st.set_page_config(page_title="B2B Matchmaking", layout="wide")
pages = ["Register Company", "Find Matches"]
page = st.sidebar.radio("📂 Navigate", pages)

# ----------------------------
# PAGE 1: Company Registration
# ----------------------------
if page == "Register Company":
    st.title("🏢 Company Registration")
    with st.form("company_form"):
        name = st.text_input("Company Name")
        role = st.radio("Acting as", ["Buyer", "Supplier"])
        country = st.selectbox("Country", ["Kosovo", "Germany", "France", "USA", "UK", "Netherlands"])
        size = st.selectbox("Company Size", ["micro", "small", "medium", "large"])
        sectors = st.multiselect("Sectors", ["Agriculture", "Textiles", "ICT", "Manufacturing", "Retail"])

        offers = st.multiselect("Products/Services Offered", ["packaging", "labeling", "IT services", "logistics", "consulting"]) if role == "Supplier" else []
        needs = st.multiselect("Products/Services Needed", ["packaging", "labeling", "IT services", "logistics", "consulting"]) if role == "Buyer" else []

        certs = st.multiselect("Certifications", ["ISO 9001", "GOTS", "CE", "Fair Trade", "Organic"])
        export_ready = st.checkbox("Export Ready?", value=True)
        needs_exporter = st.checkbox("Looking for Exporter?", value=True) if role == "Buyer" else False
        partner_types = st.multiselect("Preferred Partnership Types", ["buyer-supplier", "JV", "reseller", "franchise"])
        targets = st.multiselect("Target Countries", ["Germany", "France", "USA", "UK", "Netherlands"]) if role == "Buyer" else []

        submitted = st.form_submit_button("✅ Register Company")

        if submitted:
            company = {
                "id": str(uuid.uuid4()),
                "name": name,
                "role": role,
                "country": country,
                "size": size,
                "sectors": sectors,
                "offers": offers,
                "needs": needs,
                "certs": certs,
                "export_ready": export_ready,
                "needs_exporter": needs_exporter,
                "partner_types": partner_types,
                "targets": targets
            }
            st.session_state.companies.append(company)
            st.success("Company registered successfully!")

# ----------------------------
# PAGE 2: Matchmaking Dashboard
# ----------------------------
elif page == "Find Matches":
    st.title("🔍 AI-Powered Matchmaking")

    buyers = [c for c in st.session_state.companies if c['role'] == 'Buyer']
    suppliers = [c for c in st.session_state.companies if c['role'] == 'Supplier']

    if not buyers or not suppliers:
        st.warning("Please register at least one buyer and one supplier.")
    else:
        buyer = st.selectbox("Select Buyer", buyers, format_func=lambda x: x['name'])
        st.markdown("---")

        st.subheader(f"🔗 Top Matches for **{buyer['name']}**")
        top_matches = []
        for supplier in suppliers:
            score, reasons = compute_match_score(buyer, supplier)
            top_matches.append((supplier, score, reasons))

        top_matches = sorted(top_matches, key=lambda x: -x[1])[:5]

        for supplier, score, reasons in top_matches:
            with st.expander(f"✅ {supplier['name']} — Match Score: {score}%"):
                st.write("**Country:**", supplier['country'])
                st.write("**Sectors:**", ", ".join(supplier['sectors']))
                st.write("**Offers:**", ", ".join(supplier['offers']))
                st.write("**Certifications:**", ", ".join(supplier['certs']))
                st.write("**Why matched:**")
                for r in reasons:
                    st.markdown(f"- {r}")


