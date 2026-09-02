import streamlit as st
import pandas as pd
import re
import pypdf



# =====================================================
# AI RESUME SCREENING SYSTEM
# =====================================================

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Resume Screening System")
st.write("Automated resume screening with Multi-Format File Support (PDF, DOCX, TXT)")
st.divider()


# =====================================================
# SKILLS LIST
# =====================================================

skills = [
    "python", "java", "javascript", "html", "css", "react", "sql",
    "mysql", "mongodb", "pandas", "numpy", "machine learning",
    "data analysis", "data science", "excel", "power bi", "tableau",
    "git", "github", "communication", "teamwork", "leadership",
    "problem solving", "critical thinking"
]


# =====================================================
# FUNCTION 1: MULTI-FORMAT FILE READER (PDF, DOCX, TXT)
# =====================================================

def read_resume(file):
    """
    Extracts plain text from PDF, DOCX, and TXT files.
    """
    text = ""
    try:
        filename = file.name.lower()

        # Handle PDF Files
        if filename.endswith(".pdf"):
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "

        # Handle DOCX Files
        elif filename.endswith(".docx"):
            doc = docx.Document(file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + " "

        # Handle TXT Files
        elif filename.endswith(".txt"):
            text = file.read().decode("utf-8", errors="ignore")

        return text.lower()

    except Exception as e:
        st.error(f"Error reading file {file.name}: {e}")
        return ""


# =====================================================
# FUNCTION 2: FIND SKILLS
# =====================================================

def find_skills(text):
    found_skills = []
    for skill in skills:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text.lower()):
            found_skills.append(skill)
    return found_skills


# =====================================================
# FUNCTION 3: CALCULATE SCORE
# =====================================================

def calculate_score(matching_skills, required_skills):
    if len(required_skills) == 0:
        return 0
    score = (len(matching_skills) / len(required_skills)) * 100
    return round(score, 2)


# =====================================================
# FUNCTION 4: GET STATUS
# =====================================================

def get_status(score):
    if score >= 75:
        return "Selected"
    elif score >= 50:
        return "Under Review"
    else:
        return "Not Selected"


# =====================================================
# JOB DESCRIPTION
# =====================================================

st.header("💼 Job Description")

job_description = st.text_area(
    "Enter the job description and required skills",
    height=180,
    placeholder="""
Example:

We are looking for a Python Data Analyst.

Required skills:
Python, SQL, Pandas, NumPy, Excel, Power BI, Data Analysis, Communication, Teamwork and Problem Solving.
"""
)


# =====================================================
# RESUME UPLOAD (PDF, DOCX, TXT SUPPORTED)
# =====================================================

st.header("📄 Upload Resumes")

uploaded_files = st.file_uploader(
    "Upload candidate resumes (.pdf, .docx, .txt)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)


if uploaded_files:
    st.info(f"📂 {len(uploaded_files)} resume(s) uploaded.")


# =====================================================
# SCREEN RESUMES
# =====================================================

if st.button("🔍 SCREEN RESUMES", use_container_width=True):

    if job_description.strip() == "":
        st.error("Please enter a job description.")

    elif not uploaded_files:
        st.error("Please upload at least one resume.")

    else:
        required_skills = find_skills(job_description)

        if not required_skills:
            st.warning("No skills were detected in the job description.")

        else:
            st.success("Required Skills: " + ", ".join(required_skills))

            results = []

            for file in uploaded_files:
                resume_text = read_resume(file)

                if resume_text.strip() == "":
                    continue

                resume_skills = find_skills(resume_text)

                matching_skills = [s for s in required_skills if s in resume_skills]
                missing_skills = [s for s in required_skills if s not in resume_skills]

                score = calculate_score(matching_skills, required_skills)
                candidate_status = get_status(score)

                results.append({
                    "Candidate": file.name,
                    "Match Score": score,
                    "Matching Skills": ", ".join(matching_skills),
                    "Missing Skills": ", ".join(missing_skills),
                    "Status": candidate_status
                })

            if not results:
                st.error("Unable to read the uploaded resumes or extract content.")

            else:
                df = pd.DataFrame(results)
                df = df.sort_values("Match Score", ascending=False).reset_index(drop=True)
                df.insert(0, "Rank", range(1, len(df) + 1))

                # Dashboard
                st.divider()
                st.header("📊 Screening Dashboard")

                total = len(df)
                selected = len(df[df["Status"] == "Selected"])
                review = len(df[df["Status"] == "Under Review"])
                not_selected = len(df[df["Status"] == "Not Selected"])
                average_score = df["Match Score"].mean()

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("👥 Candidates", total)
                col2.metric("✅ Selected", selected)
                col3.metric("🟡 Under Review", review)
                col4.metric("❌ Not Selected", not_selected)

                st.metric("📈 Average Match Score", f"{average_score:.2f}%")

                # Candidate Ranking
                st.subheader("🏆 Candidate Ranking")
                st.dataframe(
                    df[["Rank", "Candidate", "Match Score", "Status"]],
                    use_container_width=True,
                    hide_index=True
                )

                # Top Candidate
                st.subheader("🥇 Top Candidate")
                top_candidate = df.iloc[0]
                st.success(
                    f"Candidate: {top_candidate['Candidate']}\n\n"
                    f"Match Score: {top_candidate['Match Score']}%\n\n"
                    f"Status: {top_candidate['Status']}"
                )

                # Detailed Candidate View
                st.subheader("🔎 Candidate Details")
                selected_candidate = st.selectbox("Select a candidate", df["Candidate"].tolist())
                candidate = df[df["Candidate"] == selected_candidate].iloc[0]

                st.write("### 👤", candidate["Candidate"])
                st.write("**Match Score:**", f"{candidate['Match Score']}%")

                if candidate["Status"] == "Selected":
                    st.success("✅ Selected")
                elif candidate["Status"] == "Under Review":
                    st.warning("🟡 Under Review")
                else:
                    st.error("❌ Not Selected")

                # Matching & Missing Skills
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("### ✅ Matching Skills")
                    matching = candidate["Matching Skills"].split(", ") if candidate["Matching Skills"] else []
                    for s in matching:
                        if s: st.write("✓", s)

                with col_b:
                    st.write("### ⚠️ Missing Skills")
                    missing = candidate["Missing Skills"].split(", ") if candidate["Missing Skills"] else []
                    for s in missing:
                        if s: st.write("✗", s)

                # Download Button
                st.subheader("📥 Download Results")
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Screening Results (CSV)",
                    csv_data,
                    "resume_screening_results.csv",
                    "text/csv",
                    use_container_width=True
                )