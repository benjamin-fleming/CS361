from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Return True if the file has one of the allowed extensions."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)

# Base directory for file paths
basedir = os.path.abspath(os.path.dirname(__file__))

# Configure the SQLite database and file upload folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'images')

db = SQLAlchemy(app)

# Database model for an inventory item
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50), nullable=True)
    item = db.Column(db.String(100), nullable=False)
    purchase_date = db.Column(db.String(20), nullable=True)  # e.g., "YYYY-MM-DD"
    value = db.Column(db.Float, nullable=True)
    image = db.Column(db.String(100), nullable=True)  # Stores the filename of the uploaded image

    def __repr__(self):
        return f'<InventoryItem {self.item}>'

# Create tables before the first request
with app.app_context():
    db.create_all()

# Home page: display all inventory items
@app.route('/')
def home():
    items = InventoryItem.query.all()
    return render_template('home.html', items=items)

# Route to add a new inventory item
@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        category = request.form['category']
        subcategory = request.form['subcategory']
        item_name = request.form['item']
        purchase_date = request.form['purchase_date']
        value = request.form['value']

        image_filename = ''
        # Check if an image file was uploaded
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        new_item = InventoryItem(
            category=category,
            subcategory=subcategory,
            item=item_name,
            purchase_date=purchase_date,
            value=float(value) if value else 0.0,
            image=image_filename
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_item.html')

# Route to edit an existing inventory item
@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.category = request.form['category']
        item.subcategory = request.form['subcategory']
        item.item = request.form['item']
        item.purchase_date = request.form['purchase_date']
        value = request.form['value']
        item.value = float(value) if value else 0.0

        # If a new image file is uploaded, process it
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                item.image = filename

        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit_item.html', item=item)

if __name__ == '__main__':
    # Ensure tables are created before running the app
    with app.app_context():
        db.create_all()
    app.run(debug=True)