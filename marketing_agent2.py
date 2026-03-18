import sqlite3
import csv
import vertexai
from typing import TypedDict
from vertexai.generative_models import GenerativeModel
from langgraph.graph import StateGraph, END

# 1. SETUP
vertexai.init(project="project-450e81d6-945c-48ed-b6e", location="us-central1")
model = GenerativeModel("gemini-2.0-flash-001")

class AgentState(TypedDict):
    customer_list: list
    current_email: str
    current_tone: str
    index: int
    report_data: list

# 2. NODES

def data_fetcher(state: AgentState):
    """Pulls pending customers including their Genre."""
    print("[NODE: FETCHER] Checking for new pending customers...")
    conn = sqlite3.connect('Bikes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # We now include 'Genre' in the selection
    cursor.execute("""
        SELECT ROWID as age_mock, first_name, city, Genre 
        FROM customers 
        WHERE city = 'Orchard Park' AND status = 'pending'
        ORDER BY ROWID DESC 
        LIMIT 5
    """)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("[NODE: FETCHER] 0 pending customers found.")
        return {"customer_list": [], "index": 0, "report_data": []}
    
    processed_rows = []
    for row in rows:
        d = dict(row)
        d['age'] = 60 if d['age_mock'] % 2 == 0 else 25 
        processed_rows.append(d)
        
    print(f"[NODE: FETCHER] Found {len(processed_rows)} customers.")
    return {"customer_list": processed_rows, "index": 0, "report_data": []}

def tone_analyzer(state: AgentState):
    customer = state['customer_list'][state['index']]
    age = int(customer['age'])
    
    if age > 50:
        tone = "Professional, focusing on scenery and comfort."
    else:
        tone = "High-energy, focusing on adrenaline and speed."
    
    print(f"[NODE: ANALYZER] {customer['first_name']} ({customer.get('Genre', 'User')}, Age {age}) -> Tone: {tone}")
    return {"current_tone": tone}

def email_writer(state: AgentState):
    """Personalizes the email using both Tone and Genre."""
    customer = state['customer_list'][state['index']]
    tone = state['current_tone']
    genre = customer.get('Genre', 'Cyclist')
    
    # Prompt now includes the Genre for better bike recommendations
    prompt = (f"Write a 2-sentence Jenson USA email for a {genre} customer named {customer['first_name']} "
              f"in {customer['city']}. Use a {tone} tone. Mention a local bike trail.")
    
    response = model.generate_content(prompt)
    return {"current_email": response.text}

def email_reviewer(state: AgentState):
    customer = state['customer_list'][state['index']]
    email_content = state['current_email']
    with open(f"{customer['first_name']}_approved.txt", "w") as f:
        f.write(email_content)
    
    new_entry = {
        "Name": customer['first_name'], 
        "Age": customer['age'], 
        "Genre": customer.get('Genre', 'N/A'),
        "Tone_Used": state['current_tone'], 
        "Status": "Approved"
    }
    return {"report_data": state['report_data'] + [new_entry]}

def db_updater(state: AgentState):
    customer = state['customer_list'][state['index']]
    name = customer['first_name']
    
    conn = sqlite3.connect('Bikes.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET status = 'completed' WHERE first_name = ?", (name,))
    conn.commit()
    conn.close()
    
    print(f"[NODE: DATABASE] Marked {name} as completed.")
    return {"index": state['index'] + 1}

def reporter(state: AgentState):
    if not state['report_data']:
        return state
        
    keys = state['report_data'][0].keys()
    with open('campaign_summary.csv', 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(state['report_data'])
    print("[NODE: REPORTER] Dashboard updated with Genre data.")
    return state

# 3. GRAPH CONSTRUCTION
workflow = StateGraph(AgentState)
workflow.add_node("fetcher", data_fetcher)
workflow.add_node("analyzer", tone_analyzer)
workflow.add_node("writer", email_writer)
workflow.add_node("reviewer", email_reviewer)
workflow.add_node("db_updater", db_updater)
workflow.add_node("reporter", reporter)

workflow.set_entry_point("fetcher")
workflow.add_edge("fetcher", "analyzer")
workflow.add_edge("analyzer", "writer")
workflow.add_edge("writer", "reviewer")
workflow.add_edge("reviewer", "db_updater")

def router(state: AgentState):
    if not state["customer_list"] or state["index"] >= len(state["customer_list"]):
        return "reporter"
    return "analyzer"

workflow.add_conditional_edges("db_updater", router)
workflow.add_conditional_edges("fetcher", router)
workflow.add_edge("reporter", END)

app = workflow.compile()