import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import plotly.express as px
import altair as alt
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Generative AI with API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract text from uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

# Function to get Gemini response
def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

# Combined Prompt Template
input_prompt = """
Act as a skilled and experienced ATS (Applicant Tracking System) with a deep understanding of tech fields, 
including software engineering, data science, data analysis, and big data engineering. 
Your task is to evaluate the resume based on the given job description and provide assistance to improve the resume. 
Check for grammar mistakes, and for each mistake, provide the incorrect sentence along with the corrected version. 
Suggest improvements and provide feedback based on current trends in the job market.

Additionally, take on the perspective of an HR Manager assessing the applicant's suitability for the role. 
Include insights on the applicant's experience, skills, and potential fit within the company culture.

Assign a percentage match to the job description, identify missing keywords, and provide job recommendations based on market trends. 
Also, include grammar and sentence improvement suggestions.

Resume: {resume_text}
Job Description: {jd_text}

The response structure should be:
{{
   "JD Match": "percentage",
   "Missing Keywords": ["keyword1", "keyword2", ...],
   "Profile Summary": "summary",
   "Grammar Corrections": [
       {{"Incorrect": "text", "Correct": "corrected text"}}
   ],
   "Job Recommendations": ["role1", "role2", ...],
   "HR Insights": "summary of the applicant's fit and potential"
}}
"""

# Apply gradient background using custom CSS
st.markdown("""
    <style>
    .gradient-bg {
        background: linear-gradient(to right, #7e5bef, #5b3cc4);
        padding: 20px;
        border-radius: 15px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# App title and description with gradient
st.markdown('<div class="gradient-bg "><h1>Smart ATS Resume Evaluator</h1><p>Optimize your resume for ATS compatibility and improve your grammar.</p></div>', unsafe_allow_html=True)

# Job Description input
jd = st.text_area("Paste the Job Description", height=200, help="Paste the job description you are applying for.")

# Resume PDF upload
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf", help="Please upload your resume in PDF format.")

# Submit button
submit = st.button("Evaluate Resume")

# On submit action
if submit:
    if uploaded_file is not None and jd:
        # Show a loading spinner while processing
        with st.spinner("Analyzing your resume..."):
            # Extract text from uploaded PDF
            text = input_pdf_text(uploaded_file)
            
            # Prepare the prompt with resume text and job description
            prompt = input_prompt.format(resume_text=text, jd_text=jd)
            
            # Get response from Gemini API
            response = get_gemini_response(prompt)
            
            # Parse the response
            try:
                response_data = json.loads(response)
                jd_match = response_data.get("JD Match", "N/A")
                missing_keywords = response_data.get("Missing Keywords", [])
                profile_summary = response_data.get("Profile Summary", "N/A")
                grammar_corrections = response_data.get("Grammar Corrections", [])
                job_recommendations = response_data.get("Job Recommendations", [])
                hr_insights = response_data.get("HR Insights", "N/A")

                # Display results in a clear, well-formatted manner
                st.success("Resume Evaluation Completed!")
                
                # Display the JD match percentage clearly
                st.markdown("### **Job Description Match: {}%**".format(jd_match))
                
                jd_match = jd_match.replace('%', '')  # Remove the percentage sign
                st.progress(float(jd_match) / 100)
                
                # Display missing keywords in a clear format
                st.markdown("### **Missing Keywords:**")
                if missing_keywords:
                    st.write(", ".join(missing_keywords))
                else:
                    st.write("No significant keywords missing.")
                
                # Visualize missing keywords as a bar chart
                if missing_keywords:
                    keywords_data = pd.DataFrame({'Keywords': missing_keywords})
                    keyword_chart = alt.Chart(keywords_data).mark_bar().encode(
                        x='Keywords',
                        y=alt.value(50)
                    )
                    st.altair_chart(keyword_chart)
                
                # Display profile summary in a clean format
                st.markdown("### **Profile Summary:**")
                st.write(profile_summary)
                
                # Display grammar corrections in an organized format
                st.markdown("### **Grammar Corrections:**")
                if grammar_corrections:
                    for correction in grammar_corrections:
                        st.write(f"**Incorrect:** {correction['Incorrect']}")
                        st.write(f"**Corrected:** {correction['Correct']}")
                        st.write("---")
                else:
                    st.write("No grammar errors found.")
                
                # Display future job recommendations
                st.markdown("### **Future Job Recommendations:**")
                if job_recommendations:
                    st.write(", ".join(job_recommendations))
                    
                    # Visualize job recommendations as a pie chart
                    job_data = pd.DataFrame({
                        'Job Roles': job_recommendations,
                        'Count': [1 for _ in job_recommendations]
                    })
                    pie_chart = px.pie(job_data, names='Job Roles', values='Count')
                    st.plotly_chart(pie_chart)
                else:
                    st.write("No specific job recommendations at the moment.")
                
                # Display HR insights
                st.markdown("### **HR Insights:**")
                st.write(hr_insights)
            
            except json.JSONDecodeError:
                st.error("Error processing the response. Please try again.")
    else:
        st.error("Please upload a resume and provide a job description.")