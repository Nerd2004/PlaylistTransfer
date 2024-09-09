from flask_cors import CORS
from app import app
from dotenv import load_dotenv
load_dotenv()



CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

if __name__ == "__main__":
    app.run(debug=True)