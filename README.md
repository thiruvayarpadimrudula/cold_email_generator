# Cold Email Generator

An AI-powered cold email generator web application built with **Streamlit** and **LLM-based AI**. Unlike static, hard-coded solutions, this app allows users to input URLs or job links and generates personalized cold emails for multiple roles dynamically.

---
<img width="1919" height="867" alt="Screenshot 2025-10-23 165747" src="https://github.com/user-attachments/assets/19694a2e-0686-44cb-af4d-3e8412616cbd" />
<img width="1919" height="879" alt="Screenshot 2025-10-23 165756" src="https://github.com/user-attachments/assets/56ef6447-401a-48d2-87e8-4a4f05ae2e43" />
<img width="1910" height="630" alt="Screenshot 2025-10-23 165809" src="https://github.com/user-attachments/assets/4bfc1f33-02ae-483b-8dff-e7ecf3713d71" />

## Table of Contents

- [Project Overview](#project-overview)  
- [Features](#features)  
- [Project Structure](#project-structure)  
- [Technologies Used](#technologies-used)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Environment Variables](#environment-variables)  
- [Acknowledgments](#acknowledgments)  
- [License](#license)  

---

## Project Overview

This project enables job seekers, freelancers, and professionals to generate professional cold emails automatically. Users provide a job URL or portfolio CSV, and the app uses an LLM model (Groq) to extract job postings, match skills with portfolio items, and generate tailored cold emails.

This implementation improves upon standard tutorials by supporting dynamic input, multi-user usage, and custom email tones, lengths, and types.

---

## Features

- Generate personalized cold emails from any job or company URL.  
- Support for user-uploaded portfolios in CSV format.  
- Automatic extraction of job information from web pages.  
- Options for email tone, length, and type.  
- Download generated emails as `.txt` files.  
- Clean, responsive **Streamlit** UI with branding/logo support.  
- Integration with **ChromaDB** for semantic portfolio matching.  

---

## Project Structure

cold_email_fresh/
│
├── .streamlit/ # Streamlit configuration
├── app/
│ ├── main.py # Streamlit app entry point
│ ├── chains.py # LLM logic for extracting jobs & generating emails
│ ├── portfolio.py # Portfolio handling and vector store logic
│ ├── utils/ # Helper functions (text cleaning, etc.)
├── requirements.txt # Python dependencies
├── vectorstore/ # ChromaDB persistent vector storage
├── .env # Environment variables (API keys)
├── .gitignore
├── logo/ # App logo (logo.jpg)
├── my_portfolio.csv # Default sample portfolio



---


<img width="985" height="274" alt="cold_email drawio" src="https://github.com/user-attachments/assets/f4540fd8-2938-4b51-9cfb-baf6856d236e" />

## Technologies Used

- **Python 3.13**  
- **Streamlit** – Interactive web interface  
- **LangChain / Groq LLM** – AI-based email generation  
- **ChromaDB** – Vector database for portfolio matching  
- **Pandas** – CSV handling  
- **dotenv** – Environment variable management  

---

## Installation

1. **Clone the repository**
    git clone https://github.com/<your-username>/cold_email_fresh.git
    cd cold_email_fresh
   
2. **Create a virtual environment**

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


Install dependencies
pip install -r requirements.txt


Set up environment variables
Create a .env file in the project root with your Groq API key:
GROQ_API_KEY=your_groq_api_key

⚠️ Alternatively, use Streamlit secrets to store your key:

# .streamlit/secrets.toml
[GROQ]
api_key="your_groq_api_key"

Usage
Run the Streamlit app
streamlit run app/main.py

Open the app in your browser
Default URL: http://localhost:8501

Generate cold emails

Enter a job URL.

Optionally upload your portfolio CSV (columns: Techstack, Links).

Choose email tone, length, and type.

Enter your sender name, title, and company name.

Click Submit to generate emails.

Preview emails in the app and download as .txt files.

Environment Variables

GROQ_API_KEY – API key for Groq LLM (required)

Important: Do not commit .env files or API keys to public repositories.
---

## Acknowledgments

Inspired by CodeBasics YouTube tutorial
Customizations and improvements for dynamic user input, multi-role emails, and portfolio integration by Mrudula**
