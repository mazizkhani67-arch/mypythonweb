from app import create_app
import config


import os

app = create_app(config_class=config.Config)
# --- پیکربندی پایگاه داده ---
# برای SQLite:
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
