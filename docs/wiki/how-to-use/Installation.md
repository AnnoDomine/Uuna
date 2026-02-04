# ⚙️ Installation & Setup
[⬅️ Back to Home](../Home.md)

Follow these steps to set up your local instance of the WoW Library.

## 1. Clone the Repository
```bash
git clone https://github.com/hackmnin/UunaWantSomething.git
cd UunaWantSomething
```

## 2. Prepare Python Environment
We recommend using a virtual environment.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Setup Ollama (The Brains)
Install Ollama and pull the required models for our agents:
```bash
ollama pull qwen2.5:7b  # Or your preferred specialized model
```

## 4. Initialize Infrastructure
Run the project initialization script to create the necessary directory structure:
```bash
python3 Tools/core/project_init.py
```
