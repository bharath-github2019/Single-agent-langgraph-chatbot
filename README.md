# Single-agent-langgraph-chatbot

This project implements a stateful conversational AI agent using Azure OpenAI, LangGraph, and LangChain messages, with full conversation memory and automatic persistence to disk.
# The agent:
Remembers the entire conversation history
Sends full context to Azure OpenAI on every turn
Auto-saves conversations after each exchange
Allows manual saving and final export on exit
# Features
Full conversation memory across turns
LangGraph-based agent execution flow
Azure OpenAI Chat Completions integration
Auto-save to current_conversation.txt
Timestamped conversation exports
Interactive CLI chat loop

# Project structure 

.
├── main.py                     # Core chat application
├── current_conversation.txt    # Auto-saved live conversation
├── conversation_history_*.txt  # Timestamped saved conversations
├── .env                        # # Environment variables
└── README.md

# Installation
Clone the repository
Copy code
Bash
git clone <your-repo-url>
cd <your-repo-name>
Create and activate a virtual environment (recommended)
Copy code
Bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
Install dependencies
Copy code
Bash
pip install openai langgraph langchain-core python-dotenv
Environment Variables
Create a .env file in the project root with the following values:
Copy code
Env
AZURE_KEY=your_azure_openai_api_key
AZURE_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_VERSION=2024-02-15-preview
AZURE_CHAT_DEPLOYMENT=your_chat_model_deployment_name
