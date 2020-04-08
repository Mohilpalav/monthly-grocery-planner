from flask import Flask, render_template, send_file, g, request, jsonify, session, escape, redirect
from passlib.hash import pbkdf2_sha256
import os
from db import Database
from base64 import b64encode

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = b'lkj98t&%$3rhfSwu3D'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = Database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/course/<path:path>')
def base_static(path):
    return send_file(os.path.join(app.root_path, '..', '..', 'course', path))

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        typed_password = request.form['password']
        if name and username and typed_password:
            encrypted_password = pbkdf2_sha256.encrypt(typed_password, rounds=200000, salt_size=16)
            get_db().create_user(name, username, encrypted_password)
            return redirect('/login')
    return render_template('create_user.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        typed_password = request.form['password']
        if username and typed_password:
            user = get_db().get_user(username)
            if user:
                if pbkdf2_sha256.verify(typed_password, user['password']):
                    session['user'] = user
                    return redirect('/user')
                else:
                    message = "Incorrect password, please try again"
            else:
                message = "Unknown user, please try again"
        elif username and not typed_password:
            message = "Missing password, please try again"
        elif not username and typed_password:
            message = "Missing username, please try again"
    return render_template('login.html', message=message)

@app.route('/search', methods=['GET', 'POST'])
def display_products():
    message = None
    products = get_db().get_products()
    images = []
    for i in range(0,len(products)):
        images.append(b64encode(products[i][4]).decode("utf-8"))

    if request.method == 'POST':
        list = request.form['product_id']
        str = ""+list
        quantity = request.form[str]
        if(quantity == ""):
            message = "Please enter the quantity"
        else:
            get_db().add(list,quantity,session['user']['user_id'])

    return render_template('search.html', products = products, len = len(products), images = images, message = message)

@app.route('/list', methods=['GET', 'POST'])
def display_list():
    length = 0
    message = None
    images = []

    products = get_db().get_list(session['user']['user_id'])
    total = get_db().get_total(session['user']['user_id'])

    if products != 0:
        length = len(products)
    else:
        message = "No items to display"
    for i in range(0,length):
        images.append(b64encode(products[i][2]).decode("utf-8"))

    if request.method == 'POST':
        list = request.form['product_id']
        get_db().remove(list,session['user']['user_id'])

    return render_template('list.html', products = products, len = length, images = images, total = total, message = message)

@app.route('/bill', methods=['GET', 'POST'])
def display_bill():
    length = 0
    message = None
    bill_id = 0
    pressed =0
    products=[]
    images=[]
    if request.method == 'POST':
        bill_id = request.form['bill']
        products = get_db().get_bill(bill_id,session['user']['user_id'])
        pressed = 1
        if products != 0:
            length = len(products)
        else:
            message = "No items to display"
        for i in range(0,length):
            images.append(b64encode(products[i][2]).decode("utf-8"))

    return render_template('bill.html', products = products, len = length, images = images, message = message, pressed=pressed)

@app.route('/analyze', methods=['GET', 'POST'])
def analysis():
    lenm = 0
    lene = 0
    lenc = 0
    message = None
    bill_id = 0
    pressed =0
    bill_total =0
    missed_products=[]
    extra_products=[]
    missed_images=[]
    extra_images=[]
    categories=[]
    if request.method == 'POST':
        bill_id = request.form['receipt']
        categories = get_db().top_categories(bill_id,session['user']['user_id'])
        missed_products = get_db().get_missed_products(bill_id,session['user']['user_id'])
        extra_products = get_db().get_extra_products(bill_id,session['user']['user_id'])
        bill_total = get_db().get_bill_total(bill_id,session['user']['user_id'])
        pressed = 1

        if extra_products != 0:
            lene = len(extra_products)
            for i in range(0,lene):
                extra_images.append(b64encode(extra_products[i][1]).decode("utf-8"))
        if missed_products != 0 and categories != 0:
            lenm = len(missed_products)
            lenc = len(categories)
        else:
            message = "No items to display"
        for i in range(0,lenm):
            missed_images.append(b64encode(missed_products[i][1]).decode("utf-8"))

    return render_template('analyze.html',missed_products = missed_products,extra_products=extra_products,extra_images=extra_images,lene=lene, lenm = lenm, missed_images = missed_images, message = message,categories = categories, lenc =lenc, pressed=pressed, bill_total = bill_total)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/<name>')
def generic(name):
    if 'user' in session:
        return render_template(name + '.html')
    else:
        return redirect('/login')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
