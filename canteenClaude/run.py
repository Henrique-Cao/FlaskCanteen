"""
run.py
~~~~~~
Development entry point.
 
    python run.py
    # or
    flask --app run:app run --debug
"""
import sass
import os
from app import create_app
 
app = create_app()
 
# ── Compile Sass on startup (development only) ───────────────────────────────
if app.debug:
    sass.compile(
        dirname=(
            os.path.join("app/static", "scss"),
            os.path.join("app/static", "css"),
        ),
        output_style="compressed",
    )
 
if __name__ == "__main__":
    app.run()
 