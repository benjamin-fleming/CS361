# Benjamin Fleming
# OSU - CS 361
# 03/09/2025


# import libraries
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import requests
import os

# define image file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """check if a file is allowed based on its extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# create flask app
app = Flask(__name__)

# get base directory for file paths
basedir = os.path.abspath(os.path.dirname(__file__))

# configure the database & folder for uploads
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'images')

# init the sql object
db = SQLAlchemy(app)

# define inventory item model
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50), nullable=True)
    item = db.Column(db.String(100), nullable=False)
    purchase_date = db.Column(db.String(20), nullable=True)  # example: "yyyy-mm-dd"
    value = db.Column(db.Float, nullable=True)
    image = db.Column(db.String(100), nullable=True)  # filename of the uploaded image

    def __repr__(self):
        return f'<InventoryItem {self.item}>'

# create database tables if they don't exist
with app.app_context():
    db.create_all()

# home page
@app.route('/')
def home():
    items = InventoryItem.query.all()
    return render_template('home.html', items=items)

#  new inventory item page
@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        # get form data for the new item
        category = request.form['category']
        subcategory = request.form['subcategory']
        item_name = request.form['item']
        purchase_date = request.form['purchase_date']
        value = request.form['value']

        image_filename = ''
        # check if an image file was provided
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        # create a new inventory item record
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

# edit inventory item page
@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    # get the item or return a 404 if it doesn't exist
    item = InventoryItem.query.get_or_404(item_id)
    if request.method == 'POST':
        # if the delete button was pressed, delete the item
        if 'delete' in request.form:
            db.session.delete(item)
            db.session.commit()
            return redirect(url_for('home'))
        # if the save button was pressed, update the item
        elif 'save' in request.form:
            item.category = request.form['category']
            item.subcategory = request.form['subcategory']
            item.item = request.form['item']
            item.purchase_date = request.form['purchase_date']
            value = request.form['value']
            item.value = float(value) if value else 0.0

            # check if a new image file was provided and process it
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    item.image = filename

            db.session.commit()
            return redirect(url_for('home'))
    return render_template('edit_item.html', item=item)

# route to delete an inventory item
@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    # get the item or return a 404 if not found
    item = InventoryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('home'))

# New route for inline editing via AJAX
@app.route('/update_item', methods=['POST'])
def update_item():
    item_id = request.form.get('item_id')
    if not item_id:
        return jsonify({'status': 'error', 'message': 'Missing item id'}), 400
    item = InventoryItem.query.get_or_404(item_id)

    item.category = request.form.get('category')
    item.subcategory = request.form.get('subcategory')
    item.item = request.form.get('item')
    item.purchase_date = request.form.get('purchase_date')
    value = request.form.get('value')
    item.value = float(value) if value else 0.0

    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image = filename

    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/export_csv')
def export_csv():
    # Retrieve all inventory items
    items = InventoryItem.query.all()

    # Convert the SQLAlchemy objects to a list of dictionaries
    json_data = []
    for item in items:
        json_data.append({
            "category": item.category,
            "subcategory": item.subcategory,
            "item": item.item,
            "purchase_date": item.purchase_date,
            "value": item.value,
            "image": item.image,
        })

    try:
        # POST JSON data to the Node.js microservice
        node_url = "http://localhost:3000/convert_json_to_csv"
        response = requests.post(node_url, json=json_data)

        if response.status_code == 200:
            csv_data = response.content
            # Return the CSV file as an attachment
            return Response(
                csv_data,
                mimetype="text/csv",
                headers={"Content-Disposition": "attachment;filename=inventory.csv"}
            )
        else:
            return "Error exporting CSV", 500
    except Exception as e:
        print("Error:", e)
        return "Error exporting CSV", 500

# run the app if this file is executed directly
if __name__ == '__main__':
    # make sure db tables are created before app starts
    with app.app_context():
        db.create_all()
    app.run(debug=True)