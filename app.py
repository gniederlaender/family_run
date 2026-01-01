from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

DATA_FILE = 'data.json'
FAMILY_MEMBERS = ['Gabor', 'Petia', 'David']


def get_week_start(date):
    """Get the Monday of the week for a given date."""
    return date - timedelta(days=date.weekday())


def get_week_key(date):
    """Get ISO week format: YYYY-WW."""
    return date.strftime('%Y-W%W')


def get_current_week_key():
    """Get current week key."""
    return get_week_key(datetime.now())


def load_data():
    """Load data from JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_data(data):
    """Save data to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_week_display(week_key):
    """Convert week key to readable format."""
    year, week = week_key.split('-W')
    # Get the Monday of that week
    first_day = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w')
    last_day = first_day + timedelta(days=6)
    return f"{first_day.strftime('%b %d')} - {last_day.strftime('%b %d, %Y')}"


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', family_members=FAMILY_MEMBERS)


@app.route('/api/data')
def get_data():
    """Get all data."""
    data = load_data()
    current_week = get_current_week_key()

    # Calculate totals for each week
    processed_data = []
    all_weeks = sorted(data.keys(), reverse=True)

    for week in all_weeks:
        week_data = {
            'week': week,
            'week_display': get_week_display(week),
            'is_current': week == current_week,
            'members': {}
        }

        for member in FAMILY_MEMBERS:
            runs = data[week].get(member, [])
            total_km = sum(runs) if runs else 0
            week_data['members'][member] = {
                'runs': runs,
                'total_km': total_km,
                'has_run': total_km > 0
            }

        processed_data.append(week_data)

    return jsonify({
        'weeks': processed_data,
        'current_week': current_week,
        'current_week_display': get_week_display(current_week)
    })


@app.route('/api/add-run', methods=['POST'])
def add_run():
    """Add a run for a family member."""
    data = load_data()
    current_week = get_current_week_key()

    member = request.json.get('member')
    km = request.json.get('km')

    if member not in FAMILY_MEMBERS:
        return jsonify({'error': 'Invalid family member'}), 400

    try:
        km = float(km)
        if km <= 0:
            return jsonify({'error': 'Distance must be positive'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid distance'}), 400

    # Initialize week if it doesn't exist
    if current_week not in data:
        data[current_week] = {member: [] for member in FAMILY_MEMBERS}

    # Initialize member if they don't exist in this week
    if member not in data[current_week]:
        data[current_week][member] = []

    # Add the run
    data[current_week][member].append(km)

    save_data(data)

    return jsonify({'success': True, 'week': current_week})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
