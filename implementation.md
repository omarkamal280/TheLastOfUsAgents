# Technical Implementation Details

## 1. Dependencies

- Python 3.8+
- OpenAI Python SDK
- python-dotenv (optional for managing environment variables)

## 2. Environment Setup

1. Create a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key in environment variable `OPENAI_API_KEY` or create a `.env` file based on `.env.example`.

## 3. Running the Debate Orchestrator

```powershell
python debate_orchestrator.py
```

The script will:
- Load system prompts from `/prompts/`
- Load testimonies from `/testimonies/`
- Sequence the debate rounds via OpenAI ChatCompletion API
- Log all messages to `debate_transcript.log`
- Print the final verdict to the console

## 4. File Structure

```text
/TheLastOfUs/
├─ debate_orchestrator.py
├─ requirements.txt
├─ .env.example
├─ project_framework.md
├─ debate_format.md
├─ implementation.md
├─ README.md
├─ /prompts/
│  ├─ ellie_attorney.md
│  ├─ abby_attorney.md
│  ├─ moderator.md
│  └─ judge.md
└─ /testimonies/
   ├─ ellie_testimony.md
   └─ abby_testimony.md
```

## 5. Logging & Transcripts

- All agent messages and timestamps are written to `debate_transcript.log`.

## 6. Optional UI

You can build a simple CLI or web dashboard to stream messages live from `debate_transcript.log` or integrate with a frontend framework.
