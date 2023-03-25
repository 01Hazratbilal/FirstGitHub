import streamlit as st
import openai
import docx
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib import styles
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
from PIL import ImageFont
import re
import os

api_key = os.environ.get('OPENAI_API_KEY')
openai.api_key = api_key


# Define necessary elements
necessary_elements = [
    "Job Title",
    "Job Type",
    "Job Location",
    "Job Summary",
    "Job Responsibilities",
    "Required Qualifications",
    "Experience",
    "Salary or Salary Range",
    "Benefits",
    "Application Deadline",
    "Company Overview",
    "Contact Information",
    "Equal Employment Opportunity Statement"
]


# Define additional elements
additional_elements = [
    "Reporting Structure",
    "Work Schedule",
    "Travel Requirements",
    "Physical Demands",
    "Working Conditions",
    "Training and Development Opportunities",
    "Performance Expectations",
    "Key Performance Indicators (KPIs)",
    "Career Advancement Opportunities",
    "Industry or Sector",
    "Company Culture",
    "Mission and Values",
    "Work Environment",
    "Skills and Competencies",
    "Tools and Technologies",
    "Team Size and Dynamics",
    "Language Requirements",
    "Certifications or Licenses Required",
    "Job Outlook",
    "Applicant Requirements",
    "Company History",
    "Job Performance Evaluation Criteria",
    "Remote Work Policy",
    "Dress Code",
    "Relocation Assistance",
    "Onboarding Process",
    "Employee Referral Program"
]


import streamlit as st

# Main screen for necessary elements
st.header("Job Description")
necessary_inputs = {}
for element in necessary_elements:
    necessary_inputs[element] = st.text_input(element)

# Sidebar for additional elements
st.sidebar.header("Additional Elements")
additional_elements_added = st.sidebar.multiselect(
    "Select additional elements", additional_elements
)

additional_inputs = {}
for element in additional_elements_added:
    additional_inputs[element] = st.text_input(element)


# Generate job description
if st.button("Generate Job Description"):
    prompt = "Create well structured and detailed job description. Use headings names (don't use if not given), use bullet points, numbering, or alphabets when needed. Do make the heading bold. Include only the provided information:\n\n"
    
    for key, value in necessary_inputs.items():
        prompt += f"<b style='font-size: 1.3em;'>{key}:</b> {value}\n\n"
        
    for key, value in additional_inputs.items():
        prompt += f"<b style='font-size: 1.3em;'>{key}:</b> {value}\n\n"
        
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )
    
    job_description = response.choices[0].text.strip()

    # Remove HTML tags from the job description
    job_description_no_html = re.sub(r'<[^>]*>', '', job_description)

    paragraphs = job_description_no_html.split("\n\n")
    formatted_description = ""
    for paragraph in paragraphs:
        formatted_description += f"{paragraph}\n\n"

    # Display the formatted job description
    st.write(f"<div style='text-align: center;'><h2>Job Description</h2></div><br><div>{job_description_no_html}</div>", unsafe_allow_html=True)

    # Save the job description as a Word document
    doc = docx.Document()
    for paragraph in paragraphs:
        doc.add_paragraph(paragraph)
    doc_bytes = BytesIO()
    doc.save(doc_bytes)
    doc_bytes.seek(0)
    st.download_button(label="Download as Word", data=doc_bytes, file_name="job_description.docx")

    # Save the job description as a PDF document
    style = styles.getSampleStyleSheet()
    pdf_buffer = BytesIO()
    pdf_doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    pdf_contents = []
    for paragraph in paragraphs:
        pdf_contents.append(Paragraph(paragraph, style['Normal']))
    pdf_doc.build(pdf_contents)
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()
    st.download_button(label="Download as PDF", data=pdf_bytes, file_name="job_description.pdf")


#     img = Image.new("RGB", (800, 1200), color="white")
#     d = ImageDraw.Draw(img)
#     x, y = 10, 10
    
#     # Get the absolute path of the current directory
#     dir_path = os.path.abspath(os.path.dirname(__file__))

#     # Use the absolute path to load the font file
#     font_path = os.path.join(dir_path, 'arial.ttf')
#     font = ImageFont.truetype(font_path, 16)

#     for paragraph in paragraphs:
#         lines = textwrap.wrap(paragraph, width=50)
#         for line in lines:
#             d.text((x, y), line, font=font, fill="black")
#             y += 20
#         y += 10

#     img_bytes = BytesIO()
#     img.save(img_bytes, "PNG")
#     img_bytes.seek(0)
#     st.download_button(label="Download as Image", data=img_bytes, file_name="job_description.png")
