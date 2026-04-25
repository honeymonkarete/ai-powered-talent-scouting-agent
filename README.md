# 🧠 AI-Powered Talent Scouting Agent

A multi-agent Streamlit application that automates resume screening by matching candidates against a job description using skill extraction, scoring, and optional LLM-generated explanations.

---

## Features

- **Bulk Resume Upload** — Process multiple PDF resumes in one run
- **JD Skill Extraction** — Automatically identifies required skills from any pasted job description
- **Resume Parsing** — Extracts candidate name and skills from uploaded PDF resumes
- **Match Scoring** — Computes a skill-overlap score between JD requirements and each candidate
- **Interest Simulation** — Estimates candidate interest level based on match strength
- **AI Explanations** — Generates a concise recruiter-friendly summary via Groq (LLaMA 3.1) if an API key is provided
- **Ranked Output** — Candidates are ranked by a weighted Final Score (70% match + 30% interest)
- **CSV Export** — Download the full ranked results as a spreadsheet

---

## Agent Architecture

The app is built around six single-responsibility agents:

| Agent | Role |
|---|---|
| `JDSkillsAgent` | Parses job description and returns a list of required skills |
| `ResumeParsingAgent` | Reads PDF, extracts candidate name and detected skills |
| `MatchingAgent` | Computes matched/missing skills and a match score (0–100) |
| `InterestSimulationAgent` | Derives an interest score and level from the match score |
| `LLMExplanationAgent` | Calls Groq API to generate a natural-language fit summary |
| `RankingAgent` | Sorts candidates by Final Score = 0.7 × Match + 0.3 × Interest |

---

## Scoring Logic

```
Match Score     = (Matched Skills / JD Skills) × 100
Interest Score  = 85 if Match ≥ 80 | 65 if Match ≥ 50 | 40 otherwise
Final Score     = (0.7 × Match Score) + (0.3 × Interest Score)
```

Score badges are colour-coded: 🟢 ≥ 80 · 🟡 ≥ 50 · 🔴 < 50

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/talent-scouting-agent.git
cd talent-scouting-agent
```

### 2. Install dependencies

```bash
pip install streamlit PyPDF2 pandas groq
```

### 3. Configure the Groq API key (optional)

AI explanations require a free [Groq API key](https://console.groq.com/).

```bash
export GROQ_API_KEY=your_key_here
```

If no key is set, the app falls back to a default explanation string — all other features work normally.

### 4. Run the app

```bash
streamlit run app.py
```

---

## Usage

1. Paste a job description into the text area
2. Upload one or more candidate PDF resumes
3. Click **Run Talent Scouting**
4. Review the ranked candidate cards with scores and skill breakdowns
5. Download the full results via **Download Results as CSV**

---

## Skill Coverage

The built-in skill database covers 25+ categories including:

- Business & Operations, Project Management, Stakeholder Management
- Analytics, Reporting, Data Analysis
- Excel, MS Office, Productivity Tools
- Marketing, SEO, Social Media, Content
- Sales, CRM, HR, Training, Finance
- IT Support, Design

The database is a plain Python dictionary (`SKILL_DB` in `app.py`) and can be extended with new categories or keywords at any time.

---

## Project Structure

```
talent-scouting-agent/
├── app.py          # Main application — all agents and UI
└── README.md       # This file
```

---

## Requirements

| Package | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `PyPDF2` | PDF text extraction |
| `pandas` | Tabular data and CSV export |
| `groq` | LLM API client (optional) |

Python 3.8+ recommended.

---

## Limitations

- Resume parsing relies on text-based PDFs; scanned/image PDFs will yield limited results
- Candidate name extraction uses heuristics and may fall back to the filename
- Interest scoring is simulated (rule-based), not derived from real candidate signals
- Skill matching is keyword-based; semantic similarity is not applied

---

## License

MIT License. Free to use, modify, and distribute.
