
# ResuMatchAI 🚀✨📄

**ResuMatchAI** is a multi-agent AI-powered resume optimizer that compares your resume against job descriptions to help you get noticed by recruiters and ATS systems. The project uses CrewAI agents and Langchain LLMs to analyze, compare, and optimize your resume with precision. 🤖📊💼

---

> **Note:**
> I initially planned to deploy this on **Streamlit Cloud**, but due to multiple issues with package compatibility (especially with `chromadb`, `crewai`, and `sqlite3` dependencies), I decided to make this a local project instead. This ensures full flexibility and avoids runtime failures on Streamlit's restricted environment. 💻🛠️🚫

---

## 🌐 MAS Agent Workflow (Flowchart) 🧠📈⚙️

![MAS Flowchart] 🎯🎬📉![alt text](image.png)

---

## 📚 How It Works 🔍📝🔧

1. **Resume Analyzer Agent**: Extracts key information from the uploaded resume.
2. **JD Scraper Agent**: Scrapes job description from the URL.
3. **Resume vs JD Analyzer Agent**: Matches skills and calculates fit.
4. **Resume Optimizer Agent**: Enhances resume with STAR method.
5. **QA Supervisor Agent**: Validates formatting and ATS readiness.
6. **Output**: Displays a formatted summary and downloadable PDF. 🎯🎯🎯

---

## 💡 Features ⚡🧩📄

- Multi-agent system using `CrewAI`
- Job scraping via SerperDev and Web tools
- PDF upload, parsing, and optimization
- Downloadable report in PDF format 🎨📂📎

---

## 🚫 Not Supported on Streamlit Cloud 🌩️🚫📉

- The app uses versions of `crewai` and `chromadb` that require `sqlite3 >= 3.35.0`, which isn't guaranteed on Streamlit Cloud
- You may experience runtime errors like:
  ```
  RuntimeError: Your system has an unsupported version of sqlite3
  ```
- Until Streamlit updates their runtime environment, **run it locally**! 🧑‍💻💪🛠️

---

## 🚀 Run Locally (Step-by-Step) 🖥️📦🧰

### 1. Clone the repo 🔗📁🧲

```bash
git clone https://github.com/your-username/resumatchai.git
cd resumatchai
```

### 2. Install `pyenv` (if needed) 🐍⚙️🔧

```bash
curl https://pyenv.run | bash
# Follow pyenv's instructions to add to shell
```

# 🪟 Installing `pyenv-win` on Windows 💻🔧🐍

To manage and switch between different Python versions on Windows, you can install `pyenv-win` — a Windows-friendly version of `pyenv`. 🪟📌⚙️

---

### 🔄 Step-by-Step Installation

```powershell
# 1. Open PowerShell (as Administrator) and run:
Invoke-WebRequest -UseBasicParsing -Uri https://pyenv.run | Invoke-Expression

# 2. Or manually install via Git:
git clone https://github.com/pyenv-win/pyenv-win.git "$HOME\.pyenv"

# 3. Add the following paths to your system environment variables:
#    You can set these in your PowerShell profile or via the Environment Variables GUI

$env:PYENV="$HOME\.pyenv"
$env:PYENV_ROOT="$PYENV"
$env:PATH="$PYENV\pyenv-win\bin;$PYENV\pyenv-win\shims;$env:PATH"

### 🔁 Restart your terminal or PowerShell window to apply the changes.

### ✅ Verify Installation 🧪🔍⚙️
Once you've completed the installation and updated your environment variables, restart your terminal and run the following command:
pyenv --version

### 3. Install Python 3.11 🐍📥📌

```bash
pyenv install 3.11.6
pyenv local 3.11.6
```

### 4. Create a virtual environment 🧪🌐🛡️

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 5. Install dependencies 📦📜📌

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Set your API Keys 🔑🌍🔐

Create a `.env` file and include:

```
OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_KEY=your_deepseek_key
SERPER_API_KEY=your_serperdev_key
```

> **Make sure `.env` is in your `.gitignore`!** 🔒📂❌

### 7. Run the app ▶️📊🖼️

```bash
streamlit run main.py
```

---

## 🔐 Notes for Developers ⚙️💬📌

- Uses `dotenv` to load environment variables
- Uses `CrewAI` for agent workflow
- Resumes must be in **PDF format**
- Job description must be from a **valid URL** 🧩📁🔧

---

## 🙏 Acknowledgments 🌟💖🙌

- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [LangChain](https://www.langchain.com/)
- [Streamlit](https://streamlit.io) 🎉🎈🎁

---

Feel free to fork, star, and contribute! 🚀💬🤝

> Built with ❤️ by Harshith Sakala 🎨🧠🌟
