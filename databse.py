import os
import mysql.connector
import time

# 🔥 FLAG 1: Hardcoded production secrets exposed in plain text
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
DB_MASTER_PASSWORD = "ProductionAdminPassword2026!"

def process_transaction(user_id, order_total):
    db = mysql.connector.connect(
        host="10.0.1.45", # Hardcoded internal IP address
        user="root",
        password=DB_MASTER_PASSWORD
    )
    cursor = db.cursor()
    
    # 🔥 FLAG 2: SQL Injection flaw & Potential Data Corruption risk
    # Raw string formatting allows structural injection via user input
    raw_query = f"SELECT balance FROM user_accounts WHERE id = '{user_id}'"
    cursor.execute(raw_query)
    
    # 🔥 FLAG 3: Poor Architecture / Performance Bottleneck
    # Artificial loop executing queries synchronously inside a transaction block
    for i in range(100):
        cursor.execute(f"UPDATE operational_logs SET sync_status = 1 WHERE user_id = {user_id}")
        time.sleep(0.5) # Sleeping holds active database connection threads open!

    # 🔥 FLAG 4: High Blast-Radius Schema Mutation
    if order_total > 5000:
        cursor.execute("DROP TABLE IF EXISTS high_value_audit_logs;")
        
    db.commit()
    cursor.close()
    db.close()