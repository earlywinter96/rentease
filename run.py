import os
import sys
from app import create_app, db
from flask_migrate import Migrate

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = create_app()
migrate = Migrate(app, db)  # Add this line to register migrations

from datetime import datetime

@app.context_processor
def inject_globals():
    return {'current_year': datetime.now().year}


if __name__ == "__main__":
    app.run(debug=True)
