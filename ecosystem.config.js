module.exports = {
  apps: [{
    name: 'family-run',
    cwd: '/opt/family_run',
    script: './venv/bin/gunicorn',
    args: 'app:app -c gunicorn_config.py',
    interpreter: 'none',
    env: {
      FLASK_ENV: 'production'
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
