import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# --- Matching logic ---
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

    # Geographic relevance
    if supplier['country'] in buyer['targets']:
        score += weights['geo']
        explanation.append(f"They are in your target market: {supplier['country']}.")

    # Certifications
    cert_score = jaccard_similarity(buyer['certs'], supplier['certs'])
    score += cert_score * weights['certs']
    if cert_score > 0:
        explanation.append("You share similar certifications.")

    # Size match
    if buyer['size'] == supplier['size']:
        score += weights['size']
        explanation.append("You're similar in size.")

    # Export readiness
    if buyer['needs_exporter'] and supplier['export_ready']:
        score += weights['export']
        explanation.append("They are export-ready.")

    # Partnership type
    partner_score = jaccard_similarity(buyer['partner_types'], supplier['partner_types'])
    score += partner_score * weights['partnership']
    if partner_score > 0:
        explanation.append("They're open to the same partnership type.")

    # Assume both are active
    score += weights['activity'] * 0.8
    explanation.append("They are recently active.")

    return round(score, 2), explanation


# --- Streamlit UI ---
st.title("🤝 B2B Matchmaking Demo")

st.subheader("Buyer Profile")
buyer = {
    "needs": st.multiselect("Products/Services Needed", ["packaging", "IT services", "logistics", "labeling"]),
    "sectors": st.multiselect("Sectors", ["Agriculture", "Textiles", "ICT", "Manufacturing"]),
    "targets": st.multiselect("Target Markets", ["Germany", "France", "USA", "UK"]),
    "certs": st.multiselect("Certifications", ["ISO 9001", "GOTS", "CE"]),
    "size": st.selectbox("Company Size", ["micro", "small", "medium", "large"]),
    "needs_exporter": st.checkbox("Needs Exporter?", value=True),
    "partner_types": st.multiselect("Preferred Partnership Types", ["buyer-supplier", "JV", "reseller"]),
    "country": "Kosovo"
}

st.subheader("Supplier Profile")
supplier = {
    "offers": st.multiselect("Products/Services Offered", ["packaging", "labeling", "IT services", "logistics"]),
    "sectors": st.multiselect("Sectors (Supplier)", ["Agriculture", "Textiles", "ICT", "Manufacturing"], key="supplier_sectors"),
    "certs": st.multiselect("Certifications (Supplier)", ["ISO 9001", "GOTS", "CE"], key="supplier_certs"),
    "size": st.selectbox("Company Size (Supplier)", ["micro", "small", "medium", "large"], key="supplier_size"),
    "export_ready": st.checkbox("Export Ready?", value=True),
    "partner_types": st.multiselect("Partner Types", ["buyer-supplier", "JV", "reseller"], key="supplier_partner_types"),
    "country": st.selectbox("Supplier Country", ["Germany", "France", "USA", "UK"])
}

if st.button("🔍 Match"):
    score, explanation = compute_match_score(buyer, supplier)
    st.success(f"Match Score: {score}%")
    st.write("### Why this match?")
    for reason in explanation:
        st.markdown(f"✅ {reason}")
