from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, Student, Election, Candidate, VoteToken, Vote, OTPCode
from auth import admin_required
from voting import cast_vote, has_voted, get_election_results, get_all_election_results
from email_service import send_otp_email

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'error'


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    return Student.query.get(int(user_id))


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Home page - redirect to login or vote."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin'))
        return redirect(url_for('vote'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Email-based login - Step 1: Enter email."""
    if current_user.is_authenticated:
        return redirect(url_for('vote'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('login.html')
        
        # Validate email domain - only @rvce.edu.in allowed
        # Validate email domain - only @rvce.edu.in allowed (whitelist admin gmail)
        if not email.endswith('@rvce.edu.in') and email != 'shaikmaaz77zz@gmail.com':
            flash('Only @rvce.edu.in email addresses are allowed.', 'error')
            return render_template('login.html')
        
        # Find student by email
        student = Student.query.filter_by(email=email).first()
        
        if not student:
            # Auto-register new student
            name_part = email.split('@')[0]
            try:
                # Special case for the developer/admin
                is_admin_user = (email == 'shaikmaaz77zz@gmail.com')
                
                new_student = Student(
                    student_id=name_part.upper()[:20],
                    email=email,
                    name=name_part.replace('.', ' ').title(),
                    is_admin=is_admin_user
                )
                db.session.add(new_student)
                db.session.commit()
                student = new_student
                flash('Account created successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                # Handle potential duplicate ID collision
                import random
                random_suffix = str(random.randint(100, 999))
                new_student.student_id = (name_part.upper())[:16] + random_suffix
                db.session.add(new_student)
                db.session.commit()
                student = new_student
        
        # If user is the specific gmail, ensure they are admin (in case created earlier)
        if email == 'shaikmaaz77zz@gmail.com' and not student.is_admin:
            student.is_admin = True
            db.session.commit()

        # Generate and send OTP
        otp_code = OTPCode.generate_otp(student.id)
        
        # DEBUG: Print OTP to console for testing without email access
        print(f"\n{'='*30}\n🔐 DEBUG OTP for {email}: {otp_code}\n{'='*30}\n")
        success, message = send_otp_email(student.email, otp_code, student.name)
        
        if success:
            # Store student ID in session for OTP verification
            session['pending_student_id'] = student.id
            session['pending_email'] = email
            flash(f'OTP sent to {email}. Check your inbox!', 'success')
            return redirect(url_for('verify_otp'))
        else:
            flash(f'Failed to send OTP: {message}', 'error')
    
    return render_template('login.html')


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """OTP verification - Step 2: Enter OTP."""
    if current_user.is_authenticated:
        return redirect(url_for('vote'))
    
    # Check if we have a pending login
    student_id = session.get('pending_student_id')
    email = session.get('pending_email')
    
    if not student_id:
        flash('Please enter your email first.', 'error')
        return redirect(url_for('login'))
    
    student = Student.query.get(student_id)
    if not student:
        session.pop('pending_student_id', None)
        session.pop('pending_email', None)
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp', '').strip()
        
        if not otp_code or len(otp_code) != 6:
            flash('Please enter the 6-digit OTP.', 'error')
            return render_template('verify_otp.html', email=email)
        
        # Verify OTP
        success, message = OTPCode.verify_otp(student_id, otp_code)
        
        if success:
            # Clear session data
            session.pop('pending_student_id', None)
            session.pop('pending_email', None)
            
            # Log in the user
            login_user(student)
            flash(f'Welcome, {student.name}!', 'success')
            
            if student.is_admin:
                return redirect(url_for('admin'))
            return redirect(url_for('vote'))
        else:
            flash(message, 'error')
    
    return render_template('verify_otp.html', email=email)


@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP code."""
    student_id = session.get('pending_student_id')
    
    if not student_id:
        return redirect(url_for('login'))
    
    student = Student.query.get(student_id)
    if not student:
        return redirect(url_for('login'))
    
    # Generate and send new OTP
    otp_code = OTPCode.generate_otp(student.id)
    success, message = send_otp_email(student.email, otp_code, student.name)
    
    if success:
        flash('New OTP sent! Check your inbox.', 'success')
    else:
        flash(f'Failed to send OTP: {message}', 'error')
    
    return redirect(url_for('verify_otp'))


@app.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ==================== VOTING ROUTES ====================

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    """Voting page for students."""
    # Get active elections
    elections = Election.query.filter_by(is_active=True).all()
    
    # Check which elections the user has already voted in
    voted_elections = set()
    for election in elections:
        if has_voted(current_user.id, election.id):
            voted_elections.add(election.id)
    
    if request.method == 'POST':
        election_id = request.form.get('election_id', type=int)
        candidate_id = request.form.get('candidate_id', type=int)
        
        if not election_id or not candidate_id:
            flash('Please select a candidate.', 'error')
            return redirect(url_for('vote'))
        
        # Cast vote
        success, message = cast_vote(current_user.id, election_id, candidate_id)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        
        return redirect(url_for('vote'))
    
    return render_template('vote.html', 
                         elections=elections, 
                         voted_elections=voted_elections,
                         user=current_user)


# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@login_required
@admin_required
def admin():
    """Admin dashboard - view election results."""
    results = get_all_election_results()
    students = Student.query.all()
    elections = Election.query.all()
    return render_template('admin.html', results=results, students=students, 
                          elections=elections, user=current_user)


@app.route('/admin/students/add', methods=['POST'])
@login_required
@admin_required
def add_student():
    """Add a new student."""
    student_id = request.form.get('student_id', '').strip()
    email = request.form.get('email', '').strip().lower()
    name = request.form.get('name', '').strip()
    is_admin = request.form.get('is_admin') == 'on'
    
    if not student_id or not name or not email:
        flash('All fields are required.', 'error')
        return redirect(url_for('admin'))
    
    # Check if student ID or email already exists
    if Student.query.filter_by(student_id=student_id).first():
        flash(f'Student ID {student_id} already exists.', 'error')
        return redirect(url_for('admin'))
    
    if Student.query.filter_by(email=email).first():
        flash(f'Email {email} already registered.', 'error')
        return redirect(url_for('admin'))
    
    try:
        student = Student(
            student_id=student_id,
            email=email,
            name=name,
            is_admin=is_admin
        )
        db.session.add(student)
        db.session.commit()
        flash(f'Student {name} added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding student.', 'error')
    
    return redirect(url_for('admin'))


@app.route('/admin/students/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(id):
    """Delete a student."""
    student = Student.query.get_or_404(id)
    
    # Prevent deleting yourself
    if student.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin'))
    
    try:
        # Delete related data
        OTPCode.query.filter_by(student_id=id).delete()
        VoteToken.query.filter_by(student_id=id).delete()
        db.session.delete(student)
        db.session.commit()
        flash(f'Student {student.name} deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting student.', 'error')
    
    return redirect(url_for('admin'))


@app.route('/admin/elections/add', methods=['POST'])
@login_required
@admin_required
def add_election():
    """Add a new election."""
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('Election title is required.', 'error')
        return redirect(url_for('admin'))
    
    try:
        election = Election(title=title, description=description, is_active=True)
        db.session.add(election)
        db.session.commit()
        flash(f'Election "{title}" created!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error creating election.', 'error')
    
    return redirect(url_for('admin'))


@app.route('/admin/elections/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_election(id):
    """Toggle election active status."""
    election = Election.query.get_or_404(id)
    
    try:
        election.is_active = not election.is_active
        db.session.commit()
        status = 'activated' if election.is_active else 'deactivated'
        flash(f'Election "{election.title}" {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating election.', 'error')
    
    return redirect(url_for('admin'))


@app.route('/admin/elections/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_election(id):
    """Delete an election and its data."""
    election = Election.query.get_or_404(id)
    
    try:
        Vote.query.filter_by(election_id=id).delete()
        VoteToken.query.filter_by(election_id=id).delete()
        Candidate.query.filter_by(election_id=id).delete()
        db.session.delete(election)
        db.session.commit()
        flash(f'Election "{election.title}" deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting election.', 'error')
    
    return redirect(url_for('admin'))


@app.route('/admin/candidates/add', methods=['POST'])
@login_required
@admin_required
def add_candidate():
    """Add a candidate to an election."""
    election_id = request.form.get('election_id', type=int)
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not election_id or not name:
        flash('Election and candidate name are required.', 'error')
        return redirect(url_for('admin'))
    
    election = Election.query.get_or_404(election_id)
    
    try:
        candidate = Candidate(election_id=election_id, name=name, description=description)
        db.session.add(candidate)
        db.session.commit()
        flash(f'Candidate "{name}" added to {election.title}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding candidate.', 'error')
    
    return redirect(url_for('admin'))


@app.route('/admin/candidates/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_candidate(id):
    """Delete a candidate."""
    candidate = Candidate.query.get_or_404(id)
    
    try:
        Vote.query.filter_by(candidate_id=id).delete()
        db.session.delete(candidate)
        db.session.commit()
        flash(f'Candidate "{candidate.name}" deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting candidate.', 'error')
    
    return redirect(url_for('admin'))


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('login.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('login.html'), 500


# ==================== RUN APP ====================

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
