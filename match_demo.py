import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
import uuid
import sqlite3
import json
from datetime import datetime

# In-memory company store (replace with database later)
if "companies" not in st.session_state:
    st.session_state.companies = []

DB_PATH = "assessments.db"

ASSESSMENT_SECTIONS = {
    "Finance": [
        "How strong is your cash flow management?",
        "How reliable are your financial forecasts?",
        "How diversified are your revenue streams?",
        "How well do you manage operational costs?",
        "How prepared are you for financial shocks?",
        "How mature is your budgeting process?"
    ],
    "Market": [
        "How clearly defined is your target customer profile?",
        "How strong is your competitive positioning?",
        "How effective is your market research process?",
        "How scalable is your go-to-market strategy?",
        "How strong is customer retention?",
        "How well does your offer fit market demand?"
    ],
    "Team": [
        "How strong are leadership capabilities?",
        "How clear are team roles and responsibilities?",
        "How effective is internal communication?",
        "How strong is talent retention?",
        "How developed are employee skills?",
        "How effective is performance management?"
    ],
    "Operations": [
        "How efficient are core business processes?",
        "How reliable is supply chain execution?",
        "How effective is quality control?",
        "How strong is your use of business systems and tools?",
        "How resilient are operations under disruption?",
        "How well are KPIs tracked and acted on?"
    ],
    "Governance": [
        "How clear is your decision-making structure?",
        "How strong are legal and compliance controls?",
        "How strong is risk management governance?",
        "How transparent is reporting to stakeholders?",
        "How mature are policy and process documents?",
        "How strong are ethics and accountability practices?"
    ]
}

