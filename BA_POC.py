import os
import json
import requests
import streamlit as st
import openai
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter


# React-inspired state management
class AppState:
    def __init__(self):
        self.selected_workflow = None
        self.generated_brd = None
        self.user_input = ""
        self.show_analysis = True


# Initialize OpenAI client
try:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("❌ OpenAI API key is missing! Add it in Streamlit Secrets.")
    st.stop()

# GitHub raw file path
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Khalil-am/BA_POC/main/Workflows_Buttons.txt"


def load_workflows():
    """Data fetcher with error handling"""
    try:
        response = requests.get(GITHUB_RAW_URL)
        response.raise_for_status()
        data = json.loads(response.text)
        return data.get("workflows", [])
    except Exception as e:
        st.error(f"🚨 Workflow loading error: {str(e)}")
        return []


def WorkflowSelector(props):
    """Workflow selection component"""
    workflows = props['workflows']
    selected = props['selected']
    on_select = props['on_select']

    with st.container():
        st.subheader("📋 Available Workflows")
        selected_wf = st.selectbox(
            "Select a Workflow:",
            [wf['name'] for wf in workflows],
            index=next((i for i, wf in enumerate(workflows) if wf['name'] == selected), 0),
            key="workflow_selector",
            on_change=lambda: on_select(st.session_state.workflow_selector)
        )
    return selected_wf


def WorkflowAnalysis(props):
    """Workflow insights component"""
    workflow = props['workflow']

    with st.expander("🔍 Workflow Analysis", expanded=True):
        cols = st.columns(3)
        cols[0].metric("Steps", len(workflow.get('steps', [])))
        cols[1].metric("Business Rules", len(workflow.get('businessRules', [])))
        cols[2].metric("Dependencies", len(workflow.get('dependencies', [])))

        st.write(f"**Actors:** {', '.join(workflow.get('actors', []))}")
        st.write(f"**Expected Outcome:** {workflow.get('expectedOutcome', '')}")


def ReActComponent(props):
    """Analysis component"""
    workflow = props['workflow']

    analysis = []
    if not workflow['steps']:
        analysis.append("⚠️ Missing workflow steps")
    if not workflow['businessRules']:
        analysis.append("⚠️ No business rules defined")
    if not workflow['dependencies']:
        analysis.append("⚠️ Missing system dependencies")

    with st.container():
        st.subheader("🧠 ReAct Analysis Engine")
        if analysis:
            for issue in analysis:
                st.error(issue)
        else:
            st.success("✅ Workflow structure validated")
        st.info("💡 Recommendation: Always verify integration points with VIDA modules")


def BRDGenerator(props):
    """BRD generation component"""
    state = props['state']
    workflows = props['workflows']

    with st.form("brd_generator"):
        st.subheader("📝 BRD Customization")
        user_input = st.text_area(
            "Enhance BRD requirements:",
            value=state.user_input,
            height=150,
            key="brd_input"
        )

        if st.form_submit_button("🔄 Generate BRD"):
            state.user_input = user_input
            state.generated_brd = generate_brd(state, workflows)
            st.rerun()


def generate_brd(state, workflows):
    """BRD generation logic"""
    try:
        workflow = next(wf for wf in workflows if wf["name"] == state.selected_workflow)
    except StopIteration:
        st.error("Selected workflow not found")
        return None

    context = f"""
    {CORPORATE_CONTEXT}
    ## Workflow Details
    {json.dumps(workflow, indent=2)}
    ## User Customizations
    {state.user_input}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a senior business analyst. Generate professional BRD:"
            }, {
                "role": "user",
                "content": context
            }],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"🚨 Generation failed: {str(e)}")
        return None


def BRDExporter(props):
    """Export component"""
    brd_content = props['content']

    with st.container():
        st.subheader("📤 Document Export")
        pdf_buffer = create_professional_pdf(brd_content)

        col1, col2 = st.columns(2)
        col1.download_button(
            "📄 Download PDF",
            data=pdf_buffer.getvalue(),
            file_name="business_requirements.pdf",
            mime="application/pdf"
        )
        col2.download_button(
            "📝 Download TXT",
            data=brd_content.encode(),
            file_name="business_requirements.txt"
        )


def create_professional_pdf(content):
    """PDF generator"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    flowables = [
        Paragraph("HMG Business Requirements Document", styles['Title']),
        Spacer(1, 24)
    ]

    sections = content.split("\n##")
    for section in sections:
        if section.strip():
            title, *body = section.strip().split("\n")
            flowables.append(Paragraph(title, styles['Heading2']))
            for line in body:
                flowables.append(Paragraph(line, styles['BodyText']))
            flowables.append(Spacer(1, 12))

    doc.build(flowables)
    buffer.seek(0)
    return buffer


def RelatedCRs(props):
    """CR component"""
    workflow_name = props['workflow_name']
    cr_db = {
        "Appointment": ["CR#6727", "CR#6853"],
        "Billing": ["CR#6691", "CR#6727"],
        "Lab": ["CR#3538"],
        "Prescription": ["CR#6691"]
    }

    module = workflow_name.split()[0]
    crs = cr_db.get(module, ["No related CRs"])

    with st.container():
        st.subheader("🔗 Related Change Requests")
        st.write(", ".join(crs))


def main():
    """Main application"""
    st.title("🔗 CoRAG + ReAct: Business Requirement Generator")
    st.subheader("Enterprise Documentation System")

    # Initialize state
    if 'app_state' not in st.session_state:
        st.session_state.app_state = AppState()

    state = st.session_state.app_state
    workflows = load_workflows()

    # Main layout
    if not workflows:
        st.error("🚨 No workflows available")
        return

    # Workflow selection
    state.selected_workflow = WorkflowSelector({
        'workflows': workflows,
        'selected': state.selected_workflow,
        'on_select': lambda wf: setattr(state, 'selected_workflow', wf)
    })

    # Get current workflow
    try:
        workflow = next(wf for wf in workflows if wf["name"] == state.selected_workflow)
    except StopIteration:
        st.error("Selected workflow not found in database")
        return

    # Analysis components
    WorkflowAnalysis({'workflow': workflow})
    ReActComponent({'workflow': workflow})

    # BRD generation
    BRDGenerator({'state': state, 'workflows': workflows})

    # Display generated BRD
    if state.generated_brd:
        st.subheader("📜 Generated Business Requirement Document")
        st.markdown(f"```\n{state.generated_brd}\n```")
        BRDExporter({'content': state.generated_brd})

    # Related CRs
    RelatedCRs({'workflow_name': state.selected_workflow})


# Corporate context
CORPORATE_CONTEXT = """
**HMG application System Context:**
- Integrated VIDA modules (Appointments, Billing, Lab, Medical Records)
- CS360 Call Center integration
- NFC emergency check-in requirements
- Dental workflow digitalization (CR#6727)
- Medical record unification initiative (CR#6691)
- Compliance with Saudi healthcare regulations
"""

if __name__ == "__main__":
    main()