# Secure Voting System for Students

## 📄 Abstract
A secure, web-based voting application designed for colleges (specifically RVCE) to facilitate student elections. The system ensures anonymity, prevents duplicate voting, and uses email-based OTP authentication to verify student identity without requiring pre-registration of passwords. This project demonstrates the implementation of secure web practices and anonymous voting protocols.

## 🚀 Key Features
- **Secure Authentication**: Uses Email OTP (One-Time Password) for login to ensure only valid students can access the system.
- **Domain Restriction**: Strictly restricts access to institutional email addresses (`@rvce.edu.in`).
- **Complete Anonymity**: The system uses a split-token architecture to separate user identity from their vote.
- **Double-Vote Prevention**: Enforces a strict "One Student, One Vote" policy per election.
- **Admin Dashboard**: A comprehensive panel for administrators to:
    - Manage Elections (Create, Activate, Deactivate, Delete)
    - Manage Candidates and Students
    - View Real-time Election Results
- **Responsive Interface**: User-friendly design accessible on desktop and mobile.

## 🛠️ Technology Stack
- **Backend Framework**: Python, Flask
- **Database**: SQLite (Development), SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Jinja2 Templating
- **Authentication**: Flask-Login, Session Management
- **Email Service**: SMTP (Support for Gmail/Outlook)

## 📊 Database Schema (System Design)
The system is built on a relational database with the following key models:

1.  **Student**: Stores student identity (Name, Email, ID).
2.  **Election**: Stores election details (Title, Description, Active Status).
3.  **Candidate**: Entities running for an election. Linking to `Election`.
4.  **OTPCode**: Temporary storage for validation codes with expiry time.
5.  **VoteToken**: A relational link between `Student` and `Election`.
    -   *Purpose*: Records **THAT** a student has voted to prevent double voting.
    -   *Privacy*: Does **NOT** record **WHO** they voted for.
6.  **Vote**: Stores the actual ballot choice.
    -   *Privacy*: Linked to `Election` and `Candidate` but **NOT** to `Student`. Verification is done via a token hash.

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher installed.

### Steps
1.  **Clone/Download the Repository**
    Extract the project files to a local directory.

2.  **Install Dependencies**
    Open a terminal in the project folder and run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Database Initialization**
    Run the setup script to create the database file (`voting.db`):
    ```bash
    python init_db.py
    ```

4.  **Configuration (Optional)**
    - The system comes with a default configuration in `config.py`.
    - To enable real email sending, update the `SMTP_` variables in `config.py` with your credentials.
    - *Note: If email sending fails (e.g., no internet/bad creds), the OTP is printed to the server console for debugging.*

5.  **Run the Application**
    Start the local development server:
    ```bash
    python app.py
    ```
    The application will be accessible at: **http://127.0.0.1:5000**

## 📖 Usage Guide

### 🧑‍🎓 For Students
1.  Navigate to the home page.
2.  Enter your college email (`@rvce.edu.in`).
3.  Check your email inbox (or the command prompt/terminal if in dev mode) for the 6-digit OTP.
4.  Enter the OTP to verify your identity.
5.  On the dashboard, you will see active elections.
6.  Select an election, choose a candidate, and click "Cast Vote".

### 👨‍💼 For Administrators
*Admin access is restricted to specific email addresses (e.g., `shaikmaaz77zz@gmail.com`).*

1.  Log in using an authorized admin email.
2.  You will be redirected to the **Admin Dashboard**.
3.  **Manage Elections**: Create new elections or toggle their status to "Active" (allow voting) or "Inactive" (close voting).
4.  **Manage Candidates**: Add candidates to specific elections.
5.  **View Results**: See the current vote count for all candidates.

## 🔒 Security Implementation
- **Anonymity Architecture**: The system decouples the "Right to Vote" from the "Vote Cast". Even a database administrator cannot query the database to see which candidate a specific student voted for.
- **Session Security**: Uses signed session cookies to prevent tampering.
- **Input Validation**: Server-side validation for all inputs to prevent injection attacks.

---
*Project developed for Educational Purpose*