SECTION_RECOMMENDATIONS = {
    "Finance": [
        "Build a rolling 12-month cash flow forecast and review it monthly.",
        "Set a cost-control target and track margin by product/service line.",
        "Create a contingency reserve equivalent to at least 3 months of fixed costs.",
        "Introduce quarterly scenario planning for best/base/worst cases.",
        "Standardize budget ownership by department with monthly variance reviews."
    ],
    "Market": [
        "Refresh customer segmentation using recent buying behavior data.",
        "Document your competitive differentiation in a one-page value proposition.",
        "Run structured customer interviews each quarter.",
        "Pilot at least one new channel with measurable CAC and conversion targets.",
        "Implement a customer churn analysis and retention action plan."
    ],
    "Team": [
        "Define role scorecards with clear outcomes for each key position.",
        "Set biweekly 1:1 check-ins between managers and team members.",
        "Create an annual training plan tied to strategic priorities.",
        "Introduce a lightweight performance review cycle every 6 months.",
        "Launch an employee feedback pulse survey and track action items."
    ],
    "Operations": [
        "Map and optimize your top 3 critical workflows end-to-end.",
        "Track operational KPIs weekly with owners and thresholds.",
        "Define supplier backup options for high-risk dependencies.",
        "Implement periodic quality audits and corrective action logs.",
        "Automate repetitive manual tasks using simple workflow tools."
    ],
    "Governance": [
        "Formalize a decision rights matrix for leadership and teams.",
        "Review compliance obligations annually with an assigned owner.",
        "Maintain a live risk register with probability/impact scoring.",
        "Publish a monthly management report with key financial and operational metrics.",
        "Update core policies (ethics, procurement, approvals) and train staff annually."
    ]
}


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS assessments (
            id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            total_score REAL NOT NULL,
            section_scores_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS assessment_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id TEXT NOT NULL,
            section_name TEXT NOT NULL,
            question_text TEXT NOT NULL,
            score INTEGER NOT NULL,
            FOREIGN KEY (assessment_id) REFERENCES assessments(id)
        )
        """
    )
    conn.commit()
    conn.close()


def compute_assessment_scores(answers):
    section_scores = {}
    total_raw = 0
    max_total = 0

    for section, questions in ASSESSMENT_SECTIONS.items():
        section_answers = answers[section]
        raw_score = sum(section_answers)
        max_section = len(questions) * 5
        section_scores[section] = round((raw_score / max_section) * 100, 2)
        total_raw += raw_score
        max_total += max_section

    total_score = round((total_raw / max_total) * 100, 2)
    return section_scores, total_score


def get_top_recommendations(section_scores):
    ordered_sections = sorted(section_scores.items(), key=lambda item: item[1])
    recommendations = []
    for section, _ in ordered_sections:
        for rec in SECTION_RECOMMENDATIONS[section]:
            recommendations.append((section, rec))
            if len(recommendations) == 5:
                return recommendations
    return recommendations


def save_assessment(company, answers, section_scores, total_score):
    assessment_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO assessments (id, company_id, company_name, created_at, total_score, section_scores_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            assessment_id,
            company["id"],
            company["name"],
            created_at,
            total_score,
            json.dumps(section_scores)
        )
    )

    answer_rows = []
    for section, questions in ASSESSMENT_SECTIONS.items():
        for idx, question in enumerate(questions):
            answer_rows.append((assessment_id, section, question, answers[section][idx]))

    conn.executemany(
        """
        INSERT INTO assessment_answers (assessment_id, section_name, question_text, score)
        VALUES (?, ?, ?, ?)
        """,
        answer_rows
    )
    conn.commit()
    conn.close()


init_db()

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
pages = ["Register Company", "Find Matches", "Assessment", "View Past Assessments"]
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

# ----------------------------
# PAGE 3: Assessment
# ----------------------------
elif page == "Assessment":
    st.title("📊 Business Assessment")
    if not st.session_state.companies:
        st.warning("Please register a company before completing an assessment.")
    else:
        company = st.selectbox("Select Company", st.session_state.companies, format_func=lambda x: x["name"])
        st.caption("Score each question from 1 (low) to 5 (high).")

        answers = {}
        with st.form("assessment_form"):
            for section, questions in ASSESSMENT_SECTIONS.items():
                st.subheader(section)
                section_answers = []
                for idx, question in enumerate(questions):
                    score = st.slider(
                        question,
                        min_value=1,
                        max_value=5,
                        value=3,
                        key=f"{section}_{idx}"
                    )
                    section_answers.append(score)
                answers[section] = section_answers

            submitted = st.form_submit_button("Calculate & Save Assessment")

        if submitted:
            section_scores, total_score = compute_assessment_scores(answers)
            recommendations = get_top_recommendations(section_scores)
            save_assessment(company, answers, section_scores, total_score)

            st.success("Assessment saved successfully.")
            st.metric("Total Score (0-100)", total_score)

            st.subheader("Section Breakdown")
            for section, score in section_scores.items():
                st.write(f"**{section}:** {score}")
                st.progress(min(score / 100, 1.0))

            st.subheader("Top 5 Recommendations")
            for i, (section, rec) in enumerate(recommendations, start=1):
                st.markdown(f"{i}. **{section}** — {rec}")

# ----------------------------
# PAGE 4: Past Assessments
# ----------------------------
elif page == "View Past Assessments":
    st.title("🗂️ Past Assessments")
    if not st.session_state.companies:
        st.warning("No companies available yet. Register a company first.")
    else:
        company = st.selectbox("Select Company", st.session_state.companies, format_func=lambda x: x["name"])
        conn = get_db_connection()
        rows = conn.execute(
            """
            SELECT id, created_at, total_score, section_scores_json
            FROM assessments
            WHERE company_id = ?
            ORDER BY created_at DESC
            """,
            (company["id"],)
        ).fetchall()
        conn.close()

        if not rows:
            st.info("No assessments saved for this company yet.")
        else:
            for row in rows:
                section_scores = json.loads(row["section_scores_json"])
                with st.expander(f"{row['created_at']} — Total Score: {row['total_score']}"):
                    st.write("**Section Scores**")
                    for section, score in section_scores.items():
                        st.write(f"- {section}: {score}")

