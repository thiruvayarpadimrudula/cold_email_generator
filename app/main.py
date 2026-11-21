import streamlit as st
import pandas as pd
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import os
import time

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
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=120)
        else:
            st.markdown(
                "<div style='height:72px;'></div>",
                unsafe_allow_html=True
            )

    with col2:
        st.markdown(
            "<div class='app-title card'><h1>📧 Cold Email Generator</h1></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")


def create_streamlit_app(llm, portfolio):
    render_header()

    # ---------------------------
    # Input section
    # ---------------------------
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    input_method = st.radio(
        "Choose job description input method:",
        ["Job URL", "Paste Job Description"]
    )

    url_input = ""
    job_description_input = ""

    if input_method == "Job URL":
        url_input = st.text_input("Enter Job URL:")
    else:
        job_description_input = st.text_area(
            "Paste the complete Job Description:",
            height=300,
            placeholder="Paste the job responsibilities, qualifications and required skills here..."
        )

    sender_name = st.text_input(
        "Sender name:",
        value="Mrudula"
    )

    # ---------------------------
    # Email customization
    # ---------------------------
    st.markdown("### Email style options")

    tone = st.selectbox(
        "Email tone",
        ["Formal", "Friendly", "Persuasive", "Neutral"],
        index=0
    )

    length = st.selectbox(
        "Email length",
        ["Short", "Medium", "Detailed"],
        index=1
    )

    email_type = st.selectbox(
        "Email type",
        [
            "Job Application",
            "Collaboration",
            "Partnership / Pitch",
            "Introductory"
        ],
        index=0
    )

    st.markdown("---")

    # ---------------------------
    # Portfolio upload
    # ---------------------------
    st.subheader("Portfolio (CSV)")

    st.write(
        "Upload a CSV with columns `Techstack` and `Links` "
        "(Links can be GitHub/website)."
    )

    uploaded_file = st.file_uploader(
        "Upload portfolio CSV (optional)",
        type=["csv"]
    )

    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)

            st.write("Preview of uploaded portfolio:")
            st.dataframe(uploaded_df.head(10))

            if st.button("Use uploaded portfolio"):
                portfolio.load_portfolio(uploaded_df)

                st.success(
                    "Uploaded portfolio loaded into vector store."
                )

        except Exception as e:
            st.error(f"Failed to read uploaded CSV: {e}")
    else:
        portfolio_df = pd.read_csv("data/portfolio.csv")
        portfolio.load_portfolio(portfolio_df) 

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------
    # Submit
    # ---------------------------
    submit_button = st.button(
        "Submit",
        key="submit_main"
    )

    if submit_button:
        try:
            total_start = time.perf_counter()

            # ---------------------------
            # 1. Get job description
            # ---------------------------
            if input_method == "Job URL":

                if not url_input.strip():
                    st.error("Please enter a valid URL.")
                    st.stop()

                loader = WebBaseLoader([url_input])

                page_content = loader.load().pop().page_content

                clean_data = clean_text(page_content)

            else:

                if not job_description_input.strip():
                    st.error("Please paste a job description.")
                    st.stop()

                clean_data = job_description_input.strip()

            # Limit input length
            clean_data = clean_data[:16000]

            st.write(
                "Job description characters:",
                len(clean_data)
            )

            st.subheader("DEBUG: Scraped Job Description")

            st.text_area(
                "Cleaned text",
                clean_data,
                height=300
            )

            # ---------------------------
            # 2. Ensure portfolio is loaded
            # ---------------------------
            portfolio_start = time.perf_counter()

            portfolio.load_portfolio()

            portfolio_load_time = (
                time.perf_counter() - portfolio_start
            )

            # ---------------------------
            # 3. Extract job details
            # ---------------------------
            extraction_start = time.perf_counter()

            jobs = llm.extract_jobs(clean_data)

            extraction_time = (
                time.perf_counter() - extraction_start
            )

            if not jobs:
                st.warning(
                    "No job details could be extracted from the description."
                )
                st.stop()

            # ---------------------------
            # 4. Retrieve projects and generate emails
            # ---------------------------
            retrieval_times = []
            email_times = []

            for idx, job in enumerate(jobs):

                job_skills = job.get("skills", [])

                if isinstance(job_skills, str):
                    job_skills = [job_skills]

                # Portfolio retrieval
                retrieval_start = time.perf_counter()

                links = portfolio.query_links(job_skills)

                retrieval_time = (
                    time.perf_counter() - retrieval_start
                )

                retrieval_times.append(retrieval_time)

                st.subheader("DEBUG: Extracted Job Details")
                st.json(job)

                st.subheader("DEBUG: Retrieved Portfolio Projects")
                st.json(links)

                # Generate email
                email_start = time.perf_counter()

                email = llm.write_mail(
                    job,
                    links,
                    sender_name=sender_name,
                    tone=tone,
                    length=length,
                    email_type=email_type
                )

                email_time = (
                    time.perf_counter() - email_start
                )

                email_times.append(email_time)

                # Convert escaped newlines
                if isinstance(email, str):
                    email = email.replace("\\n", "\n")

                # ---------------------------
                # Email preview
                # ---------------------------
                st.markdown(
                    f"### ✉️ Email #{idx + 1}: "
                    f"{job.get('role', 'Unknown Role')}"
                )

                st.text_area(
                    f"Email preview — Job #{idx + 1}",
                    value=email.strip(),
                    height=260,
                    key=f"email_preview_{idx}"
                )

                # One-click TXT export
                st.download_button(
                    label="Download email (.txt)",
                    data=email.strip(),
                    file_name=f"cold_email_job_{idx + 1}.txt",
                    mime="text/plain",
                    key=f"download_email_{idx}"
                )

            # ---------------------------
            # 5. Performance measurements
            # ---------------------------
            total_time = time.perf_counter() - total_start

            total_retrieval_time = sum(retrieval_times)
            total_email_time = sum(email_times)

            st.markdown("---")
            st.subheader("Performance Report")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Portfolio loading",
                    f"{portfolio_load_time:.3f} sec"
                )

                st.metric(
                    "Job extraction",
                    f"{extraction_time:.3f} sec"
                )

            with col2:
                st.metric(
                    "Portfolio retrieval",
                    f"{total_retrieval_time:.3f} sec"
                )

                st.metric(
                    "Email generation",
                    f"{total_email_time:.3f} sec"
                )

            st.metric(
                "Total processing time",
                f"{total_time:.2f} seconds"
            )

            print("\n===== PERFORMANCE REPORT =====")
            print(
                f"Portfolio loading: {portfolio_load_time:.3f} sec"
            )
            print(
                f"Job extraction: {extraction_time:.3f} sec"
            )
            print(
                f"Portfolio retrieval: {total_retrieval_time:.3f} sec"
            )
            print(
                f"Email generation: {total_email_time:.3f} sec"
            )
            print(
                f"Total processing time: {total_time:.2f} sec"
            )

            # Show LRU cache statistics
            if hasattr(portfolio, "_get_cached_embedding"):
                st.subheader("Embedding Cache Statistics")

                cache_info = portfolio.get_embedding_cache_info()

                st.write({
                    "Cache hits": cache_info.hits,
                    "Cache misses": cache_info.misses,
                    "Maximum capacity": cache_info.maxsize,
                    "Current entries": cache_info.currsize
                })

                print("Embedding cache:", cache_info)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            print(f"Application error: {e}")


# ---------------------------
# Application entry point
# ---------------------------
if __name__ == "__main__":

    st.set_page_config(
        layout="wide",
        page_title="Cold Email Generator",
        page_icon="📧"
    )

    chain = Chain()

    if "portfolio" not in st.session_state:
        st.session_state.portfolio = Portfolio()
        st.session_state.portfolio.load_portfolio()

    portfolio = st.session_state.portfolio

    create_streamlit_app(chain, portfolio)
