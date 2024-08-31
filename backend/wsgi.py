from flask_cors import CORS
from app import app

CORS(app, resources={r"/*": {"origins": "https://playlist-transfer-lovat.vercel.app"}}, supports_credentials=True)

if __name__ == "__main__":
    app.run(debug=True)