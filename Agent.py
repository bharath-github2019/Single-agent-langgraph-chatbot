# =========================
# Imports & Setup
# =========================

from typing import TypedDict, List
from datetime import datetime
import builtins

from dotenv import load_dotenv
from openai import AzureOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
load_dotenv(override=True)


# =========================
# Azure OpenAI Client
# =========================

client = AzureOpenAI(
    api_key=AZURE_KEY,
    api_version=AZURE_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
)


# =========================
# Global Conversation Store
# =========================

# Stores the full conversation across turns
conversation_history: List[HumanMessage | AIMessage] = []


# =========================
# Agent State Definition
# =========================

class AgentState(TypedDict):
    messages: List[HumanMessage | AIMessage]


# =========================
# Core Processing Node
# =========================

def process_node(state: AgentState) -> AgentState:
    """
    Sends the full conversation history + current message to the LLM
    and appends the AI response to the state.
    """

    messages_payload = []

    # Add full conversation history
    for message in conversation_history:
        role = "assistant" if isinstance(message, AIMessage) else "user"
        messages_payload.append(
            {"role": role, "content": message.content}
        )

    # Add current turn messages
    for message in state["messages"]:
        role = "assistant" if isinstance(message, AIMessage) else "user"
        messages_payload.append(
            {"role": role, "content": message.content}
        )

    print(f"\nSending {len(messages_payload)} messages to AI...")

    completion = client.chat.completions.create(
        model=AZURE_CHAT_DEPLOYMENT,
        messages=messages_payload,
    )

    reply = completion.choices[0].message.content
    print("\nAI:", reply)

    state["messages"].append(AIMessage(content=reply))
    return state


# =========================
# Conversation Persistence
# =========================

def save_conversation_to_file() -> str | None:
    """
    Saves the complete conversation to a timestamped file.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"conversation_history_{timestamp}.txt"

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("=== CONVERSATION HISTORY ===\n")
            file.write(f"Saved: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
            file.write(f"Total messages: {len(conversation_history)}\n")
            file.write("=" * 50 + "\n\n")

            for i, message in enumerate(conversation_history, 1):
                label = "AI" if isinstance(message, AIMessage) else "USER"
                file.write(f"[{i:02d}] {label}: {message.content}\n\n")

            file.write("=" * 50 + "\n")
            file.write("=== END OF CONVERSATION ===\n")

        print(f"Conversation saved to: {filename}")
        return filename

    except Exception as e:
        print(f"Error saving conversation: {e}")
        return None


def auto_save_conversation() -> None:
    """
    Auto-saves the ongoing conversation after every exchange.
    """

    if not conversation_history:
        return

    try:
        with open("current_conversation.txt", "w", encoding="utf-8") as file:
            file.write("=== CURRENT CONVERSATION ===\n")
            file.write(f"Last updated: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
            file.write(f"Messages: {len(conversation_history)}\n")
            file.write("=" * 40 + "\n\n")

            for i, message in enumerate(conversation_history, 1):
                label = "AI" if isinstance(message, AIMessage) else "USER"
                file.write(f"[{i:02d}] {label}: {message.content}\n\n")

            file.write("=" * 40 + "\n")
            file.write("(Auto-saved – conversation continues...)\n")

    except Exception as e:
        print(f"Auto-save error: {e}")


# =========================
# LangGraph Setup
# =========================

graph = StateGraph(AgentState)
graph.add_node("process", process_node)
graph.add_edge(START, "process")
graph.add_edge("process", END)

agent = graph.compile()


# =========================
# Interactive Chat Loop
# =========================

print("Chat with the AI")
print("Commands: 'exit' to quit | 'save' to manually save")
print("Auto-saving to 'current_conversation.txt'")
print("AI remembers the full conversation")

user_input = builtins.input("\nYou: ")

while user_input.lower() not in {"exit", "quit"}:

    if user_input.lower() == "save":
        save_conversation_to_file()
        user_input = builtins.input("\nYou: ")
        continue

    # Create and store user message
    user_message = HumanMessage(content=user_input)
    conversation_history.append(user_message)

    # Invoke agent with only the new message
    final_state = agent.invoke({"messages": [user_message]})

    # Store AI response
    ai_message = final_state["messages"][-1]
    conversation_history.append(ai_message)

    # Auto-save after each exchange
    auto_save_conversation()

    print(f"[Messages: {len(conversation_history)}]")
    user_input = builtins.input("\nYou: ")


# =========================
# Final Save on Exit
# =========================

print("\nSaving final conversation...")
final_filename = save_conversation_to_file()
print(f"Goodbye. Conversation saved in '{final_filename}'.")
