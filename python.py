from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configure upload folder (where images will be saved)
UPLOAD_FOLDER = 'uploads'  # Create this folder in the same directory as your script
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist

# Allowed extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)  # Redirect if no image is uploaded

        image = request.files['image']
        description = request.form['description']

        if image.filename == '':
            return redirect(request.url)  # Redirect if no file is selected

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Here you would typically store the complaint data (image filename, description)
            # in a database. For this example, we'll just print it.
            print(f"Image saved as: {filename}")
            print(f"Description: {description}")

            return "Complaint submitted successfully!"  # Or redirect to a thank you page

        else:
            return "Invalid file type. Please upload an image."

    return render_template('user.html')  # Render your HTML form

if __name__ == '__main__':
    app.run(debug=True)