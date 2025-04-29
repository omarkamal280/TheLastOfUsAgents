# Project Framework

## 1. Debate Format and Rules

- **Rounds**: Opening Statements, Evidence Presentation, Rebuttals, Cross-Examination, Closing Statements
- **Time/Turn Limits**: e.g., 1–3 messages per participant per round
- **Moderator**: Introduces each round, enforces turn order, asks clarifying questions
- **Judge**: Observes debate silently; delivers final verdict based on arguments
- **Allowed Evidence**: Only in-game events and provided testimonies; no external lore

## 2. Character Profiles

- **Debater A (Ellie’s Attorney)**
  - Tone: Empathetic, protective
  - Goal: Justify Ellie’s actions as necessary justice
  - Source Material: `testimonies/ellie_testimony.md`

- **Debater B (Abby’s Attorney)**
  - Tone: Principled, resolute
  - Goal: Argue Abby’s revenge as moral and justified
  - Source Material: `testimonies/abby_testimony.md`

- **Moderator**
  - Tone: Neutral, authoritative
  - Responsibilities: Open/close rounds, manage timing, pose clarifications

- **Judge**
  - Tone: Analytical, unbiased
  - Responsibilities: Evaluate adherence to rules, assess persuasiveness, issue verdict

## 3. Key Evidence from the Game

- **Joel’s Death Scene**: motive and trauma for Ellie
- **Abby’s Flashback**: her father’s murder by Joel (Firefly mission)
- **Ellie’s Hunt**: collateral victims and moral cost
- **Abby’s Actions**: loss of allies, personal sacrifice
- **Supporting Scenes**: Dina/Jesse, Lev/Northwest Settlement

## 4. Technical Implementation Details

- **Directory Layout**:
  - `/testimonies/` – saved testimonies
  - `/prompts/` – system/user prompts for agents
  - `project_framework.md` – this outline
  - `debate_orchestrator.py` – orchestrates LLM calls
  - `implementation.md` – detailed technical notes

- **Agent Orchestration**:
  - Use OpenAI chat API (or similar) to instantiate four agents
  - Sequence rounds via a controller script
  - Maintain context/history for each agent turn

- **Prompts**:
  - Store in `/prompts/ellie_attorney.md`, `/prompts/abby_attorney.md`, etc.
  - Define system instructions, role descriptions, and referencing testimonies

- **Logging & Verdict**:
  - Log all messages to file
  - Final judge prompt ingests transcript and outputs verdict summary

- **Optional UI**:
  - CLI runner or lightweight web dashboard for live debate
  - Display messages and verdict
