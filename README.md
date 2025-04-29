# Multi-Agent Moot Court Debate – The Last of Us: The Case of Joel's Death

## 🚀 Project Overview

This project simulates a structured courtroom debate around the morally complex events in The Last of Us Part II, focusing on Ellie and Abby's perspectives following Joel's murder. The debate explores themes of revenge, justice, grief, and moral ambiguity through a legal framework.

## 🧠 Agents and Roles

- **Debater A (Ellie's Attorney)**: Defends Ellie's actions using her personal testimony as source material.
- **Debater B (Abby's Attorney)**: Defends Abby's actions using her personal testimony as source material.
- **Moderator**: Acts like a courtroom judge or mediator. Introduces rounds, maintains order, asks clarification questions.
- **Judge**: Evaluates both sides' arguments at the end and delivers a reasoned verdict.

## 📁 Project Structure

- `/testimonies/` - Character testimonies from Ellie and Abby
- `/prompts/` - Agent prompts and system instructions
- `/frontend/` - Web UI for the debate
- `/debate_format.md` - Rules and structure for the debate
- `/implementation.md` - Technical implementation details

## 🛠️ Setup and Installation

1. Clone this repository
2. Run the setup script to create a virtual environment and install dependencies:
   ```
   python setup.py
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Edit the `.env` file to add your OpenAI API key
5. Start the debate server:
   ```
   python debate_orchestrator.py
   ```
6. Open your browser to http://localhost:8000

## 🎯 Goal

To create a compelling, nuanced exploration of the moral complexities in The Last of Us Part II through a structured debate format, allowing for deep examination of the characters' motivations, actions, and their consequences.
