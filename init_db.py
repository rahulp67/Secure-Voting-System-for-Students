"""
Database initialization script.
Run this script to create the database and seed it with sample data.

Usage:
    python init_db.py
"""

from app import app
from models import db, Student, Election, Candidate


def init_database():
    """Initialize the database with tables and sample data."""
    
    with app.app_context():
        # Drop all tables and recreate (for fresh start with new schema)
        db.drop_all()
        db.create_all()
        print("✓ Database tables created")
        
        # ==================== CREATE SAMPLE STUDENTS ====================
        # Using @rvce.edu.in emails (RV College of Engineering)
        students = [
            Student(
                student_id="1RV21CS001",
                email="rahul.sharma@rvce.edu.in",
                name="Rahul Sharma",
                is_admin=False
            ),
            Student(
                student_id="1RV21CS002",
                email="priya.patel@rvce.edu.in",
                name="Priya Patel",
                is_admin=False
            ),
            Student(
                student_id="1RV21CS003",
                email="amit.kumar@rvce.edu.in",
                name="Amit Kumar",
                is_admin=False
            ),
            Student(
                student_id="1RV21CS004",
                email="sneha.gupta@rvce.edu.in",
                name="Sneha Gupta",
                is_admin=False
            ),
            Student(
                student_id="1RV21CS005",
                email="vikram.singh@rvce.edu.in",
                name="Vikram Singh",
                is_admin=False
            ),
            # Admin user - CHANGE THIS TO YOUR REAL RVCE EMAIL!
            Student(
                student_id="ADMIN001",
                email="admin@rvce.edu.in",
                name="Admin User",
                is_admin=True
            ),
        ]
        
        for student in students:
            db.session.add(student)
        
        print("✓ Sample students created")
        
        # ==================== CREATE SAMPLE ELECTIONS ====================
        
        # Election 1: Student Body President
        election1 = Election(
            title="Student Body President 2026",
            description="Vote for your next Student Body President who will represent the RVCE student community.",
            is_active=True
        )
        db.session.add(election1)
        db.session.flush()
        
        candidates1 = [
            Candidate(
                election_id=election1.id,
                name="Arjun Mehta",
                description="Focused on improving campus facilities and student welfare programs."
            ),
            Candidate(
                election_id=election1.id,
                name="Kavya Reddy",
                description="Committed to enhancing academic resources and career opportunities."
            ),
            Candidate(
                election_id=election1.id,
                name="Rohan Joshi",
                description="Dedicated to promoting cultural activities and student mental health."
            ),
        ]
        
        for candidate in candidates1:
            db.session.add(candidate)
        
        # Election 2: Technical Club Secretary
        election2 = Election(
            title="IEEE RVCE Chapter Lead",
            description="Choose the next leader of IEEE RVCE to organize technical workshops and hackathons.",
            is_active=True
        )
        db.session.add(election2)
        db.session.flush()
        
        candidates2 = [
            Candidate(
                election_id=election2.id,
                name="Neha Verma",
                description="Plans to organize monthly coding competitions and industry talks."
            ),
            Candidate(
                election_id=election2.id,
                name="Siddharth Nair",
                description="Aims to establish partnerships with tech companies for internships."
            ),
        ]
        
        for candidate in candidates2:
            db.session.add(candidate)
        
        # Election 3: Sports Captain
        election3 = Election(
            title="RVCE Sports Captain",
            description="Elect the Sports Captain who will lead RVCE sports teams in inter-college events.",
            is_active=True
        )
        db.session.add(election3)
        db.session.flush()
        
        candidates3 = [
            Candidate(
                election_id=election3.id,
                name="Aditya Kulkarni",
                description="Former state-level cricket player with leadership experience."
            ),
            Candidate(
                election_id=election3.id,
                name="Meera Iyer",
                description="National-level basketball player committed to inclusive sports."
            ),
        ]
        
        for candidate in candidates3:
            db.session.add(candidate)
        
        # Commit all changes
        db.session.commit()
        print("✓ Sample elections and candidates created")
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZED SUCCESSFULLY!")
        print("="*60)
        print("\n⚠️  IMPORTANT: Configure SMTP in config.py before testing!")
        print("-" * 60)
        print("For Gmail SMTP:")
        print("  SMTP_SERVER = 'smtp.gmail.com'")
        print("  SMTP_USER = 'your-email@gmail.com'")
        print("  SMTP_PASSWORD = 'your-app-password'")
        print("-" * 60)
        print("\nTest Emails (@rvce.edu.in):")
        print("-" * 60)
        print("Students:")
        print("  rahul.sharma@rvce.edu.in")
        print("  priya.patel@rvce.edu.in")
        print("  amit.kumar@rvce.edu.in")
        print("  sneha.gupta@rvce.edu.in")
        print("  vikram.singh@rvce.edu.in")
        print("\nAdmin:")
        print("  admin@rvce.edu.in")
        print("-" * 60)
        print("\n🔐 No passwords needed - login uses email OTP!")
        print("="*60)


if __name__ == '__main__':
    init_database()
