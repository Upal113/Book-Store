import base64
from itertools import product
from operator import delitem
import re
from flask import *
from datetime import datetime, time, timedelta
import time
from flask_sqlalchemy import *
import datetime
from datetime import timedelta
from werkzeug.utils import secure_filename
import os
import re
import random

cwd = os.getcwd()
app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=100)
app.app_context().push()
app.secret_key = 'qewtrytydy'
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Books.sql'
app.config['SECRET_KEY'] = 'superb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = cwd + '/static/Images/'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
from base64 import b64encode

db = SQLAlchemy(app)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    writer = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer)
    path = db.Column(db.String(100))
    mimetype = db.Column(db.String, nullable=False)
    posted = db.Column(db.DateTime, default = datetime.datetime.now().date)


    def __init__(self, name,  descrption, writer, price, path, mimetype):
        self.name = name
        self.description = descrption
        self.writer = writer
        self.price = price
        self.path = path
        self.mimetype = mimetype

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method=='POST':
       
        search = request.form['search-txt']
        session['search'] = search
        return redirect(f'/search/{search}/')
    else:
        pre_all_product= Books.query.all()
        all_product = list(random.sample(pre_all_product, int(len(pre_all_product))))  
        return render_template('products.html', all_products= all_product)

@app.route('/author/<author_name>/')        
def author(author_name):
    Book = Books.query.filter_by(writer=author_name)
    return render_template('author.html', others=Book)



@app.route('/book/<int:id>/')
def book_details(id):
    Book = Books.query.filter_by(id=id).first()
    book_name = str(Book.name)
    others = Books.query.filter(Books.name.contains(book_name.split(' ')[0])).filter(Books.name != Book.name)
    return render_template('book.html', Book= Book, others=others)


@app.route('/search/<searchterm>/', methods=['GET', 'POST'])
def search(searchterm):
    if request.method=='POST':
       
        search = request.form['search-txt']
        session['search'] = search
        return redirect(f'/search/{search}/')
    searchterm = session['search']   
    pre_found_items = list(Books.query.filter(Books.description.contains(searchterm)).all())
    found_items = list(random.sample(pre_found_items, int(len(pre_found_items))))
    return render_template('products.html' , all_products= found_items, searched = searchterm)



@app.route('/ourteam')
def team():
    return render_template('team.html')  

@app.route('/thankyou')
def thanks():
    return render_template('thankyou.html')

@app.route('/admin/additem/', methods=['GET', 'POST'])
def add_item():
    if 'admin' in session:
        if request.method == 'POST':
            name = request.form['book-name']
            price = request.form['book-price']
            author = request.form['book-writer-name']
            description = request.form['book-description']
            image = request.files['book-image']
            file_name = secure_filename(image.filename)
            mimetype = secure_filename(image.mimetype)
            
            if mimetype=="image_png" or "image_jpeg":
                if request.form['security-key'] == str(int(20211112)):
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'] ,file_name))
                    new_book = Books(name=name, descrption=description, writer=author, 
                    price=price,path = file_name , mimetype=mimetype)
                    db.session.add(new_book)
                    db.session.commit()
            return redirect(url_for('home'))
        return render_template('add-product.html')
    else:
        return redirect(url_for('admin_login'))    

@app.route('/admin/delete/', methods=['GET', 'POST'])
def delete():
    if 'admin' in session:
        if request.method=='POST':
            delete_entry = request.form['delete']
            deleteentry = Books.query.filter_by(id = delete_entry).first()
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], deleteentry.path))
            db.session.delete(deleteentry)
            db.session.commit()
        paths = []
        all_product= Books.query.all()
        for p in all_product:
            pth = p.path
            paths.append(pth) 
           
        return render_template('delete.html', all_products= zip(all_product, paths))   
    else:
        return redirect(url_for('admin_login'))    

@app.route('/admin/login/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username=='admin' and password=='admin':
            session['admin'] = username
            session.permanent = True
            return redirect(url_for('add_item'))
        else:
            return redirect(request.url)    
    return render_template('login.html')    


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
