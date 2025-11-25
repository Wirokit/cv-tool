# Initial file by Gemini
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory, session
from werkzeug.utils import secure_filename
from google import genai
""" from dotenv import load_dotenv """
from cv_generator import generate_professional_cv

# --- Environment ---
""" load_dotenv() """

# Create a Flask application
application = Flask(__name__)

# Define upload and processed directories
# os.path.dirname(__file__) gets the directory this script is in
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed_files")

# Ensure these directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Application config
application.config.from_mapping(
    SECRET_KEY = os.environ['SECRET_FLASK_KEY'],
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024, # Set a max file size (e.g., 50MB)
)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {"pdf"}

# Create a Gemini client
geminicli = genai.Client()
prompt = open("prompt.txt", "r").read()


def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --- New Route to Serve the Frontend ---


@application.route("/")
def serve_html():
    """Serves the html files for the frontend."""
    """html files are assumed to be in the same directory as application.py (BASE_DIR)"""

    html_path = ""
    html_file = ""

    user_id = session.get('user_id')
    if not user_id:
        html_path = os.path.join(BASE_DIR, "login.html")
        html_file = "login.html"
    else:
        html_path = os.path.join(BASE_DIR, "upload_page.html")
        html_file = "upload_page.html"

    # Check if html exists
    if not os.path.exists(html_path):
        return "Frontend ({html_file}) not found.", 404

    # Send the html file
    return send_from_directory(BASE_DIR, html_file)


# --- Endpoint 1: File Upload and Processing ---


@application.route("/upload", methods=["POST"])
def upload_file():
    """
    Handles file upload, processing, and returns a link to the new file.
    """

    # Ensure user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "Access forbidden."}), 403

    # 1. Check if a file was sent
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in the request."}), 400

    file = request.files["file"]
    contact = request.values["contact"]

    # 2. Check if the user selected a file
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400

    # 3. Check if the file is an allowed type (PDF)
    if not allowed_file(file.filename):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "File type not allowed. Please upload a PDF.",
                }
            ),
            400,
        )

    if file:
        # 4. Secure the filename (prevents directory traversal attacks)
        original_filename = secure_filename(file.filename)

        # 5. Save the original file
        original_filepath = os.path.join(UPLOAD_FOLDER, original_filename)
        file.save(original_filepath)

        # 6. Generate a unique ID for the processed file
        file_id = str(uuid.uuid4())
        processed_filename = f"{file_id}.html"
        processed_filepath = os.path.join(PROCESSED_FOLDER, processed_filename)

        # 7. --- PDF PROCESSING LOGIC ---
        try:
            pdf_to_process = geminicli.files.upload(file=original_filepath)
            response = geminicli.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, pdf_to_process],
                config={
                    "response_mime_type": "application/json",
                },
            )

            result_json = response.text

            generate_professional_cv(result_json, processed_filepath, contact_name=contact)

            # --- End of PDF processing logic ---

        except FileNotFoundError:
            # The command (e.g., 'pdftk' or 'cp') wasn't found on the server
            print("Error: A command-line tool was not found.")
            return (
                jsonify({"success": False, "error": "Server configuration error."}),
                500,
            )
        except Exception as e:
            # Catch other potential errors
            print(f"An unexpected error occurred: {e}")
            return (
                jsonify(
                    {"success": False, "error": "An unexpected server error occurred."}
                ),
                500,
            )

        # 8. Build the URL for the new file
        # This URL points to our '/view/' endpoint below
        new_url = f"/view/{file_id}"

        # 9. Send the success response
        return jsonify({"success": True, "url": new_url})


# --- Endpoint 2: Serve the Processed File ---


@application.route("/view/<file_id>", methods=["GET"])
def view_file(file_id):
    """
    Serves the processed file to the user.
    """
    try:
        # Securely build the filename
        filename = f"{secure_filename(file_id)}.html"

        # Check if the file exists
        filepath = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(filepath):
            return "File not found.", 404

        # Send the file from the 'processed_files' directory
        return send_from_directory(
            PROCESSED_FOLDER,
            filename,
            as_attachment=False,  # Set to True to force download
        )
    except Exception as e:
        print(f"Error serving file: {e}")
        return "An error occurred.", 500
    

# --- Endpoint 3: Login ---


@application.route("/login", methods=["POST"])
def check_login():
    # Ensure that data was sent
    if not request.values["password"]:
        return jsonify({"success": False, "error": "Empty body."}), 400
    
    # Check that password matches
    password_correct = request.values["password"] == os.environ['SECRET_PASSWORD']

    if password_correct:
        session['user_id'] = "super"
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


# --- Run the Application ---

if __name__ == "__main__":
    # Run the app.
    # 'debug=True' is great for development as it auto-reloads.
    # For production, use a real web server like Gunicorn or Waitress.
    application.run(debug=True, host="0.0.0.0")
