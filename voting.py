import secrets
from models import db, VoteToken, Vote, Election, Candidate
from sqlalchemy import func


def generate_anonymous_token() -> str:
    """Generate a cryptographically secure random token for anonymous voting."""
    return secrets.token_hex(32)  # 64 character hex string


def has_voted(student_id: int, election_id: int) -> bool:
    """Check if a student has already voted in an election."""
    token = VoteToken.query.filter_by(
        student_id=student_id,
        election_id=election_id
    ).first()
    return token is not None


def cast_vote(student_id: int, election_id: int, candidate_id: int) -> tuple[bool, str]:
    """
    Cast a vote for a candidate in an election.
    
    This function implements the anonymity mechanism:
    1. Check if student already voted (using vote_tokens table)
    2. Generate a random token
    3. Store token in vote_tokens (links student to election - for double-vote prevention)
    4. Store vote in votes table (uses ONLY token - ensures anonymity)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Check if student already voted
    if has_voted(student_id, election_id):
        return False, "You have already voted in this election."
    
    # Verify election exists and is active
    election = Election.query.get(election_id)
    if not election:
        return False, "Election not found."
    if not election.is_active:
        return False, "This election is not active."
    
    # Verify candidate belongs to this election
    candidate = Candidate.query.get(candidate_id)
    if not candidate or candidate.election_id != election_id:
        return False, "Invalid candidate for this election."
    
    try:
        # Generate anonymous token
        token = generate_anonymous_token()
        
        # Create vote token (links student to election, NOT to the vote)
        vote_token = VoteToken(
            student_id=student_id,
            election_id=election_id,
            token=token
        )
        db.session.add(vote_token)
        
        # Create anonymous vote (uses ONLY token, no student reference)
        vote = Vote(
            token=token,
            election_id=election_id,
            candidate_id=candidate_id
        )
        db.session.add(vote)
        
        db.session.commit()
        return True, "Your vote has been cast successfully!"
        
    except Exception as e:
        db.session.rollback()
        return False, f"An error occurred while casting your vote. Please try again."


def get_election_results(election_id: int) -> dict:
    """
    Get aggregated results for an election.
    
    Returns vote counts per candidate WITHOUT any voter information.
    """
    election = Election.query.get(election_id)
    if not election:
        return None
    
    # Get vote counts per candidate
    results = db.session.query(
        Candidate.id,
        Candidate.name,
        Candidate.description,
        func.count(Vote.id).label('vote_count')
    ).outerjoin(
        Vote, Candidate.id == Vote.candidate_id
    ).filter(
        Candidate.election_id == election_id
    ).group_by(
        Candidate.id
    ).all()
    
    total_votes = sum(r.vote_count for r in results)
    
    return {
        'election': {
            'id': election.id,
            'title': election.title,
            'description': election.description,
            'is_active': election.is_active
        },
        'candidates': [
            {
                'id': r.id,
                'name': r.name,
                'description': r.description,
                'vote_count': r.vote_count,
                'percentage': round((r.vote_count / total_votes * 100), 1) if total_votes > 0 else 0
            }
            for r in results
        ],
        'total_votes': total_votes
    }


def get_all_election_results() -> list:
    """Get results for all elections."""
    elections = Election.query.all()
    return [get_election_results(e.id) for e in elections]
