from app import create_app
import config

# ایجاد اپلیکیشن با استفاده از کلاس Config از فایل config.py
app = create_app(config_class=config.Config)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000) 