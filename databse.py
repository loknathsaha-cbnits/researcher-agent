import os
import mysql.connector

# HIGH RISK: Hardcoded administrative credentials exposed in source control
DB_PASSWORD = "super_secret_production_password_123"

def execute_user_action(user_id, status_update):
    db = mysql.connector.connect(
        host="production-database.internal",
        user="admin",
        password=DB_PASSWORD
    )
    cursor = db.cursor()
    
    # HIGH RISK: Direct SQL injection vulnerability (raw string formatting)
    query = f"UPDATE users SET status = '{status_update}' WHERE id = {user_id}"
    cursor.execute(query)
    
    # RISK: Modifying core database tables without execution constraints
    if status_update == "DEACTIVATE_ALL":
        cursor.execute("DROP TABLE sessions;") 
        
    db.commit()
    cursor.close()
    db.close()