import json
import os
import streamlit as st
import openai
from dotenv import load_dotenv
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
import requests

# Load environment variables
load_dotenv()


# React-inspired state management
class WorkflowState:
    def __init__(self):
        self.current_view = "default"
        self.new_workflow = {}
        self.form_step = 0


class WorkflowManager:
    def __init__(self):
        self.state = st.session_state.setdefault('workflow_state', WorkflowState())

    def set_view(self, view_name):
        self.state.current_view = view_name

    def update_form_data(self, field, value):
        self.state.new_workflow[field] = value

    def reset_form(self):
        self.state.new_workflow = {}
        self.state.form_step = 0


# Initialize components
workflow_manager = WorkflowManager()

# GitHub raw file path for JSON data
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Khalil-am/BA_POC/main/Workflows_Buttons.txt"


def load_workflows(file_url):
    """Load workflows from GitHub raw file URL"""
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        data = json.loads(response.text)
        return data.get("workflows", [])
    except Exception as e:
        st.error(f"Workflow loading error: {str(e)}")
        return []


# Load workflows from GitHub
all_workflows = load_workflows(GITHUB_RAW_URL)

# Corporate context remains the same
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


def WorkflowCreator():
    """React-inspired component for new workflow creation"""
    st.write("## 🛠️ New Workflow Creation")

    steps = [
        ("Basic Info", ["name", "description"]),
        ("Workflow Steps", ["steps"]),
        ("Business Rules", ["businessRules"]),
        ("Dependencies", ["dependencies"])
    ]

    current_step = workflow_manager.state.form_step

    # Step navigation
    cols = st.columns(4)
    for i, (step_name, _) in enumerate(steps):
        cols[i].button(step_name, disabled=i != current_step,
                       on_click=workflow_manager.set_view, args=(f"step_{i}",))

    # Form content
    with st.form("workflow_form"):
        # Step 1: Basic Info
        if current_step == 0:
            name = st.text_input("Workflow Name")
            description = st.text_area("Workflow Description")

            if st.form_submit_button("Next →"):
                workflow_manager.update_form_data("name", name)
                workflow_manager.update_form_data("description", description)
                workflow_manager.state.form_step += 1

        # Step 2: Workflow Steps
        elif current_step == 1:
            steps = st.text_area("Enter steps (one per line)",
                                 help="Format: Step Number|Action|Notes\nExample: 1|Patient login|Authentication required")

            if st.form_submit_button("Next →"):
                parsed_steps = []
                for line in steps.split('\n'):
                    parts = line.split('|')
                    if len(parts) >= 3:
                        parsed_steps.append({
                            "stepNumber": parts[0].strip(),
                            "action": parts[1].strip(),
                            "notes": parts[2].strip()
                        })
                workflow_manager.update_form_data("steps", parsed_steps)
                workflow_manager.state.form_step += 1

        # Step 3: Business Rules
        elif current_step == 2:
            rules = st.text_area("Enter business rules (one per line)")

            if st.form_submit_button("Next →"):
                workflow_manager.update_form_data("businessRules", rules.split('\n'))
                workflow_manager.state.form_step += 1

        # Step 4: Dependencies
        elif current_step == 3:
            deps = st.text_area("Enter dependencies (one per line)")

            if st.form_submit_button("Submit Workflow"):
                workflow_manager.update_form_data("dependencies", deps.split('\n'))
                all_workflows.append(workflow_manager.state.new_workflow)
                workflow_manager.reset_form()
                workflow_manager.set_view("default")
                st.success("Workflow created successfully!")


def BRDGenerator(workflow):
    """React-inspired BRD generation component"""
    st.write(f"## 📄 Generating BRD for: {workflow['name']}")

    # Stateful document construction
    if 'brd_sections' not in st.session_state:
        st.session_state.brd_sections = {
            'objectives': '',
            'scope': '',
            'requirements': '',
            'risks': ''
        }

    # Document builder form
    with st.form("brd_builder"):
        st.session_state.brd_sections['objectives'] = st.text_area("Business Objectives")
        st.session_state.brd_sections['scope'] = st.text_area("Project Scope")
        st.session_state.brd_sections['requirements'] = st.text_area("Functional Requirements")
        st.session_state.brd_sections['risks'] = st.text_area("Risk Analysis")

        if st.form_submit_button("Generate Final BRD"):
            full_brd = assemble_brd(workflow)
            st.session_state.generated_br = full_brd
            st.rerun()


def assemble_brd(workflow):
    """Combine user inputs with AI generation"""
    context = f"""
    {CORPORATE_CONTEXT}
    Workflow Details: {json.dumps(workflow, indent=2)}
    User Inputs: {json.dumps(st.session_state.brd_sections, indent=2)}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "Combine corporate context with user inputs to create professional BRD:"
            }, {
                "role": "user",
                "content": context
            }],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Generation failed: {str(e)}")
        return ""


# Main App Component
def App():
    """Root application component"""
    st.title("🔗 CoRAG: Business Requirement Generator")
    st.subheader("React-inspired Workflow Management System")

    # Navigation
    col1, col2 = st.columns(2)
    if col1.button("🏠 Existing Workflows"):
        workflow_manager.set_view("default")
    if col2.button("🆕 Create New Workflow"):
        workflow_manager.set_view("create")

    # View routing
    if workflow_manager.state.current_view == "create":
        WorkflowCreator()
    else:
        DefaultView()


def DefaultView():
    """Main workflow selection and BRD generation view"""
    if not all_workflows:
        st.error("🚨 No workflows found! Check data source.")
        return

    # Workflow selection
    selected_workflow = st.selectbox(
        "Select Workflow:",
        [wf['name'] for wf in all_workflows],
        help="Choose from existing workflows"
    )

    workflow = next(wf for wf in all_workflows if wf['name'] == selected_workflow)

    # Workflow analysis dashboard
    with st.expander("📊 Workflow Analysis", expanded=True):
        cols = st.columns(3)
        cols[0].metric("Steps", len(workflow.get('steps', [])))
        cols[1].metric("Business Rules", len(workflow.get('businessRules', [])))
        cols[2].metric("Dependencies", len(workflow.get('dependencies', [])))

        st.write(f"**Actors:** {', '.join(workflow.get('actors', []))}")
        st.write(f"**Expected Outcome:** {workflow.get('expectedOutcome', '')}")

    # BRD generation workflow
    BRDGenerator(workflow)

    # Display generated BRD
    if 'generated_br' in st.session_state:
        st.subheader("📜 Final Business Requirement Document")
        st.markdown(f"```\n{st.session_state.generated_br}\n```")

        # Export functionality
        pdf_buffer = create_professional_pdf(st.session_state.generated_br)
        st.download_button("📄 Download BRD (PDF)", pdf_buffer.getvalue(),
                           file_name=f"BRD_{selected_workflow.replace(' ', '_')}.pdf",
                           mime="application/pdf")

        # Related CRs
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


# PDF generation function remains the same
def create_professional_pdf(content):
    """Create formatted PDF using corporate template"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    flowables = []

    # Add corporate header
    header = Paragraph("HMG Business Requirements Document", styles['Title'])
    flowables.append(header)
    flowables.append(Spacer(1, 12))

    # Format content
    for section in content.split('\n##'):
        if section.strip():
            p = Paragraph(section.replace('#', '').strip(), styles['BodyText'])
            flowables.append(p)
            flowables.append(Spacer(1, 8))

    doc.build(flowables)
    buffer.seek(0)
    return buffer


# Run the app
if __name__ == "__main__":
    App()