import os
import uuid
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# --- Configuration ---

# 1. Create a Flask application
app = Flask(__name__)

# 2. Define upload and processed directories
# os.path.dirname(__file__) gets the directory this script is in
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed_files")

# 3. Ensure these directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# 4. (Optional) Set a max file size (e.g., 50MB)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

# 5. Define allowed file extensions
ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --- New Route to Serve the Frontend ---


@app.route("/")
def serve_index():
    """Serves the index.html file for the frontend."""
    # index.html is assumed to be in the same directory as app.py (BASE_DIR)
    index_path = os.path.join(BASE_DIR, "index.html")

    # Check if index.html exists
    if not os.path.exists(index_path):
        return "Frontend (index.html) not found.", 404

    # Send the index.html file
    return send_from_directory(BASE_DIR, "index.html")


# --- Endpoint 1: File Upload and Processing ---


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Handles file upload, processing, and returns a link to the new file.
    """

    # 1. Check if a file was sent
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in the request."}), 400

    file = request.files["file"]

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
        processed_filename = f"{file_id}.pdf"
        processed_filepath = os.path.join(PROCESSED_FOLDER, processed_filename)

        # 7. --- !!! YOUR PDF PROCESSING LOGIC GOES HERE !!! ---
        # This is where you call your command-line tool or Python script.
        try:
            # Example using a command-line tool like 'pdftk'
            # This command is just a placeholder. Replace it with your actual command.
            # For example, to stamp a watermark:
            # ['pdftk', original_filepath, 'stamp', 'watermark.pdf', 'output', processed_filepath]

            # As a simple placeholder, we'll just *copy* the file
            # Replace this 'cp' command with your real command.
            command = ["cp", original_filepath, processed_filepath]

            # Run the command
            subprocess.run(
                command,
                check=True,  # Raise an error if the command fails
                timeout=30,  # Set a timeout (e.g., 30 seconds)
            )

            # --- End of your processing logic ---

        except subprocess.CalledProcessError as e:
            # The command failed
            print(f"Subprocess failed: {e}")
            return jsonify({"success": False, "error": "PDF processing failed."}), 500
        except FileNotFoundError:
            # The command (e.g., 'pdftk' or 'cp') wasn't found on the server
            print("Error: A command-line tool was not found.")
            return (
                jsonify({"success": False, "error": "Server configuration error."}),
                500,
            )
        except subprocess.TimeoutExpired:
            # The process took too long
            print("Error: PDF processing timed out.")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Processing timed out. File may be too large.",
                    }
                ),
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


@app.route("/view/<file_id>", methods=["GET"])
def view_file(file_id):
    """
    Serves the processed file to the user.
    """
    try:
        # Securely build the filename
        filename = f"{secure_filename(file_id)}.pdf"

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


# --- Run the Application ---

if __name__ == "__main__":
    # Run the app.
    # 'debug=True' is great for development as it auto-reloads.
    # For production, use a real web server like Gunicorn or Waitress.
    app.run(debug=True, host="0.0.0.0", port=5000)
