import psutil
import time
from flask import Flask, render_template_string

app = Flask(__name__)

# Function to convert bytes to readable format (KB, MB, GB)
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

@app.route("/")
def index():
    # 1. CPU & Memory
    cpu_metric = psutil.cpu_percent(interval=1)
    mem_metric = psutil.virtual_memory().percent

    # 2. Disk Usage
    disk_metric = psutil.disk_usage('/').percent

    # 3. Network Traffic (Sent/Recv)
    net_io = psutil.net_io_counters()
    bytes_sent = get_size(net_io.bytes_sent)
    bytes_recv = get_size(net_io.bytes_recv)

    # 4. Status Message
    message = "System Healthy" if cpu_metric < 80 else "WARNING: High Load"
    color = "green" if cpu_metric < 80 else "red"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mission Control Dashboard</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e2e; color: white; text-align: center; padding: 20px; }}
            .container {{ max-width: 800px; margin: auto; }}
            h1 {{ margin-bottom: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
            .card {{ background: #2e2e42; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .metric-title {{ font-size: 1.2rem; color: #a6a6c3; margin-bottom: 10px; }}
            .metric-value {{ font-size: 2.5rem; font-weight: bold; color: #89b4fa; }}
            .status {{ margin-top: 30px; font-size: 1.5rem; color: {color}; font-weight: bold; padding: 10px; border: 2px solid {color}; border-radius: 8px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 DevOps Mission Control</h1>
            <p>Live Telemetry from AWS EC2 (US-EAST-1)</p>
            
            <div class="grid">
                <div class="card">
                    <div class="metric-title">CPU Load</div>
                    <div class="metric-value">{cpu_metric}%</div>
                </div>
                
                <div class="card">
                    <div class="metric-title">RAM Usage</div>
                    <div class="metric-value">{mem_metric}%</div>
                </div>

                <div class="card">
                    <div class="metric-title">Disk Space</div>
                    <div class="metric-value">{disk_metric}%</div>
                </div>

                <div class="card">
                    <div class="metric-title">Network Traffic</div>
                    <div class="metric-value" style="font-size: 1.5rem;">
                        ⬇ {bytes_recv} <br> ⬆ {bytes_sent}
                    </div>
                </div>
            </div>

            <div class="status">STATUS: {message}</div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)