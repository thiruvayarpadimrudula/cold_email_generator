# chains.py
import os
import streamlit as st

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

# Load .env file in project root
load_dotenv()


class Chain:
    def __init__(self):
        # ✅ Get API key from local .env

        GROQ_API_KEY = st.secrets["GROQ"]["api_key"]

        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set! Add it in a .env file in project root.")

        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=GROQ_API_KEY,
            model_name="groq/compound"
        )

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            Extract job postings and return them as valid JSON with keys: 
            `role`, `experience`, `skills`, `description`.
            Only return JSON (no extra text or preamble).
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke({"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            jobs = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return jobs if isinstance(jobs, list) else [jobs]

    def write_mail(
        self,
        job,
        links,
        sender_name="Mrudula",
        company_name="Artgen_z",
        sender_title="BDE",
        tone="Formal",
        length="Medium",
        email_type="Job Application"
    ):
        # Convert links to comma-separated string
        if not links:
            link_list_str = "No portfolio links provided."
        else:
            link_items = []
            for d in links:
                val = d.get('links') if isinstance(d, dict) else str(d)
                if val:
                    link_items.append(val)
            link_list_str = ", ".join(link_items) if link_items else "No portfolio links provided."

        # Sender description
        sender_desc = f"{sender_name}, {sender_title} at {company_name}" if sender_title else f"{sender_name} at {company_name}"

        # Length guidance
        length_map = {
            "Short": "2-4 sentences (concise)",
            "Medium": "4-8 sentences (balanced)",
            "Detailed": "8-15 sentences (detailed, but professional)"
        }
        length_guidance = length_map.get(length, "4-8 sentences (balanced)")

        prompt_email = PromptTemplate.from_template(
            """
            ### JOB ROLE:
            {job_role}

            ### JOB DESCRIPTION:
            {job_description}

            ### CONTEXT:
            You are {sender_desc}.
            Company: {company_name}.
            Email Type: {email_type}.
            Desired Tone: {tone}.
            Desired Length: {length_guidance}.
            Portfolio links (if any): {link_list}

            ### INSTRUCTION:
            Write a cold email tailored to the job role/description above.
            - Start directly with the email content (no preamble like "Hi" explanations).
            - Keep it professional and aligned with the selected tone.
            - Make it suitable for sending to a hiring manager or recruiter.
            - Mention relevant portfolio links naturally where appropriate.
            ### EMAIL (NO PREAMBLE):
            """
        )

        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_role": job.get('role', ''),
            "job_description": job.get('description', ''),
            "link_list": link_list_str,
            "sender_desc": sender_desc,
            "company_name": company_name,
            "email_type": email_type,
            "tone": tone,
            "length_guidance": length_guidance
        })
        return res.content


if __name__ == "__main__":
    # Test locally
    key = os.getenv("GROQ_API_KEY")
    print("GROQ API Key:", key)
