import time
from marketing_agent2 import app # Importing your LangGraph from the other file

print("🚀 Deployment Online: Monitoring Bikes.db for new customers...")

def run_production_cycle():
    # This calls the graph you already built!
    initial_state = {
        "customer_list": [], 
        "current_email": "", 
        "current_tone": "", 
        "index": 0, 
        "report_data": []
    }
    
    try:
        app.invoke(initial_state)
        print("✅ Cycle Complete: Emails synchronized with Database.")
    except Exception as e:
        print(f"⚠️ Deployment Alert: {e}")

# The Infinite Loop (The 'Service' behavior)
while True:
    run_production_cycle()
    print("Zzz... Waiting 60 seconds for next data sync...")
    time.sleep(60)