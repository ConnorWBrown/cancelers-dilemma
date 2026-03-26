import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cancelers_dilemma.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Event(db.Model):
    id = db.Column(db.String(12), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user1_choice = db.Column(db.String(20), nullable=True)  # 'cancel' or 'dont_cancel'
    user2_choice = db.Column(db.String(20), nullable=True)
    user1_submitted = db.Column(db.Boolean, default=False)
    user2_submitted = db.Column(db.Boolean, default=False)
    
    def get_result(self):
        """Determine the result based on both users' choices."""
        if not self.user1_submitted or not self.user2_submitted:
            return None
        
        if self.user1_choice == 'cancel' and self.user2_choice == 'cancel':
            return 'both_cancelled'
        else:
            return 'have_fun'
    
    def is_complete(self):
        """Check if both users have submitted their choices."""
        return self.user1_submitted and self.user2_submitted


def generate_event_id():
    """Generate a unique short ID for an event."""
    return secrets.token_urlsafe(9)


@app.route('/')
def index():
    """Home page - allows user to create or join an event."""
    return render_template('index.html')


@app.route('/create', methods=['POST'])
def create_event():
    """Create a new event and redirect to user 1's page."""
    event_id = generate_event_id()
    event = Event(id=event_id)
    db.session.add(event)
    db.session.commit()
    return redirect(url_for('event_page', event_id=event_id, user='1'))


@app.route('/event/<event_id>')
def event_page(event_id):
    """Display the event page where a user makes their choice."""
    event = db.session.get(Event, event_id)
    
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('index'))
    
    # Get user parameter from query string
    user = request.args.get('user', '1')
    if user not in ['1', '2']:
        user = '1'
    
    # Check if user has already submitted
    if user == '1' and event.user1_submitted:
        return redirect(url_for('waiting_page', event_id=event_id, user='1'))
    elif user == '2' and event.user2_submitted:
        return redirect(url_for('waiting_page', event_id=event_id, user='2'))
    
    return render_template('event.html', event_id=event_id, user=user)


@app.route('/event/<event_id>/submit', methods=['POST'])
def submit_choice(event_id):
    """Process user's choice submission."""
    event = db.session.get(Event, event_id)
    
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('index'))
    
    user = request.form.get('user')
    choice = request.form.get('choice')
    
    if choice not in ['cancel', 'dont_cancel']:
        flash('Invalid choice.', 'error')
        return redirect(url_for('event_page', event_id=event_id, user=user))
    
    if user == '1':
        event.user1_choice = choice
        event.user1_submitted = True
    elif user == '2':
        event.user2_choice = choice
        event.user2_submitted = True
    else:
        flash('Invalid user.', 'error')
        return redirect(url_for('event_page', event_id=event_id, user=user))
    
    db.session.commit()
    
    return redirect(url_for('waiting_page', event_id=event_id, user=user))


@app.route('/event/<event_id>/waiting')
def waiting_page(event_id):
    """Show waiting page until both users have submitted."""
    event = db.session.get(Event, event_id)
    
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('index'))
    
    user = request.args.get('user', '1')
    
    if event.is_complete():
        return redirect(url_for('result_page', event_id=event_id))
    
    # Generate the join URL for the other user
    join_url = request.host_url.rstrip('/') + url_for('event_page', event_id=event_id, user='2', _external=False)
    
    return render_template('waiting.html', event_id=event_id, user=user, join_url=join_url)


@app.route('/event/<event_id>/result')
def result_page(event_id):
    """Display the result of the game."""
    event = db.session.get(Event, event_id)
    
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('index'))
    
    if not event.is_complete():
        return redirect(url_for('waiting_page', event_id=event_id))
    
    result = event.get_result()
    
    return render_template('result.html', event_id=event_id, result=result)


@app.route('/event/<event_id>/status')
def event_status(event_id):
    """API endpoint to check if both users have submitted (for AJAX polling)."""
    event = db.session.get(Event, event_id)
    
    if not event:
        return {'error': 'Event not found'}, 404
    
    return {
        'user1_submitted': event.user1_submitted,
        'user2_submitted': event.user2_submitted,
        'complete': event.is_complete()
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=5000)
