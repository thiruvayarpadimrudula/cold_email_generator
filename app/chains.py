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
            model_name="openai/gpt-oss-120b"
        )

    
    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}

            ### INSTRUCTIONS:
            Extract ONLY the primary job posting described on this page.

            Ignore:
            - Related or recommended jobs
            - Other job listings
            - Navigation menus
            - Footer content
            - Similar job suggestions

            Extract the following fields:
        - role
        - experience
        - skills
        - description

        Return exactly ONE JSON object, not a list.
        Use an empty string or empty list if information is unavailable.

        Return valid JSON only. No markdown or explanations.
        """
        )

        chain_extract = prompt_extract | self.llm
 
        res = chain_extract.invoke({"page_data": cleaned_text})

        try:
            json_parser = JsonOutputParser()
            job = json_parser.parse(res.content)

            if isinstance(job, list):
               job = job[0] if job else {}

            return [job] if isinstance(job, dict) else []

        except OutputParserException:
            raise OutputParserException(
            "Unable to extract or parse the job description."
        )


    def write_mail(
        self,
        job,
        links,
        sender_name="Mrudula",
        tone="Formal",
        length="Medium",
        email_type="Job Application"
    ):
        # Convert links to comma-separated string
        if not links:
            portfolio_context = "No relevant portfolio projects found."
        else:
            project_details = []

            for project in links:
                techstack = project.get("techstack", "")
                link = project.get("links", "")

                if techstack or link:
                    project_details.append(
                    f"Technologies: {techstack}\n"
                    f"Project Link: {link}"
                )

            portfolio_context = (
                "\n\n".join(project_details)
                if project_details
                else "No relevant portfolio projects found."
            )

        # Sender description
        sender_desc = f"{sender_name}"

        # Length guidance
        length_map = {
            "Short": "2-4 sentences (concise)",
            "Medium": "4-8 sentences (balanced)",
            "Detailed": "8-15 sentences (detailed, but professional)"
        }
        length_guidance = length_map.get(length, "4-8 sentences (balanced)")

        prompt_email = PromptTemplate.from_template("""
        You are helping an IT graduate write a professional cold email
        to apply for a job opportunity.

        ### JOB ROLE:
        {job_role}

        ### JOB DESCRIPTION:
        {job_description}

        ### RELEVANT PORTFOLIO PROJECTS:
        {portfolio_context}

        ### INSTRUCTIONS:
        Write a {email_type} email expressing interest in the {job_role} position.

        - Use a {tone} tone.
        - Follow this length guidance: {length_guidance}.
        - Mention only skills and experience supported by the job information
          and portfolio context.
        - Do not invent work experience, qualifications, or technical skills.
        - Explain briefly how the relevant projects demonstrate the applicant's abilities.
        - Do not refer to the applicant as representing another company.
        - Do not invent details about the hiring company.
        - End with a professional closing and the name Mrudula.

        Return only the email content.
        """)
        

        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_role": job.get('role', ''),
            "job_description": job.get('description', ''),
            "portfolio_context": portfolio_context,
            "email_type": email_type,
            "tone": tone,
            "length_guidance": length_guidance
        })
        return res.content


if __name__ == "__main__":
    # Test locally
    key = os.getenv("GROQ_API_KEY")
    print("GROQ API Key:", key)
