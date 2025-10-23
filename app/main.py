import streamlit as st
import pandas as pd
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import os

# ---------------------------
# UI constants
# ---------------------------
BG_COLOR = "#f1e7ca"
TEXT_COLOR = "#266130"
LOGO_PATH = "logo.jpg"  # adjust if your logo is in a subfolder

# ---------------------------
# CSS styling (injected)
# ---------------------------
STYLE = f"""
<style>
/* ===== Base page styling ===== */
.stApp {{
    background-color: {BG_COLOR} !important;
    color: {TEXT_COLOR} !important;
}}

[data-testid="stAppViewContainer"] {{
    background-color: {BG_COLOR} !important;
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

[data-testid="stSidebar"] {{
    background-color: #ffffffcc;
}}

/* ===== Containers & cards ===== */
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}}

.card {{
    background: rgba(255,255,255,0.8);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    color: {TEXT_COLOR};
}}

/* ===== Title & headings ===== */
.app-title {{
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 0.5rem;
}}
.app-title h1 {{
    font-size: 2rem;
    color: {TEXT_COLOR};
    font-weight: 700;
    margin: 0;
}}

/* ===== Buttons ===== */
.stButton>button {{
    background-color: #eaf7ea;
    color: {TEXT_COLOR};
    border: 1px solid rgba(38,97,48,0.25);
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}}
.stButton>button:hover {{
    background-color: #d9f5d9;
}}

/* ===== Inputs ===== */
input, select, textarea {{
    border-radius: 8px !important;
}}
</style>
"""


def render_header():
    # Inject CSS
    st.markdown(STYLE, unsafe_allow_html=True)

    # Header with logo and title
    col1, col2 = st.columns([1, 8])
    with col1:
        # try show logo; if not found, skip gracefully
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=120)
        else:
            # small placeholder space so layout keeps
            st.markdown("<div style='height:72px;'></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(
            "<div class='app-title card'><h1>📧 Cold Email Generator</h1></div>",
            unsafe_allow_html=True
        )
    st.markdown("---")

def create_streamlit_app(llm, portfolio):
    render_header()

    # wrap controls in a card
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    url_input = st.text_input(
        "Enter a URL:",
        value="https://www.google.com/about/careers/applications/jobs/results/93158356268524230-customer-solutions-engineer-data-analytics-google-cloud"
    )

    # Sender customization
    sender_name = st.text_input("Sender name:", value="Mrudula")
    company_name = st.text_input("Company name:", value="Artgen_z")
    sender_title = st.text_input("Sender title / role (optional):", value="BDE")

    st.markdown("### Email style options")

    # New controls: tone, length, email type
    tone = st.selectbox("Email tone", ["Formal", "Friendly", "Persuasive", "Neutral"], index=0)
    length = st.selectbox("Email length", ["Short", "Medium", "Detailed"], index=1)
    email_type = st.selectbox("Email type", ["Job Application", "Collaboration", "Partnership / Pitch", "Introductory"], index=0)

    st.markdown("---")
    st.subheader("Portfolio (CSV)")
    st.write("Upload a CSV with columns `Techstack` and `Links` (Links can be GitHub/website).")
    uploaded_file = st.file_uploader("Upload portfolio CSV (optional)", type=["csv"])

    # preview and load uploaded csv into portfolio when provided
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            st.write("Preview of uploaded portfolio:")
            st.dataframe(uploaded_df.head(10))
            if st.button("Use uploaded portfolio"):
                portfolio.load_portfolio(uploaded_df)
                st.success("Uploaded portfolio loaded into vector store.")
        except Exception as e:
            st.error(f"Failed to read uploaded CSV: {e}")

    st.markdown("</div>", unsafe_allow_html=True)  # close card

    submit_button = st.button("Submit", key="submit_main")

    if submit_button:
        try:
            if not url_input.strip():
                st.error("Please enter a valid URL.")
                return

            # 1️⃣ Load and clean page data
            loader = WebBaseLoader([url_input])
            page_content = loader.load().pop().page_content
            clean_data = clean_text(page_content)

            # 2️⃣ Ensure portfolio is loaded (if not loaded yet, load default CSV)
            portfolio.load_portfolio()

            # 3️⃣ Extract jobs from page
            jobs = llm.extract_jobs(clean_data)

            # 4️⃣ Generate emails for each job
            for idx, job in enumerate(jobs):
                job_skills = job.get('skills', [])
                if isinstance(job_skills, str):
                    job_skills = [job_skills]

                # Query portfolio links for this job
                links = portfolio.query_links(job_skills)

                # Generate cold email using provided sender info and style options
                email = llm.write_mail(
                    job,
                    links,
                    sender_name=sender_name,
                    company_name=company_name,
                    sender_title=sender_title,
                    tone=tone,
                    length=length,
                    email_type=email_type
                )

                # Ensure escaped newlines are actual newlines
                if isinstance(email, str):
                    email = email.replace("\\n", "\n")

                st.markdown(f"### ✉️ Email #{idx + 1}: {job.get('role', 'Unknown Role')}")
                # Show email in a text area with preserved formatting and ability to copy
                st.text_area(f"Email preview — Job #{idx+1}", value=email.strip(), height=260)

                # Also provide a downloadable txt button for convenience
                st.download_button(
                    label="Download email (.txt)",
                    data=email.strip(),
                    file_name=f"cold_email_job_{idx+1}.txt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio)
