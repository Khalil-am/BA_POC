🚀 CoRAG + ReAct: Business Requirement Generator
This is an AI-powered Business Requirement Document (BRD) generator leveraging CoRAG (Chain-of-Retrieval Augmented Generation) and ReAct (Reasoning + Acting) to provide structured, professional BRDs for workflows.

📌 Features
✅ Workflow Selection: Choose from predefined workflows stored in a GitHub repository.
✅ ReAct Analysis: Identifies missing steps, business rules, and dependencies.
✅ CoRAG AI Generation: Generates BRDs based on structured business analysis.
✅ User Customization: Modify or enhance BRD requirements before generation.
✅ Download & Export: Save documents in PDF and TXT formats.
✅ Related Change Requests (CRs): Fetch related CRs based on the selected workflow.

🛠️ Installation
1️⃣ Clone the Repository:

sh
Copy
Edit
git clone https://github.com/Khalil-am/BA_POC.git
cd BA_POC
2️⃣ Install Dependencies:

sh
Copy
Edit
pip install -r requirements.txt
3️⃣ Run the Streamlit App:

sh
Copy
Edit
streamlit run app.py
📚 Usage
Select a workflow from the dropdown list.
View workflow analysis and see key actors, steps, and dependencies.
ReAct engine will analyze missing details and provide recommendations.
Enter custom user input to refine the BRD.
Click "Generate BRD" to get a structured document.
Download BRD in PDF or TXT format.
🏗️ Project Structure
bash
Copy
Edit
📂 BA_POC
 ├── 📜 app.py          # Main Streamlit application
 ├── 📜 requirements.txt # Required dependencies
 ├── 📜 README.md        # Project documentation
 ├── 📜 .streamlit       # Streamlit configuration files
 ├── 📂 assets           # Additional assets (if needed)
🔑 Environment Variables
Before running the application, ensure your OpenAI API key is configured:

1️⃣ Set API Key in Streamlit Secrets:
Inside .streamlit/secrets.toml, add:

toml
Copy
Edit
OPENAI_API_KEY = "your-openai-api-key-here"
2️⃣ Or set API Key as an environment variable:
sh
Copy
Edit
export OPENAI_API_KEY="your-openai-api-key-here"
🛠️ Dependencies
streamlit
openai
requests
reportlab
python-dotenv
Install all using:

sh
Copy
Edit
pip install -r requirements.txt
📤 Adding to GitHub
Follow these steps to push the repository to GitHub:

sh
Copy
Edit
# Initialize Git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit - CoRAG + ReAct BRD Generator"

# Add GitHub remote (Replace with your actual GitHub repo URL)
git remote add origin https://github.com/Cloud-Solutions/BA_POC.git

# Push changes
git push -u origin main
👥 Contributing
Want to contribute? Fork the repo and submit a pull request (PR).
For major changes, please open an issue first to discuss what you’d like to update.

📄 License
© 2025 Cloud Solutions – All Rights Reserved.

🌍 Connect With Us
📧 Email: support@cloudsolutions.com
🌐 Website: cloudsolutions.com
🚀 LinkedIn: linkedin.com/company/cloudsolutions

This README.md provides a structured overview of your project, guiding users from installation to usage and contributing. 🚀

Next Steps:
Add this file to GitHub using the commands above.
Ensure Cloud Solutions is correctly set as the repository owner.
Share with your team for further collaboration! 🎯
