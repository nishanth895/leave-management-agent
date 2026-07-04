# AI-Powered Leave Management Agent 📅

A production-ready, beautiful, and secure Leave Management System built with **Streamlit**, **SQLite**, and **Google Gemini AI**.

This application provides employees and administrators with a centralized platform to request, review, and analyze leaves. A smart AI agent evaluates request details in real-time, matching parameters like reasons and balances to make immediate recommendations for administrators.

---

## 🎨 Application Preview
Below is a high-fidelity visual preview of the dashboard:

![Leave Management Agent Dashboard Mockup](assets/dashboard_screenshot.jpg)

---

## 🚀 Key Features

### 👤 Employee Portal
- **Real-Time Leave Balances**: Instantly check available Casual, Sick, and Paid leave balances in premium glassmorphic widgets.
- **Overlapping Protection**: Date validations prevent duplicate applications and double-bookings.
- **Instant AI Feedback**: Submitting an application triggers an immediate preliminary recommendation from the AI agent.
- **Detailed History**: Chronological view of past applications with colored status badges.
- **Profile Password Update**: Secure password changes with current credential verification.

### 🛡️ Admin Dashboard
- **Intelligent Reviews**: Review pending applications side-by-side with remaining employee balances and AI assessments.
- **Audit Logging**: Logs every status update and balance modification to a secure system audit log.
- **Interactive Analytics**: Real-time charts of leave distributions and status percentages powered by Plotly.
- **Exporting Capabilities**: Download complete Excel/CSV data or generate print-ready PDF Executive Summaries with `fpdf2`.

---

## 🛠️ Tech Stack & Architecture

- **Frontend & Routing**: Streamlit
- **Data Visualization**: Plotly Express & Pandas
- **Database**: SQLite3
- **Security & Hashing**: Bcrypt
- **Document Generation**: FPDF2
- **Artificial Intelligence**: Google Generative AI (`gemini-2.5-flash` model)

---

## 📋 Database Schema

The database `leave_management.db` contains three tables:

- **`users`**: Manages credentials, roles (`admin`, `employee`), and remaining balances.
- **`leave_requests`**: Tracks duration dates, reasons, and AI feedback.
- **`audit_logs`**: Logs all admin decisions for security audit trails.

---

## 🏁 Getting Started

### Prerequisites
- Python 3.10 or 3.11
- (Optional) Google Gemini API Key

### Local Installation

1. **Clone the Repository** (or enter the directory):
   ```bash
   cd "Leave management Agent"
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables (Optional for AI)**:
   - For complete AI assessments, set your Gemini API key:
     ```bash
     # Windows (Command Prompt)
     set GEMINI_API_KEY="your-api-key"
     
     # Windows (PowerShell)
     $env:GEMINI_API_KEY="your-api-key"
     
     # Linux / MacOS
     export GEMINI_API_KEY="your-api-key"
     ```
   - *Note: If no API key is found, the system runs on a smart heuristic rule engine fallback.*

4. **Launch the Application**:
   ```bash
   streamlit run app.py
   ```

---

## 🔐 Default Credentials

The database initializes and seeds itself with three default accounts:

| Username | Password | Role | Name |
| :--- | :--- | :--- | :--- |
| **`admin`** | `admin123` | Administrator | System Administrator |
| **`alice`** | `password123` | Employee | Alice Smith |
| **`bob`** | `password123` | Employee | Bob Jones |

---

## 🐳 Docker Deployment

You can build and run this application inside an isolated Docker container:

1. **Build the Image**:
   ```bash
   docker build -t leave-agent .
   ```

2. **Run the Container**:
   ```bash
   docker run -p 8501:8501 --env GEMINI_API_KEY="your-api-key" leave-agent
   ```

3. Open your browser and navigate to `http://localhost:8501`.

---

## ☁️ Streamlit Community Cloud Deploy Ready

This project is fully structured for easy deployment on **Streamlit Community Cloud**:
1. Push this repository to GitHub (include `.github/`, `app.py`, `database.py`, `ai_agent.py`, `auth.py`, `employee.py`, `admin.py`, `requirements.txt`, and `Dockerfile`).
2. Link the repository on the Streamlit Cloud dashboard.
3. Add your Gemini API key in Streamlit **Secrets** under App Settings:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
