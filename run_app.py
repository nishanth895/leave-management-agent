#!/usr/bin/env python3
"""
Leave Management Agent - Reliable Auto-Start Script
Opens browser automatically every time
"""
import subprocess
import time
import webbrowser
import sys
import os
from pathlib import Path

def check_server_ready(max_attempts=30):
    """Check if Streamlit server is ready"""
    import socket
    
    for i in range(max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 8501))
            sock.close()
            
            if result == 0:
                return True
            
            time.sleep(1)
            print(f"Waiting for server... ({i+1}/{max_attempts})", end='\r')
        except:
            time.sleep(1)
    
    return False

def open_browser_multiple_ways(url):
    """Try multiple methods to open browser"""
    
    # Method 1: Standard webbrowser module
    try:
        webbrowser.open(url)
        print("✓ Browser opened (method 1)")
    except:
        print("× Method 1 failed")
    
    time.sleep(1)
    
    # Method 2: Try specific browsers
    browsers = [
        'chrome',
        'firefox', 
        'microsoft-edge',
        'opera',
        'safari'
    ]
    
    for browser_name in browsers:
        try:
            browser = webbrowser.get(browser_name)
            browser.open(url)
            print(f"✓ Browser opened (method 2: {browser_name})")
            break
        except:
            continue
    
    # Method 3: Windows specific
    if sys.platform == 'win32':
        try:
            os.startfile(url)
            print("✓ Browser opened (method 3: Windows)")
        except:
            print("× Method 3 failed")

def main():
    print("\n" + "="*60)
    print("  LEAVE MANAGEMENT AGENT - HRMS DASHBOARD")
    print("="*60 + "\n")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🚀 Starting Streamlit server...")
    
    # Start Streamlit process
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py",
             "--server.port=8501",
             "--server.headless=true",
             "--browser.gatherUsageStats=false"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        print("⏳ Waiting for server to initialize...\n")
        
        # Wait for server to be ready
        if check_server_ready():
            print("\n" + "="*60)
            print("  ✅ SERVER READY!")
            print("="*60 + "\n")
            
            time.sleep(2)
            
            print("🌐 Opening browser at http://localhost:8501\n")
            
            # Try multiple methods to open browser
            open_browser_multiple_ways("http://localhost:8501")
            
            print("\n" + "="*60)
            print("📌 Access URL: http://localhost:8501")
            print("🔐 Admin: admin@example.com / admin123")
            print("👤 Employee: alice@example.com / password123")
            print("="*60)
            print("\n⚠️  Press Ctrl+C to stop the server\n")
            
            # Keep running
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping server...")
                process.terminate()
                time.sleep(1)
                print("✅ Server stopped!\n")
        else:
            print("\n❌ ERROR: Server failed to start!")
            print("Please check:")
            print("  1. Python and Streamlit are installed")
            print("  2. Port 8501 is not already in use")
            print("  3. All dependencies are installed\n")
            process.terminate()
            
    except FileNotFoundError:
        print("\n❌ ERROR: Streamlit not found!")
        print("Please install: pip install streamlit\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
