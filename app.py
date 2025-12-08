import psutil
import psycopg2
import os
from flask import Flask

app = Flask(__name__)

# Database Config (These come from the GitHub Secrets -> Docker Env Vars)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = "jasondevopsdb"
DB_USER = "jasonadmin"
DB_PASS = "Password123!"

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

# Initialize DB Table (Run once on startup)
def init_db():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS visits (id SERIAL PRIMARY KEY, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);')
            conn.commit()
            cur.close()
            conn.close()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Init Error: {e}")

# Run init immediately
init_db()

@app.route("/")
def index():
    # 1. System Metrics
    cpu_metric = psutil.cpu_percent(interval=1)
    mem_metric = psutil.virtual_memory().percent

    # 2. Database Operations
    visit_count = 0
    db_status = "Waiting..."

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Insert new visit
            cur.execute('INSERT INTO visits DEFAULT VALUES;')
            conn.commit()
            # Get total count
            cur.execute('SELECT COUNT(*) FROM visits;')
            visit_count = cur.fetchone()[0]
            cur.close()
            conn.close()
            db_status = "Connected to RDS Postgres"
        except Exception as e:
            db_status = f"Query Error: {e}"
    else:
        db_status = "Connection Failed (Check Secrets)"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>3-Tier DevOps Architecture</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: sans-serif; background-color: #1e1e2e; color: white; text-align: center; padding: 50px; }}
            .container {{ max-width: 800px; margin: auto; }}
            .card {{ background: #2e2e42; padding: 20px; border-radius: 12px; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .metric {{ font-size: 2.5rem; font-weight: bold; color: #89b4fa; }}
            .db-status {{ margin-top: 10px; font-size: 0.9rem; color: #a6e3a1; }}
            .error {{ color: #f38ba8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 3-Tier DevOps Architecture</h1>
            <p>Client -> Server (EC2) -> Database (RDS)</p>
            
            <div class="card">
                <h3>Infrastructure Health</h3>
                <p>CPU: {cpu_metric}% | RAM: {mem_metric}%</p>
            </div>

            <div class="card">
                <h3>Persistent Visitor Log</h3>
                <p>Total Visits Saved to DB:</p>
                <div class="metric">{visit_count}</div>
                <div class="db-status { 'error' if 'Error' in db_status or 'Failed' in db_status else '' }">
                    {db_status}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)