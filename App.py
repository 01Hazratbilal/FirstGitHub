import streamlit as st
import openai
import docx
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib import styles
from PIL import Image, ImageDraw
from io import BytesIO
import textwrap
import re
import os
from googletrans import Translator

api_key = os.environ.get('OPENAI_API_KEY')
openai.api_key = api_key

# Add translator
translator = Translator()

# Language options
languages = {
    "English": "en",
    "German": "de",
    "Russian": "ru",
    "Chinese": "zh-CN"
}

# Create columns
col1, col2 = st.columns((8, 2))

# Add the dropdown menu to the right column
selected_language = col2.selectbox("Select language", list(languages.keys()), index=0, key="language_select")

def translate_text(text, target_language):
    if target_language != "en":
        translated_text = translator.translate(text, dest=target_language).text
        return translated_text
    else:
        return text

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

# Define required elements
required_elements = [
    "Job Title",
    "Job Type",
    "Job Location",
    "Job Summary",
    "Job Responsibilities",
    "Required Qualifications",
    "Benefits",
    "Company Overview",
    "Contact Information",
]

# Main screen for necessary elements
st.title(translate_text("Job Description Generator", languages[selected_language]))
necessary_inputs = {}
for element in necessary_elements:
    translated_element = translate_text(element, languages[selected_language])
    necessary_inputs[element] = st.text_input(translated_element)

# Sidebar for additional elements
st.sidebar.header("Additional Elements")
additional_elements_added = st.sidebar.multiselect(
    "Select additional elements", additional_elements
)

additional_inputs = {}
for element in additional_elements_added:
    translated_element = translate_text(element, languages[selected_language])
    additional_inputs[element] = st.text_input(translated_element)
    
   
# Add text area prompt
st.subheader(translate_text("Job Description Style", languages[selected_language]))
style_prompt = st.text_area(translate_text("What type of Job Description you want?", languages[selected_language]), placeholder="e.g. Write the Job Description for an Older Audience Ground that are Looking for saved Jobs and have a lot of Experience.")

prompt = ""
if st.button("Generate Job Description"):
    # Check if all required fields are filled
    all_required_filled = all(necessary_inputs[element] for element in required_elements)
    
    if not all_required_filled:
        st.warning("Please fill in all required fields.")
    else:
        # Modify the OpenAI API prompt based on the text from the text area
        style_prompt = f"Make a well-structured Job Description. Bold the headings. Use bullet points, numbers, or alphabets. {style_prompt}"
        if style_prompt:
            prompt += f"Write the job description in the following style: {style_prompt}\n\n"
        
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
    st.write(f"<div style='text-align: center;'><h2>Job Description</h2></div><br>{job_description_no_html}", unsafe_allow_html=True)


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

    # Save the job description as an image
    img = Image.new("RGB", (800, 1200), color="white")
    d = ImageDraw.Draw(img)
    x, y = 10, 10

    for paragraph in paragraphs:
        lines = textwrap.wrap(paragraph, width=50)
        for line in lines:
            d.text((x, y), line, fill="black")
            y += 20
        y += 10

    img_bytes = BytesIO()
    img.save(img_bytes, "PNG")
    img_bytes.seek(0)
    st.download_button(label="Download as Image", data=img_bytes, file_name="job_description.png")
