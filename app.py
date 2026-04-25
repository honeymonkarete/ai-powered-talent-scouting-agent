import streamlit as st
import re
import os
import pandas as pd
from PyPDF2 import PdfReader
from groq import Groq

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="AI‑Powered Talent Scouting Agent", layout="wide")
st.title("🧠 AI‑Powered Talent Scouting Agent")

# =================================================
# LARGE SKILL DATABASE
# =================================================
SKILL_DB = {

    # =========================
    # CORE BUSINESS & OPERATIONS
    # =========================
    "operations": [
        "operations", "operational", "workflow", "process", "coordination",
        "logistics", "resource planning", "resource allocation",
        "business operations", "service delivery"
    ],

    "project management": [
        "project management", "project coordinator", "project planning",
        "roadmap", "milestones", "jira", "asana", "trello", "ms project"
    ],

    "management": [
        "management", "manager", "team lead", "leadership",
        "people management", "supervision", "performance review"
    ],

    "stakeholder management": [
        "stakeholder", "stakeholder management", "cross functional",
        "cross-functional", "client coordination", "vendor coordination"
    ],

    # =========================
    # COMMUNICATION & SUPPORT
    # =========================
    "communication": [
        "communication", "verbal communication", "written communication",
        "presentation", "documentation", "report writing"
    ],

    "customer service": [
        "customer service", "customer support", "client support",
        "helpdesk", "service desk", "customer engagement",
        "client interaction"
    ],

    # =========================
    # ANALYTICS & REPORTING
    # =========================
    "reporting": [
        "reporting", "reports", "dashboards", "metrics", "kpis",
        "tracking", "monitoring", "analysis"
    ],

    "data analysis": [
        "data analysis", "data analytics", "insights",
        "trend analysis", "performance analysis"
    ],

    # =========================
    # OFFICE TOOLS & PRODUCTIVITY
    # =========================
    "excel": [
        "excel", "ms excel", "microsoft excel",
        "google sheets", "spreadsheets",
        "pivot table", "vlookup", "formulas"
    ],

    "office tools": [
        "ms office", "microsoft office",
        "powerpoint", "word", "outlook"
    ],

    # =========================
    # MARKETING & GROWTH
    # =========================
    "marketing": [
        "marketing", "campaign", "campaign management",
        "brand awareness", "lead generation", "growth marketing"
    ],

    "digital marketing": [
        "digital marketing", "email marketing",
        "marketing automation", "mailchimp"
    ],

    "social media": [
        "social media", "linkedin", "instagram",
        "facebook", "twitter", "content calendar",
        "community management"
    ],

    "content": [
        "content", "content creation", "copywriting",
        "blog", "articles", "creative writing"
    ],

    "seo": [
        "seo", "search engine optimization",
        "keywords", "on-page seo", "google search console"
    ],

    # =========================
    # SALES & CRM
    # =========================
    "sales": [
        "sales", "business development",
        "prospecting", "pipeline", "closing deals"
    ],

    "crm": [
        "crm", "salesforce", "hubspot",
        "zoho", "customer relationship management"
    ],

    # =========================
    # HR & PEOPLE OPERATIONS
    # =========================
    "human resources": [
        "human resources", "hr",
        "recruitment", "talent acquisition",
        "hiring", "onboarding"
    ],

    "training": [
        "training", "upskilling", "coaching",
        "learning", "development", "onboarding"
    ],

    # =========================
    # FINANCE & ADMIN
    # =========================
    "finance": [
        "finance", "budget", "budgeting",
        "billing", "invoice", "cost tracking",
        "financial reporting"
    ],

    "administration": [
        "administration", "administrative",
        "office administration", "record keeping"
    ],

    # =========================
    # TECH / IT (LIGHTWEIGHT)
    # =========================
    "it support": [
        "it support", "technical support",
        "systems", "software support",
        "application support"
    ],

    "tools": [
        "tools", "platforms", "systems",
        "software", "applications"
    ],

    # =========================
    # DESIGN (OPTIONAL)
    # =========================
    "design": [
        "design", "graphic design",
        "canva", "figma", "adobe",
        "creative assets"
    ]
}

# =================================================
# UTILS
# =================================================
def clean(text):
    return re.sub(r"\s+", " ", text.lower())


def read_pdf(file):
    reader = PdfReader(file)
    return " ".join(page.extract_text() or "" for page in reader.pages)


