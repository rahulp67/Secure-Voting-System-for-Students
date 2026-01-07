from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets

db = SQLAlchemy()

class Student(UserMixin, db.Model):
    """Student model for authentication."""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    vote_tokens = db.relationship('VoteToken', backref='student', lazy=True)
    otp_codes = db.relationship('OTPCode', backref='student', lazy=True)
    
    def __repr__(self):
        return f'<Student {self.student_id}>'


class OTPCode(db.Model):
    """OTP codes for email verification."""
    __tablename__ = 'otp_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    @staticmethod
    def generate_otp(student_id, expiry_minutes=5):
        """Generate a new 6-digit OTP for a student."""
        # Invalidate any existing unused OTPs for this student
        OTPCode.query.filter_by(student_id=student_id, is_used=False).delete()
        
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        otp = OTPCode(
            student_id=student_id,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes)
        )
        db.session.add(otp)
        db.session.commit()
        return code
    
    @staticmethod
    def verify_otp(student_id, code):
        """Verify an OTP code for a student."""
        otp = OTPCode.query.filter_by(
            student_id=student_id,
            code=code,
            is_used=False
        ).first()
        
        if not otp:
            return False, "Invalid OTP code."
        
        if datetime.utcnow() > otp.expires_at:
            return False, "OTP has expired. Please request a new one."
        
        # Mark as used
        otp.is_used = True
        db.session.commit()
        return True, "OTP verified successfully."


class Election(db.Model):
    """Election model."""
    __tablename__ = 'elections'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    candidates = db.relationship('Candidate', backref='election', lazy=True)
    vote_tokens = db.relationship('VoteToken', backref='election', lazy=True)
    votes = db.relationship('Vote', backref='election', lazy=True)
    
    def __repr__(self):
        return f'<Election {self.title}>'


class Candidate(db.Model):
    """Candidate model."""
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationship to votes
    votes = db.relationship('Vote', backref='candidate', lazy=True)
    
    def __repr__(self):
        return f'<Candidate {self.name}>'


class VoteToken(db.Model):
    """
    Vote token model - links student to election (for double-vote prevention).
    IMPORTANT: This table tracks WHO has voted, but the actual vote (candidate choice)
    is stored separately in the votes table using only the token, ensuring anonymity.
    """
    __tablename__ = 'vote_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a student can only have one token per election
    __table_args__ = (
        db.UniqueConstraint('student_id', 'election_id', name='unique_student_election'),
    )
    
    def __repr__(self):
        return f'<VoteToken {self.token[:8]}...>'


class Vote(db.Model):
    """
    Vote model - stores ANONYMOUS votes.
    IMPORTANT: This table intentionally does NOT have a student_id field.
    Votes are linked only by token, and the token-to-student mapping is
    one-way (you can check if a student voted, but can't see how they voted).
    """
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Vote for candidate {self.candidate_id}>'
