<p align="center">
  <a href="https://brightdata.com/">
    <img src="https://mintlify.s3.us-west-1.amazonaws.com/brightdata/logo/light.svg" width="300" alt="Bright Data Logo">
  </a>
</p>

<div align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue"/>
  <img src="https://img.shields.io/badge/License-MIT-blue"/>
</div>

---


# 🚀 GEO AI Content Optimization Agent

This project uses LangGraph to automate AI-driven webpage content audits. Enter a URL, and the system accesses the webpage, extracts its title, generates and summarizes related queries using Gemini with the Google Search tool, fetches Google AI Overviews via Bright Data SERP API, compares results, and outputs actionable page-level optimization suggestions in Markdown files.

<img src="https://github.com/brightdata/geo-ai-agent/blob/main/GEO%20diagram.png"/>

---

## 🤖 Understanding Your Workflow

The `ai_content_optimization_agent` workflow is composed of six AI agents, each with unique roles and goals. These agents collaborate on a series of tasks, leveraging their collective skills to achieve complex objectives. All logic is now implemented in Python using LangGraph, with agent definitions in `src/ai_content_optimization_agent/agents/`.

## 🛠️ Installation

Ensure you have **Python >=3.10 <3.14** installed on your system.

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management and package handling.
First, if you haven't already, install `uv`:

```bash
pip install uv
```

Next, navigate to your project directory and install the project's dependencies:

```bash
cd geo-ai-agent
uv sync
```

---

## 🔑 Environment Configuration

This project requires four environment variables to work:
- **`GEMINI_API_KEY`**: Your Gemini API key.
- **`MODEL`**: The name of the Gemini model to power your crew of agents (e.g., `gemini/gemini-2.5-flash`).
- **`BRIGHT_DATA_API_KEY`**: Your [Bright Data API key](https://docs.brightdata.com/api-reference/authentication).
- **`BRIGHT_DATA_ZONE`**: The name of the [Web Unlocker zone in your Bright Data dashboard](https://docs.brightdata.com/scraping-automation/web-unlocker/quickstart) you want to connect to.

Define them directly in your terminal or place them in a `.env` file at the root of your project:
```
geo-ai-agent/
├── ...
├── .env # <---
└── src/
    └── ai_content_optimization_agent/
        └── ...
```
Populate the `.env` file like this:
```
GEMINI_API_KEY="<YOUR_GEMINI_API_KEY>"
MODEL="<CHOSEN_GEMINI_MODEL>"
BRIGHT_DATA_API_KEY="<BRIGHT_DATA_API_KEY>"
BRIGHT_DATA_ZONE="<YOUR_BRIGHT_DATA_ZONE>"
```


## ▶️ Running the Project
Activate the `.venv` created by the `uv sync` command:
```bash
source .venv/bin/activate
```
Or, on Windows:
```powershell
.venv/Scripts/activate
```

With the virtual environment activated, start the LangGraph workflow by running:
```bash
python src/ai_content_optimization_agent/main.py
```
or from the project root (if your PYTHONPATH is set):
```bash
python -m src.ai_content_optimization_agent.main
```

This will prompt you for a URL and run the full AI content optimization workflow. Output files will be saved in the `output/` directory, including `output/report.md` and other intermediate results.

---


### ⚙️ Customizing
- 🔧 Update the `MODEL` environment variable to change the Gemini model used by the workflow.
- 🧑‍💻 Edit agent logic in `src/ai_content_optimization_agent/agents/` to modify agent behavior.
- ⚡ Edit `src/ai_content_optimization_agent/main.py` to add custom inputs or workflow logic.

---


## 💬 Support

For support, questions, or feedback regarding the `ai_content_optimization_agent` workflow:
- ☀️ Visit Bright Data's [SERP API docs](https://docs.brightdata.com/scraping-automation/serp-api/introduction)

---

✨ Let's create wonders together with the power and simplicity of Bright Data & LangGraph.