def extract_name(raw_text, filename):
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

    for line in lines[:12]:
        cleaned = re.sub(r"[^A-Za-z ]", "", line)
        words = cleaned.split()
        if 2 <= len(words) <= 4:
            if cleaned.isupper() or cleaned.istitle():
                return cleaned.title()

    name = filename.replace("_", " ").replace("-", " ")
    name = re.sub(r"\d+", "", name)
    return name.replace(".pdf", "").title().strip()


def color_badge(score, label):
    if score >= 80:
        icon = "🟢"
    elif score >= 50:
        icon = "🟡"
    else:
        icon = "🔴"
    return f"{icon} **{label}:** {score}"

# =================================================
# AGENTS
# =================================================
class JDSkillsAgent:
    def run(self, jd):
        jd = clean(jd)
        skills = []
        for skill, kws in SKILL_DB.items():
            for kw in kws:
                if re.search(rf"\b{kw}\b", jd):
                    skills.append(skill)
                    break
        return list(set(skills))


class ResumeParsingAgent:
    def run(self, file):
        raw = read_pdf(file)
        name = extract_name(raw, file.name)
        text = clean(raw)

        skills = []
        for skill, kws in SKILL_DB.items():
            for kw in kws:
                if re.search(rf"\b{kw}\b", text):
                    skills.append(skill)
                    break
        return name, list(set(skills))


class MatchingAgent:
    def run(self, jd_skills, resume_skills):
        matched = list(set(jd_skills) & set(resume_skills))
        missing = list(set(jd_skills) - set(resume_skills))
        score = round((len(matched) / len(jd_skills)) * 100, 1) if jd_skills else 100
        return score, matched, missing


class InterestSimulationAgent:
    def run(self, match_score):
        if match_score >= 80:
            return 85, "High"
        elif match_score >= 50:
            return 65, "Medium"
        else:
            return 40, "Low"


class LLMExplanationAgent:
    def __init__(self):
        self.key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.key) if self.key else None

    def explain(self, matched, missing, interest):
        if not self.client:
            return "Candidate fit is based on skill alignment and simulated interest."

        prompt = f"""
Explain candidate fit to a recruiter in 1–2 concise sentences.
Avoid definitions.

Matched skills: {matched}
Missing skills: {missing}
Interest level: {interest}
"""

        res = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
        return res.choices[0].message.content.strip()


class RankingAgent:
    def run(self, results):
        for r in results:
            r["Final Score"] = round(
                0.7 * r["Match Score"] + 0.3 * r["Interest Score"], 1
            )
        return sorted(results, key=lambda x: x["Final Score"], reverse=True)

# =================================================
# UI
# =================================================
jd_text = st.text_area("📄 Paste Job Description")

files = st.file_uploader(
    "📁 Upload Resumes (PDF – bulk upload supported)",
    type=["pdf"],
    accept_multiple_files=True,
)

if st.button("Run Talent Scouting"):
    if not jd_text or not files:
        st.warning("Please paste a Job Description and upload resumes.")
        st.stop()

    jd_agent = JDSkillsAgent()
    resume_agent = ResumeParsingAgent()
    match_agent = MatchingAgent()
    interest_agent = InterestSimulationAgent()
    llm_agent = LLMExplanationAgent()
    ranking_agent = RankingAgent()

    jd_skills = jd_agent.run(jd_text)
    results = []

    for file in files:
        name, skills = resume_agent.run(file)
        match_score, matched, missing = match_agent.run(jd_skills, skills)
        interest_score, interest_level = interest_agent.run(match_score)

        explanation = llm_agent.explain(
            ", ".join(matched) or "None",
            ", ".join(missing) or "None",
            interest_level,
        )

        results.append({
            "Candidate": name,
            "Match Score": match_score,
            "Interest Score": interest_score,
            "Interest Level": interest_level,
            "Matched Skills": ", ".join(matched) or "None",
            "Missing Skills": ", ".join(missing) or "None",
            "Explanation": explanation,
        })

    ranked = ranking_agent.run(results)

    # ================= CSV EXPORT =================
    df = pd.DataFrame(ranked)
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="ranked_candidates.csv",
        mime="text/csv",
    )

    st.subheader("📊 Ranked Candidates")

    for i, r in enumerate(ranked, 1):
        st.markdown(f"""
### #{i} {r['Candidate']}

{color_badge(r['Match Score'], "Match Score")}  
{color_badge(r['Interest Score'], "Interest Score")} ({r['Interest Level']})  
{color_badge(r['Final Score'], "Final Score")}

✅ **Matched Skills:** {r['Matched Skills']}  
❌ **Missing Skills:** {r['Missing Skills']}

🧠 **AI Explanation:**  
{r['Explanation']}
""")