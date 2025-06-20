from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>Business Card Upload</title></head>
        <body>
            <h2>Upload a Business Card</h2>
            <form method="post" action="/extract" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*" required>
                <input type="submit" value="Extract Info">
            </form>
        </body>
        </html>
    """)

@app.route("/extract", methods=["POST"])
def extract():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    # Just confirms receipt for now
    return jsonify({"message": "Image uploaded successfully. OCR coming soon."})

# This is optional for local run, ignored by Vercel
if __name__ == "__main__":
    app.run(debug=True)
