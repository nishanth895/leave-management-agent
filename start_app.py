"""
Leave Management Agent - Auto Start Script
This script automatically starts the Streamlit app and opens it in the browser
"""
import subprocess
import time
import webbrowser
import sys

def start_leave_management_app():
    """Start the Leave Management Agent with auto browser open"""
    
    print("🚀 Starting Leave Management Agent...")
    print("=" * 60)
    
    # Start Streamlit in background
    try:
        # Start streamlit process
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", 
             "--server.headless=false",
             "--browser.gatherUsageStats=false"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("⏳ Waiting for server to start...")
        time.sleep(3)  # Wait for server to initialize
        
        # Open browser
        url = "http://localhost:8501"
        print(f"🌐 Opening browser at {url}")
        webbrowser.open(url)
        
        print("✅ Leave Management Agent is running!")
        print("=" * 60)
        print("📌 Access URL: http://localhost:8501")
        print("🔐 Admin Login: admin@example.com / admin123")
        print("👤 Employee Login: alice@example.com / password123")
        print("=" * 60)
        print("⚠️  Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Keep process running
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Leave Management Agent...")
        process.terminate()
        print("✅ Server stopped successfully!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    start_leave_management_app()
