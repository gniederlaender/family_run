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
# Method 1: Using the restart script (recommended)
./restart_app.sh

# Method 2: Using PM2 commands directly
pm2 start ecosystem.config.js --update-env
pm2 save
```

Note: Simply using `pm2 restart family-run` will NOT reload the configuration from ecosystem.config.js. You must use one of the methods above to ensure configuration changes are applied.

Current production settings:
- Timeout: 300 seconds (prevents worker timeout errors)
- Graceful timeout: 30 seconds
- Keep-alive: 5 seconds
- Log level: error (configured in gunicorn_config.py)
- Workers: 2
- Error filtering: Suppresses benign "Error handling request (no URI read)" messages during graceful shutdowns

### Troubleshooting PM2 Configuration Issues

If error logs show issues that should be filtered (like "Error handling request (no URI read)"), verify that PM2 is using the correct configuration:

```bash
# Check current PM2 configuration
pm2 describe family-run

# Look for "script args" - it should show: app:app -c gunicorn_config.py
# If it shows hardcoded args like --bind, --workers, etc., the config file is not being used

# To fix: restart with the ecosystem config file
pm2 restart ecosystem.config.js
pm2 save
```
