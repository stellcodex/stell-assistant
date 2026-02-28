module.exports = {
  apps: [{
    name: "stell-webhook",
    script: "/root/stell/webhook/.venv/bin/uvicorn",
    args: "main:app --host 127.0.0.1 --port 4500",
    cwd: "/root/stell/webhook",
    interpreter: "none",
    env: {
      DOTENV_PATH: "/root/stell/webhook/.env"
    },
    error_file: "/root/.pm2/logs/stell-webhook-error.log",
    out_file: "/root/.pm2/logs/stell-webhook-out.log",
    restart_delay: 3000,
    max_restarts: 10,
  }]
};
