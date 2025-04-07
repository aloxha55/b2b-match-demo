import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

    # Product matching
    prod_score = jaccard_similarity(buyer['needs'], supplier['offers'])
    score += prod_score * weights['product']
    if prod_score > 0:
        explanation.append("They offer what you need.")

    # Sector matching
    sect_score = jaccard_similarity(buyer['sectors'], supplier['sectors'])
    score += sect_score * weights['sector']
    if sect_score > 0:
        explanation.append("You're in compatible sectors.")

    # Geography match
    if supplier['country'] in buyer['targets']:
        score += weights['geo']
        explanation.append(f"They are in your target market: {supplier['country']}.")

    # Certifications
    cert_score = jaccard_similarity(buyer['certs'], supplier['certs'])
    score += cert_score * weights['certs']
    if cert_score > 0:
        explanation.append("You share similar certifications.")

    # Company size
    if buyer['size'] == supplier['size']:
        score += weights['size']
        explanation.append("You're similar in size.")

    # Export readiness
    if buyer['needs_exporter'] and supplier['export_ready']:
        score += weights['export']
        explanation.append("They are export-ready.")

    # Partnership types
    partner_score = jaccard_similarity(buyer['partner_types'], supplier['partner_types'])
    score += partner_score * weights['partnership']
    if partner_score > 0:
        explanation.append("You're open to the same partnership type.")

    # Activity level (dummy assumption)
    score += weights['activity'] * 0.8
    explanation.append("They are recently active.")

    return round(score, 2), explanation

# ----------------------------
# Streamlit App UI
# ----------------------------

st.set_page_config(page_title="B2B Matchmaking Platform", layout="wide")
st.title("🤝 AI-Powered B2B Matchmaking Platform")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔷 Buyer Profile")

    buyer = {
        "needs": st.multiselect("What do you need?", ["packaging", "IT services", "logistics", "labeling", "consulting"]),
        "sectors": st.multiselect("Your sectors", ["Agriculture", "Textiles", "ICT", "Manufacturing", "Retail"]),
        "targets": st.multiselect("Target countries", ["Germany", "France", "USA", "UK", "Netherlands"]),
        "certs": st.multiselect("Certifications", ["ISO 9001", "GOTS", "CE", "Fair Trade", "Organic"]),
        "size": st.selectbox("Company size", ["micro", "small", "medium", "large"]),
        "needs_exporter": st.checkbox("Looking for exporters?", value=True),
        "partner_types": st.multiselect("Preferred partnership types", ["buyer-supplier", "JV", "reseller", "franchise"]),
        "country": "Kosovo"
    }

with col2:
    st.subheader("🟢 Supplier Profile")

    supplier = {
        "offers": st.multiselect("What do you offer?", ["packaging", "labeling", "IT services", "logistics", "consulting"]),
        "sectors": st.multiselect("Your sectors", ["Agriculture", "Textiles", "ICT", "Manufacturing", "Retail"], key="supplier_sectors"),
        "certs": st.multiselect("Certifications", ["ISO 9001", "GOTS", "CE", "Fair Trade", "Organic"], key="supplier_certs"),
        "size": st.selectbox("Company size", ["micro", "small", "medium", "large"], key="supplier_size"),
        "export_ready": st.checkbox("Are you export-ready?", value=True),
        "partner_types": st.multiselect("Available for partnerships", ["buyer-supplier", "JV", "reseller", "franchise"], key="supplier_partner_types"),
        "country": st.selectbox("Country of operation", ["Germany", "France", "USA", "UK", "Netherlands"])
    }

st.markdown("---")

if st.button("🔍 Match Now"):
    score, explanation = compute_match_score(buyer, supplier)
    st.success(f"Match Score: **{score}%**")

    st.markdown("### 🤔 Why this match?")
    for reason in explanation:
        st.markdown(f"✅ {reason}")

