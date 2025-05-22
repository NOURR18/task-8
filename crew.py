import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import matplotlib.pyplot as plt
from collections import Counter
from fpdf import FPDF
import os
from crewai import Agent, Task, Crew

# ========== 1. Web Search Agent ==========
class WebSearchAgent:
    def _init_(self):
        self.name = "Web Search Agent"

    def fetch_job_listings(self, query="AI ML", region="MENA"):
        print(f"[{self.name}] Fetching jobs...")
        urls = [
            f"https://wuzzuf.net/search/jobs/?q={query}&a=hpb",
            f"https://www.bayt.com/en/egypt/jobs/{query.replace(' ', '-')}-jobs/"
        ]
        jobs = []
        for url in urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            if "wuzzuf" in url:
                listings = soup.find_all("div", class_="css-1gatmva e1v1l3u10")
                for job in listings:
                    title = job.find("h2").text.strip() if job.find("h2") else "N/A"
                    company = job.find("a", class_="css-17s97q8").text.strip() if job.find("a", class_="css-17s97q8") else "N/A"
                    location = job.find("span", class_="css-5wys0k").text.strip() if job.find("span", class_="css-5wys0k") else "N/A"
                    jobs.append({"title": title, "company": company, "location": location})
            
            if "bayt" in url:
                listings = soup.find_all("div", class_="media")
                for job in listings:
                    title = job.find("h2").text.strip() if job.find("h2") else "N/A"
                    company = job.find("a", class_="company-name").text.strip() if job.find("a", class_="company-name") else "N/A"
                    location = job.find("span", class_="location").text.strip() if job.find("span", class_="location") else "N/A"
                    jobs.append({"title": title, "company": company, "location": location})
        
        df = pd.DataFrame(jobs)
        df.to_csv("jobs_data.csv", index=False)
        print(f"[{self.name}] {len(jobs)} jobs collected.")
        return df

# ========== 2. Data Extraction Agent ==========
class DataExtractionAgent:
    def _init_(self):
        self.name = "Data Extraction Agent"

    def extract_skills_from_titles(self, df):
        print(f"[{self.name}] Extracting skills...")
        skills_keywords = ["python", "tensorflow", "keras", "pytorch", "sql", "nlp", "vision", "pandas", "scikit", "ml", "ai", "deep learning"]
        skill_counts = Counter()

        for title in df["title"].dropna():
            title_lower = title.lower()
            for skill in skills_keywords:
                if skill in title_lower:
                    skill_counts[skill] += 1
        return skill_counts

# ========== 3. Trend Analysis Agent ==========
class TrendAnalysisAgent:
    def _init_(self):
        self.name = "Trend Analysis Agent"

    def analyze_trends(self, df, skill_counts):
        print(f"[{self.name}] Analyzing trends...")
        top_roles = df["title"].value_counts().head(10)
        top_locations = df["location"].value_counts().hed(10)
        top_skills = dict(skill_counts.most_common(10))

        return top_roles, top_locations, top_skills

# ========== 4. Report Writer Agent ==========
class ReportWriterAgent:
    def _init_(self):
        self.name = "Report Writer Agent"

    def generate_report(self, top_roles, top_locations, top_skills):
        print(f"[{self.name}] Generating report...")

        os.makedirs("results", exist_ok=True)

        # Visuals
        plt.figure(figsize=(10, 6))
        top_roles.plot(kind="bar", title="Top AI/ML Roles in MENA")
        plt.ylabel("Frequency")
        plt.savefig("results/top_roles.png")
        plt.clf()


        top_locations.plot(kind="bar", title="Top Locations")
        plt.ylabel("Frequency")
        plt.savefig("results/top_locations.png")
        plt.clf()

        pd.Series(top_skills).plot(kind="bar", title="Top Skills")
        plt.ylabel("Frequency")
        plt.savefig("results/top_skills.png")
        plt.clf()

        # PDF Report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Top AI/ML Jobs in MENA – May 2025", ln=True, align="C")

        pdf.set_font("Arial", "", 12)
        pdf.ln(10)
        pdf.cell(200, 10, "Top 10 Job Roles:", ln=True)
        for role, count in top_roles.items():
            pdf.cell(200, 10, f"- {role} ({count})", ln=True)

        pdf.ln(10)
        pdf.cell(200, 10, "Top Locations:", ln=True)
        for loc, count in top_locations.items():
            pdf.cell(200, 10, f"- {loc} ({count})", ln=True)

        pdf.ln(10)
        pdf.cell(200, 10, "Top Skills:", ln=True)
        for skill, count in top_skills.items():
            pdf.cell(200, 10, f"- {skill} ({count})", ln=True)

        pdf.image("results/top_roles.png", w=180)
        pdf.image("results/top_locations.png", w=180)
        pdf.image("results/top_skills.png", w=180)

        pdf.output("results/mena_ai_jobs_report.pdf")
        print(f"[{self.name}] Report saved to results/mena_ai_jobs_report.pdf")

# ========== MAIN ==========
if __name__ == "_main_":
    # Initialize agents
    web_search_agent = WebSearchAgent()
    data_extraction_agent = DataExtractionAgent()
    trend_analysis_agent = TrendAnalysisAgent()
    report_writer_agent = ReportWriterAgent()

    # Execute tasks
    df = web_search_agent.fetch_job_listings()
    skill_counts = data_extraction_agent.extract_skills_from_titles(df)
    top_roles, top_locations, top_skills = trend_analysis_agent.analyze_trends(df, skill_counts)
    report_writer_agent.generate_report(top_roles, top_locations, top_skills)