# Family Run Tracker

A simple, lightweight web application for tracking weekly running activities for Gabor, Petia, and David.

## Features

- Track weekly runs (multiple runs per week supported)
- Automatic km summation per week
- View current week progress
- Historical table showing all past weeks
- Simple, clean interface
- No authentication required
- JSON-based storage

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

- **Add a run**: Select your name, enter the distance in km, and click "Add Run"
- **Current week**: Shows this week's progress for all family members
- **History table**: Shows all weeks with green ticks (✓) and km for completed runs, or 0 for no runs
- **Week definition**: Weeks start on Monday
- **Editing**: Only the current week can be edited; past weeks are read-only

## Data Storage

Data is stored in `data.json` in the following format:
```json
{
  "2026-W01": {
    "Gabor": [5.0, 10.0],
    "Petia": [7.0],
    "David": []
  }
}
```

Each week uses ISO format (YYYY-WW), and each family member has an array of run distances in km.

## Production Deployment

The application is deployed using PM2 and Gunicorn. Configuration is in `ecosystem.config.js`.

To apply configuration changes:
```bash
pm2 delete family-run
pm2 start ecosystem.config.js
pm2 save
```

Current production settings:
- Timeout: 300 seconds (prevents worker timeout errors)
- Graceful timeout: 30 seconds
- Keep-alive: 5 seconds
- Log level: warning (reduces noise from invalid bot requests)
- Workers: 2
