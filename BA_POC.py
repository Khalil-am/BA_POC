import os
import json
import requests
import streamlit as st
import openai
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter

# ✅ Ensure Streamlit secrets are correctly loaded
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("❌ OpenAI API key is missing! Add it in Streamlit Secrets.")
    st.stop()

# ✅ Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ✅ GitHub raw file path for JSON data
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Khalil-am/BA_POC/main/Workflows_Buttons.txt"

def load_workflows(file_url):
    """Load workflows from GitHub raw file URL"""
    try:
        response = requests.get(file_url)
        response.raise_for_status()  # Raise error if request fails
        data = json.loads(response.text)
        if not data.get("workflows"):
            raise ValueError("No workflows found in JSON structure")
        return data
    except Exception as e:
        st.error(f"🚨 Workflow loading error: {str(e)}")
        return {"workflows": []}

# ✅ Load workflows from GitHub
data = load_workflows(GITHUB_RAW_URL)
workflows = data.get("workflows", [])

# ✅ Corporate knowledge from CR documents
CORPORATE_CONTEXT = """
**HMG System Context:**
- Integrated VIDA modules (Appointments, Billing, Lab, Medical Records)
- CS360 Call Center integration
- NFC emergency check-in requirements
- Ongoing cloud migration (CR#6780)
- Dental workflow digitalization (CR#6727)
- Medical record unification initiative (CR#6691)
- Compliance with Saudi healthcare regulations
"""

def react_reasoning(workflow_details):
    """ReAct: Analyze workflow before generating BRD"""
    analysis = []

    # Check for missing steps
    if not workflow_details['steps']:
        analysis.append("⚠️ Warning: No steps are defined for this workflow.")

    # Check for missing business rules
    if not workflow_details['businessRules']:
        analysis.append("⚠️ Warning: No business rules are specified.")

    # Check for dependencies
    if not workflow_details['dependencies']:
        analysis.append("⚠️ Warning: No dependencies listed. Ensure all required integrations are included.")

    # Generate reasoning text
    reasoning_text = "\n".join(analysis) if analysis else "✅ Workflow is well-structured."
    return reasoning_text

def create_professional_pdf(content):
    """Create formatted PDF using corporate template"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Define custom styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16, spaceAfter=12)
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading2'], fontSize=14, spaceAfter=8, textColor='blue')
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=12, leading=15, spaceAfter=6)

    flowables = []

    # Add corporate header
    flowables.append(Paragraph("HMG Business Requirements Document", title_style))
    flowables.append(Spacer(1, 12))

    # Format content
    sections = content.split("\n##")
    for section in sections:
        if section.strip():
            lines = section.strip().split("\n")
            if lines:
                flowables.append(Paragraph(lines[0], header_style))  # Section Title
                for line in lines[1:]:
                    flowables.append(Paragraph(line, body_style))  # Section Content
                    flowables.append(Spacer(1, 4))

    doc.build(flowables)
    buffer.seek(0)
    return buffer

# ✅ Streamlit UI
st.title("🔗 CoRAG + ReAct: Business Requirement Generator")
st.subheader("AI-powered Documentation with Reasoning & Augmented Generation")

# ✅ Workflow selection
if workflows:
    selected_workflow = st.selectbox(
        "Select a Workflow:",
        [wf['name'] for wf in workflows],
        help="Select a workflow from the HMG process library"
    )
else:
    st.error("🚨 No workflows found! Check JSON file structure.")
    st.stop()

workflow_details = next(wf for wf in workflows if wf["name"] == selected_workflow)

# ✅ Display section
st.write(f"### 📌 Workflow: {workflow_details['name']}")
st.write(f"**Description:** {workflow_details['description']}")

# ✅ ReAct Layer: Analyzing workflow
st.subheader("🧐 ReAct: Workflow Analysis & Reasoning")
react_analysis = react_reasoning(workflow_details)
st.info(react_analysis)

# ✅ Context with CR Enhancements
context = f"""
{CORPORATE_CONTEXT}

## Workflow Specific Context
**Name:** {workflow_details['name']}
**Description:** {workflow_details['description']}

## Steps
{chr(10).join([f"- {s['action']}" for s in workflow_details['steps']])}

## Business Rules
{chr(10).join([f"- {r}" for r in workflow_details['businessRules']])}

## Dependencies
{chr(10).join([f"- {d}" for d in workflow_details['dependencies']])}

## BRD Requirements
1. Workflow changes
2. Simple impact analysis
3. Identify integration points with VIDA modules
4. Include potential CR cross-references
"""

# ✅ Customization
st.subheader("🔍 AI Customization")
user_input = st.text_area("Modify or enhance the BRD requirements:", "Generate a structured Business Requirements Document", height=150)

if "generated_br" not in st.session_state:
    st.session_state.generated_br = ""

# ✅ Generate BRD
if st.button("🔄 Generate BRD"):
    with st.spinner("Generating business requirement document..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are HMG's lead business analyst. Generate a professional BRD with:" + context},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3
            )
            st.session_state.generated_br = response.choices[0].message.content
            st.subheader("📜 Generated Business Requirement Document:")
            st.markdown(f"```\n{st.session_state.generated_br}\n```")  # Properly formatted text box

        except Exception as e:
            st.error(f"🚨 Generation failed: {str(e)}")

# ✅ Export features
if st.session_state.generated_br:
    pdf_buffer = create_professional_pdf(st.session_state.generated_br)
    st.download_button("📄 Download BRD (PDF)", pdf_buffer.getvalue(), file_name=f"BRD_{selected_workflow.replace(' ', '_')}.pdf", mime="application/pdf")
    st.download_button("📝 Download BRD (TXT)", st.session_state.generated_br.encode(), file_name=f"BRD_{selected_workflow.replace(' ', '_')}.txt")

# ✅ Related CRs
st.subheader("🔗 Related Change Requests")
cr_db = {
    "Appointment": ["CR#6727", "CR#6853"],
    "Billing": ["CR#6691", "CR#6727"],
    "Lab": ["CR#3538"],
    "Prescription": ["CR#6691"]
}
current_module = selected_workflow.split()[0]
related_crs = cr_db.get(current_module, ["No direct CR associations"])
st.write(f"Relevant Change Requests: {', '.join(related_crs)}")
