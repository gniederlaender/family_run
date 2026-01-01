module.exports = {
  apps: [{
    name: 'family-run',
    cwd: '/opt/family_run',
    script: './venv/bin/gunicorn',
    args: 'app:app --bind 0.0.0.0:5002 --workers 2 --timeout 120',
    interpreter: 'none',
    env: {
      FLASK_ENV: 'production'
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
