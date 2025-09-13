# Insurance Agent Lab

**An LLM-based autonomous Router Agent framework for insurance and media workflows.**

---

## Overview

`insurance-agent-lab` is a Python project that provides a dynamic, LLM-driven agent system capable of routing user requests to specialized agents for insurance and media tasks. It integrates with AWS Bedrock for LLM processing and supports modular tools like script generation, TTS, slides, and media handling.

The project structure is designed for experimentation and rapid prototyping of autonomous workflows.

---

## Features

- **Router Agent**: Central hub that interprets user input and routes it to the appropriate agent.
- **Dynamic Agent Loading**: Agents are registered dynamically from the `agents/` folder.
- **LLM Integration**: Uses AWS Bedrock for natural language understanding.
- **Modular Tools**: Script generation, TTS, slide creation, media processing.
- **Graceful Fallbacks**: Handles unrecognized input without crashing.
- **Logging & Debugging**: Captures LLM outputs and agent activity for easy debugging.

---

## Project Structure

```
insurance-agent-lab/
├── agents/
│   ├── agent_media_autonomous.py  # Dynamic LLM-driven agent
│   └── agent_media_control.py     # Previous version agent
├── router/
│   ├── router_agent.py            # Main router agent
│   └── agent_registry.py          # Dynamic agent registry
├── tools/
│   ├── script_gen.py
│   ├── catalog.py
│   ├── tts.py
│   ├── slides.py
│   └── nova_video.py
├── bedrock_helper.py              # LLM API wrapper
├── .gitignore
└── README.md
```

---

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/roy777rajat/insurance-agent-lab.git
cd insurance-agent-lab
```

2. **Create a virtual environment**
```bash
python -m venv venv
```

3. **Activate the environment**
- Windows:
```bash
venv\Scripts\activate
```
- macOS/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

> Note: Add any project-specific dependencies to `requirements.txt`.

---

## Usage

1. **Run the router agent**
```bash
python router/router_agent.py
```

2. **Interact with the agent**
- Enter your request (insurance workflow or media task) in the console.
- The router will parse your input, determine the correct agent, and execute the workflow.

---

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and commit: `git commit -m "Add your message"`
4. Push to your branch: `git push origin feature/your-feature`
5. Open a pull request.

---



## Contact

Rajat Roy  
- GitHub: [https://github.com/roy777rajat](https://github.com/roy777rajat)  
- Email: `roy777rajat@gmail.com`

