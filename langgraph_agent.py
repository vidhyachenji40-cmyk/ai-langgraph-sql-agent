import sqlite3
import os
import anthropic
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

# 1. LOAD SECRETS (Breathes in the values from your .env file)
load_dotenv()
project_id = os.getenv("GCP_PROJECT_ID")
region = os.getenv("GCP_REGION")
api_key = os.getenv("ANTHROPIC_API_KEY")

# 2. STATE DEFINITION
class AgentState(TypedDict):
    question: str
    sql: str
    results: str
    error: str
    attempts: int

# Initialize client using the variable from load_dotenv()
client = anthropic.Anthropic(api_key=api_key)
DB_PATH = "Bikes.db"

# 3. NODES
def sql_writer(state: AgentState):
    print(f"\n[NODE: WRITER] Generating SQL... (Attempt {state['attempts'] + 1})")
    
    system_msg = "You are a SQLite expert. Provide ONLY the raw SQL query. No markdown, no explanation."
    user_msg = f"Database Schema: products, categories, stocks, stores, order_items, orders, customers, staffs, brands.\n\nQuestion: {state['question']}"
    
    if state['error']:
        user_msg += f"\n\nYour previous SQL failed: {state['sql']}\nSQLite Error: {state['error']}\nAnalyze the error and provide the corrected SQL."

    res = client.messages.create(
        model="claude-sonnet-4-6", # Kept exactly as you requested
        max_tokens=300,
        system=system_msg,
        messages=[{"role": "user", "content": user_msg}]
    )
    return {"sql": res.content[0].text.strip(), "attempts": state['attempts'] + 1}

def db_executor(state: AgentState):
    print("[NODE: EXECUTOR] Testing SQL...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(state['sql'])
        rows = cur.fetchall()
        cols = [description[0] for description in cur.description]
        conn.close()
        return {"results": f"Columns: {cols}\nRows: {rows}", "error": ""}
    except Exception as e:
        print(f"!! ERROR ENCOUNTERED: {e}")
        return {"error": str(e)}

def presenter(state: AgentState):
    print("[NODE: PRESENTER] Returning result.")
    if state['error']:
        return {"results": f"FAILED after {state['attempts']} attempts. Last error: {state['error']}"}
    return {"results": state['results']}

# 4. GRAPH CONSTRUCTION
workflow = StateGraph(AgentState)

workflow.add_node("writer", sql_writer)
workflow.add_node("executor", db_executor)
workflow.add_node("presenter", presenter)

workflow.set_entry_point("writer")
workflow.add_edge("writer", "executor")

def decide_next_step(state: AgentState):
    if state["error"] and state["attempts"] < 5:
        return "writer"
    return "presenter"

workflow.add_conditional_edges("executor", decide_next_step)
workflow.add_edge("presenter", END)

app = workflow.compile()

# 5. RUN
if __name__ == "__main__":
    print("\n--- SELF-HEALING BIKE AGENT ---")
    while True:
        user_q = input("\nAsk a question (or 'exit'): ")
        if user_q.lower() == 'exit': break
        
        inputs = {"question": user_q, "attempts": 0, "error": "", "sql": "", "results": ""}
        final_state = app.invoke(inputs)
        print(f"\nFINAL RESULT:\n{final_state['results']}")
