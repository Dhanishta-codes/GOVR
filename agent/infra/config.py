"""Configuration file for SDR Agent"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# PHASE 1: AI & SEARCH
# ============================================

# -------- API KEYS --------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# -------- AI PROVIDER --------
AI_PROVIDER = os.getenv("AI_PROVIDER", "google").lower()

# -------- MODEL CONFIG --------
# Updated to supported models (2026 compatible)
MODELS = {
    "anthropic": "claude-3-haiku-20240307",   # Stable + cheap
    "google": "gemini-2.5-flash",            # FREE + stable
    "groq": "llama3-8b-8192"                 # Fast + free
}

# -------- AGENT SETTINGS --------
MAX_RESEARCH_ITERATIONS = 3
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))


# ============================================
# PHASE 2: CONTACT FINDING
# ============================================

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY", "")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")


# ============================================
# PHASE 2: EMAIL SENDING
# ============================================

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

EMAIL_SIGNATURE = """
Best regards,
{sender_name}
{sender_title}
{company_name}
{website}
"""

SENDER_INFO = {
    "name": os.getenv("SENDER_NAME", "Your Name"),
    "title": os.getenv("SENDER_TITLE", "Sales Development Representative"),
}


# ============================================
# PHASE 2: LINKEDIN AUTOMATION
# ============================================

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")

LINKEDIN_HEADLESS = os.getenv("LINKEDIN_HEADLESS", "True").lower() == "true"
LINKEDIN_DELAY_MIN = int(os.getenv("LINKEDIN_DELAY_MIN", "3"))
LINKEDIN_DELAY_MAX = int(os.getenv("LINKEDIN_DELAY_MAX", "7"))
LINKEDIN_DAILY_LIMIT = int(os.getenv("LINKEDIN_DAILY_LIMIT", "50"))


# ============================================
# PHASE 2: GOOGLE SHEETS TRACKING
# ============================================

GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "SDR Agent - Prospects")


# ============================================
# ICP & COMPANY SETTINGS
# ============================================

ICP_CRITERIA = {
    "company_size": "10-500 employees",
    "industries": ["SaaS", "Technology", "E-commerce"],
    "decision_maker_titles": [
        "VP Sales",
        "Head of Sales",
        "Sales Director",
        "Chief Revenue Officer",
        "CRO",
        "VP Marketing",
        "CMO"
    ]
}

YOUR_COMPANY = {
    "name": os.getenv("COMPANY_NAME", "Your Company"),
    "value_proposition": os.getenv(
        "VALUE_PROP",
        "We help sales teams automate prospecting and close more deals"
    ),
    "website": os.getenv("COMPANY_WEBSITE", "https://yourcompany.com")
}


# ============================================
# WORKFLOW SETTINGS
# ============================================

ENABLE_EMAIL_SENDING = os.getenv("ENABLE_EMAIL_SENDING", "False").lower() == "true"
ENABLE_LINKEDIN_OUTREACH = os.getenv("ENABLE_LINKEDIN_OUTREACH", "False").lower() == "true"
ENABLE_SHEETS_LOGGING = os.getenv("ENABLE_SHEETS_LOGGING", "False").lower() == "true"

AUTO_FOLLOWUP_ENABLED = os.getenv("AUTO_FOLLOWUP_ENABLED", "False").lower() == "true"
FOLLOWUP_DELAY_DAYS = int(os.getenv("FOLLOWUP_DELAY_DAYS", "3"))


# ============================================
# VALIDATION CHECKS
# ============================================

if AI_PROVIDER == "google" and not GOOGLE_API_KEY:
    print("⚠️ GOOGLE_API_KEY missing")

if AI_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
    print("⚠️ ANTHROPIC_API_KEY missing")

if AI_PROVIDER == "groq" and not GROQ_API_KEY:
    print("⚠️ GROQ_API_KEY missing")

if not TAVILY_API_KEY:
    print("⚠️ TAVILY_API_KEY missing")
