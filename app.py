import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, usd
import base64

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///business.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    real = []
    if session["tipo"] == 'client':
        real = db.execute(
            "SELECT real.*, products.name FROM real inner join products on products.id = real.product_id WHERE user_id = ?", session["user_id"])
    else:
        real = db.execute(
            "SELECT real.*, products.name FROM real inner join products on products.id = real.product_id")
    total = 0
    if (len(real) > 0):
        for data in real:
            total += round(float(data['total_price']), 2)
            data['total_price'] = usd(data['total_price'])
            data['price'] = usd(data['price'])

    total = usd(total)
    return render_template("index.html", real=real, total=total)


@app.route("/seguro")
@login_required
def seguro():
    seguro = db.execute("SELECT * FROM seguro")
    if (len(seguro) > 0):
        for data in seguro:
            data['insurance'] = usd(data['insurance'])
    return render_template("insurance.html", seguro=seguro)


@app.route("/products")
@login_required
def products():
    products = []
    if session["tipo"] == 'client':
        products = db.execute("SELECT * FROM products where available > 0")
    else:
        products = db.execute("SELECT * FROM products")
    if (len(products) > 0):
        for data in products:
            data['price'] = usd(data['price'])
    return render_template("products.html", products=products)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    if request.method == "POST":
        if session["tipo"] == 'client':
            query = "SELECT history.*, products.name as name, users.username as username FROM history inner join products on products.id = history.product_id inner join users on users.id= history.user_id WHERE user_id = ? "
        else:
            query = "SELECT history.*, products.name as name , users.username as username FROM history inner join products on products.id = history.product_id inner join users on users.id= history.user_id "

        # agregar paginado, orden y busqueda
         # search filter

        search = request.form.get('search[value]')
        if search:
            if session["tipo"] == 'client':
                query += "and ( name like ? or transactionid like ? or username like ? or operation like ?) "
                query1 = db.execute(query, session["user_id"], "%" + search + "%",
                                    "%" + search + "%", "%" + search + "%", "%" + search + "%")
            else:
                query += "where name like ? or transactionid like ? or username like ? or operation like ? "
                query1 = db.execute(query, "%" + search + "%", "%" + search +
                                    "%", "%" + search + "%", "%" + search + "%")
        else:
            if session["tipo"] == 'client':
                query1 = db.execute(query, session["user_id"])
            else:
                query1 = db.execute(query)

         # sorting
        order = []
        i = 0
        while True:
            col_index = request.form.get(f'order[{i}][column]')
            if col_index is None:
                break
            col_name = request.form.get(f'columns[{col_index}][data]')

            if col_name not in ['ammount', 'price', 'total_price', 'operation', 'username', 'name', 'date_start', 'date_end', 'transactionid', 'current_day']:
                col_name = 'transactionid'
            order = request.form.get(f'order[{i}][dir]')
            order = "asc"
            i += 1
        if order:
            query += f"ORDER BY {col_name} {order}"

        # pagination
        start = request.form.get('start', type=int)
        length = request.form.get('length', type=int)
        query += " LIMIT ? OFFSET ?"

        if search:
            if session["tipo"] == 'client':
                result = db.execute(query, session["user_id"], '%'+search+'%',
                                    '%'+search+'%', '%'+search+'%', '%'+search+'%', length, start)
            else:
                result = db.execute(query, '%'+search+'%', '%'+search+'%',
                                    '%'+search+'%', '%'+search+'%', length, start)
        else:
            if session["tipo"] == 'client':
                result = db.execute(query, session["user_id"], length, start)
            else:
                result = db.execute(query, length, start)

        total_filtered = len(query1)

        for data in result:
            data['price'] = usd(data['price'])
            data['total_price'] = usd(data['total_price'])

         # response
        return {
            'data': result,
            'recordsFiltered': total_filtered,
            'recordsTotal': total_filtered,
            'draw': request.form.get('draw', type=int)
        }

    if request.method == "GET":
        return render_template("history.html")


@app.route("/rent", methods=["GET", "POST"])
@login_required
def rent():
    if request.method == "POST":
        product = request.form.get("product")
        if not product:
            flash(u'Must provide the product', 'error')
            return redirect('/products_rent')
        try:
            product = int(product)
        except ValueError:
            flash(u'Product must be in whole number', 'error')
            return redirect('/products_rent')
        start = request.form.get("start")
        if not start:
            flash(u'Must provide start date', 'error')
            return redirect('/products_rent')
        end = request.form.get("end")
        if not end:
            flash(u'Must provide end date', 'error')
            return redirect('/products_rent')
        cant = request.form.get("cant")
        if not cant:
            flash(u'Must provide ammount', 'error')
            return redirect('/products_rent')
        try:
            cant = int(cant)
        except ValueError:
            flash(u'Ammount must be in whole number', 'error')
            return redirect('/products_rent')
        if cant < 1:
            flash(u'must provide Ammount > 0', 'error')
            return redirect('/products_rent')
        result = db.execute("SELECT * FROM products where id = ?", product)
        if result == None:
            flash(u'The product is not correct', 'error')
            return redirect('/products_rent')
        if cant > result[0]["available"]:
            flash(u'The Ammount is not correct', 'error')
            return redirect('/products_rent')
        idt = str(base64.b64encode(os.urandom(6)).decode('ascii'))

        user = request.form.get("user")
        if not user:
            user = session["user_id"]

        totalp = totalO(result[0]['price']) * cant
        db.execute(
            "INSERT INTO history (ammount, price, total_price, operation, user_id, product_id, date_start, date_end, transactionid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            cant, result[0]["price"], totalp, 'rent', user, product, start, end, idt)
        db.execute(
            "INSERT INTO real (operation, user_id, ammount, price, total_price, date_start, date_end, transactionid, product_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            'rent', user, cant, result[0]["price"], totalp, start, end, idt, product)

        db.execute(
            "UPDATE products SET available = ? WHERE id= ?", result[0]['available']-cant, product)

        real = db.execute(
            "SELECT real.*, products.name FROM real inner join products on products.id = real.product_id where user_id =?", user)
        total = 0
        if (len(real) > 0):
            for data in real:
                total += round(float(data['total_price']), 2)
                data['price'] = usd(data['price'])
                data['total_price'] = usd(data['total_price'])
        total = usd(total)
    flash(u'Rented Product', 'success')
    return render_template("index.html", real=real, total=total)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash(u'Must provide username', 'error')
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash(u'Must provide password', 'error')
            return redirect("/login")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash(u'Invalid username and/or password', 'error')
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["tipo"] = rows[0]["tipo"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash(u'Must provide username', 'error')
            return redirect("/register")
        password = request.form.get("password")
        if not password:
            flash(u'Must rovide password', 'error')
            return redirect("/register")
        confirm_password = request.form.get("confirmation")
        if not confirm_password:
            flash(u'Must rovide confirm password', 'error')
            return redirect("/register")
        if password != confirm_password:
            flash(u'Password and confirmation do not match', 'error')
            return redirect("/register")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        if len(rows) != 0:
            flash(u'Username already exist', 'error')
            return redirect("/register")
        passworhash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, hash, tipo) VALUES (%s,%s, %s)", username, passworhash, 'client'
        )
        flash(u'Registered user', 'success')
        return redirect("/")
    return render_template("register.html")


@app.route("/products_rent", methods=["GET"])
@login_required
def products_rent():
    products = db.execute("SELECT * FROM products")
    if (len(products) > 0):
        for data in products:
            data['price'] = usd(data['price'])
    users = db.execute("SELECT * FROM users")
    list = []
    if (len(users) > 0):
        for data in users:
            list.append({
                "id": data['id'],
                "username": data['username']
            })

    return render_template("rent.html", products=products, users=list)


@app.route('/api/data', methods=["GET", "POST"])
def data():
    if request.method == "POST":
        query = "SELECT * FROM products "
        # search filter
        search = request.form.get('search[value]')
        if search:
            query += "where name like ? or identifier like ? "
            query1 = db.execute(query, "%" + search + "%", "%" + search + "%")
        else:
            query1 = db.execute(query)

        # sorting
        order = []
        i = 0
        while True:
            col_index = request.form.get(f'order[{i}][column]')
            if col_index is None:
                break
            col_name = request.form.get(f'columns[{col_index}][data]')

            if col_name not in ['name', 'amount', 'available', 'price', 'identifier']:
                col_name = 'name'
            order = request.form.get(f'order[{i}][dir]')
            order = "asc"
            i += 1
        if order:
            # query = query.order_by(*order)
            query += f"ORDER BY {col_name} {order}"

        # pagination
        start = request.form.get('start', type=int)
        length = request.form.get('length', type=int)
        query += " LIMIT ? OFFSET ?"

        if search:
            result = db.execute(query, '%'+search+'%', '%'+search+'%', length, start)
        else:
            result = db.execute(query, length, start)

        total_filtered = len(query1)

        iva = db.execute("Select insurance from seguro")
        if len(iva) > 0:
            imp = iva[0]['insurance']

        for data in result:
            data['total'] = usd(totalO(data['price']))
            data['price'] = usd(data['price'])
            data['edit'] = f'<a href="/edit_product?id={data['id']}">Edit</a>'

        # response
        return {
            'data': result,
            'recordsFiltered': total_filtered,
            'recordsTotal': total_filtered,
            'draw': request.form.get('draw', type=int)
        }


def totalO(price):
    iva = db.execute("Select insurance from seguro")
    if len(iva) > 0:
        return (price * iva[0]['insurance'] * 0.01) + price
    return price


@app.route("/return", methods=["GET", "POST"])
@login_required
def returnProduct():
    if request.method == "GET":
        real = []
        id = request.args.get('id')
        if not id:
            flash(u'Must provide id', 'error')
            return redirect('/products_return')
        real = db.execute("SELECT * FROM real where id = ?", id)
        if real == None:
            flash(u'The id is not correct', 'error')
            return redirect('/products_return')
        result = db.execute("SELECT * FROM products where id = ?", real[0]['product_id'])
        if result == None:
            flash(u'The product is not correct', 'error')
            return redirect('/products_return')

        db.execute(
            "INSERT INTO history (ammount, price, total_price, operation, user_id, product_id, date_start, date_end, transactionid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            real[0]['ammount'], real[0]["price"], real[0]["total_price"], 'return', real[0]['user_id'],  real[0]['product_id'], real[0]['date_start'], real[0]['date_end'], real[0]['transactionid'])
        db.execute(
            "UPDATE products SET available = ? WHERE id= ?", result[0]['available']+real[0]['ammount'], real[0]['product_id'])

        db.execute(
            "DELETE from real WHERE id= ?", id)

        flash(u'Return product', 'success')
        return redirect("/products_return")


@app.route('/api/real', methods=["GET", "POST"])
def datareal():
    if request.method == "POST":
        if session["tipo"] == 'client':
            query = "SELECT real.*, products.name, users.username FROM real inner join products on products.id = real.product_id inner join users on users.id = real.user_id WHERE user_id = ? "
        else:
            query = "SELECT real.*, products.name, users.username FROM real inner join products on products.id = real.product_id inner join users on users.id = real.user_id "

        # search filter
        search = request.form.get('search[value]')
        if search:
            if session["tipo"] == 'client':
                query += "and ( name like ? or transactionid like ? or username like ? ) "
                query1 = db.execute(query, session["user_id"],
                                    "%" + search + "%", "%" + search + "%", "%" + search + "%")
            else:
                query += "where name like ? or transactionid like ? or username like ? "
                query1 = db.execute(query, "%" + search + "%", "%" + search + "%", "%" + search + "%")
        else:
            if session["tipo"] == 'client':
                query1 = db.execute(query, session["user_id"])
            else:
                query1 = db.execute(query)

        # sorting
        order = []
        i = 0
        while True:
            col_index = request.form.get(f'order[{i}][column]')
            if col_index is None:
                break
            col_name = request.form.get(f'columns[{col_index}][data]')

            if col_name not in ['name', 'amount', 'date_start', 'date_end', 'operation', 'price', 'total_price', 'transactionid', 'username']:
                col_name = 'transactionid'
            order = request.form.get(f'order[{i}][dir]')
            order = "asc"
            i += 1
        if order:
            query += f"ORDER BY {col_name} {order}"

        # pagination
        start = request.form.get('start', type=int)
        length = request.form.get('length', type=int)
        query += " LIMIT ? OFFSET ?"

        if search:
            if session["tipo"] == 'client':
                result = db.execute(query, session["user_id"],
                                    '%'+search+'%', '%'+search+'%',  '%'+search+'%', length, start)
            else:
                result = db.execute(query, '%'+search+'%', '%'+search+'%', '%'+search+'%', length, start)
        else:
            if session["tipo"] == 'client':
                result = db.execute(query, session["user_id"], length, start)
            else:
                result = db.execute(query, length, start)

        total_filtered = len(query1)

        for data in result:
            data['total'] = usd(totalO(data['price']))
            data['price'] = usd(data['price'])
            data['return'] = f'<a href="/return?id={data['id']}">Return</a>'

        # response
        return {
            'data': result,
            'recordsFiltered': total_filtered,
            'recordsTotal': total_filtered,
            'draw': request.form.get('draw', type=int)
        }


@app.route("/products_return", methods=["GET"])
@login_required
def products_return():
    # flash(u'Invalid password provided', 'error')
    # flash(u'Invalid password provided', 'success')
    return render_template("return.html")


@app.route("/new_product", methods=["GET", "POST"])
@login_required
def new_product():
    if request.method == "POST":
        price = request.form.get("price")
        if not price:
            flash(u'Must provide price', 'error')
            return redirect('/new_product')
        name = request.form.get("name")
        if not name:
            flash(u'Must provide name', 'error')
            return redirect('/new_product')

        amount = request.form.get("amount")
        if not amount:
            flash(u'Must provide amount', 'error')
            return redirect('/new_product')
        available = request.form.get("available")
        if not available:
            flash(u'Must provide available', 'error')
            return redirect('/new_product')
        try:
            amount = int(amount)
        except ValueError:
            flash(u'Amount must be in whole number', 'error')
            return redirect('/new_product')
        try:
            available = int(available)
        except ValueError:
            flash(u'Available must be in whole number', 'error')
            return redirect('/new_product')
        try:
            price = float(price)
        except ValueError:
            flash(u'Price must be numbers', 'error')
            return redirect('/new_product')

        if amount < 0 or available < 0:
            flash(u'Must provide available and amount  >= 0', 'error')
            return redirect('/new_product')

        if available > amount:
            flash(u'the ammount is not correct', 'error')
            return redirect('/new_product')
        idt = str(base64.b64encode(os.urandom(6)).decode('ascii'))
        db.execute(
            "INSERT INTO products (	amount, available, 	price, name,identifier) VALUES (?, ?, ?, ?, ?)",
            amount, available, price, name, idt)
        flash(u'Saved Product', 'success')
        return redirect("/products")
    if request.method == "GET":
        return render_template("new_product.html")


@app.route("/insurance_edit", methods=["GET", "POST"])
@login_required
def insurance_edit():
    if request.method == "POST":
        seguro = request.form.get("seguro")
        if not seguro:
            flash(u'Must provide the insurance', 'error')
            return redirect("/seguro")
        cant = request.form.get("cant")
        if not cant:
            flash(u'Must provide the ammount', 'error')
            return redirect("/seguro")
        try:
            cant = int(cant)
        except ValueError:
            flash(u' the ammount must be in whole number', 'error')
            return redirect("/seguro")
        if cant < 1:
            flash(u'must provide ammount > 0', 'error')
            return redirect("/seguro")
        db.execute(
            "UPDATE seguro SET insurance = ? WHERE id= ?", cant, seguro)
        flash(u'Edited insurance', 'success')
        return redirect("/seguro")
    return redirect("/seguro")


@app.route("/edit_product", methods=["GET", "POST"])
@login_required
def edit_product():
    if request.method == "POST":
        idp = request.form.get("id")
        if not idp:
            flash(u'Must provide the product', 'error')
            return redirect("/edit_product")
        price = request.form.get("price")
        if not price:
            flash(u'Must provide the price', 'error')
            return redirect("/edit_product")
        name = request.form.get("name")
        if not name:
            flash(u'Must provide the name', 'error')
            return redirect("/edit_product")
        amount = request.form.get("amount")
        if not amount:
            flash(u'Must provide the amount', 'error')
            return redirect("/edit_product")
        available = request.form.get("available")
        if not available:
            flash(u'Must provide the available', 'error')
            return redirect("/edit_product")
        try:
            amount = int(amount)
        except ValueError:
            flash(u'Amount must be in whole number', 'error')
            return redirect("/edit_product")
        try:
            available = int(available)
        except ValueError:
            flash(u'Available must be in whole number', 'error')
            return redirect("/edit_product")
        try:
            price = float(price)
        except ValueError:
            flash(u'Price must be in number', 'error')
            return redirect("/edit_product")

        if amount < 0 or available < 0:
            flash(u'Must provide available and amount  >= 0', 'error')
            return redirect("/edit_product")

        if available > amount:
            flash(u'The ammount is not correct', 'error')
            return redirect("/edit_product")
        idt = str(base64.b64encode(os.urandom(6)).decode('ascii'))

        db.execute(
            "UPDATE products SET amount = ?, available = ?, price= ?, name= ? WHERE id= ?", amount, available, price, name, idp)

        flash(u'Saved Product', 'success')
        return redirect("/products")
    if request.method == "GET":
        id = request.args.get('id')
        if not id:
            flash(u'Must provide id', 'error')
            return redirect("/edit_product")
        product = db.execute("SELECT * FROM products where id = ?", id)
        if len(product) > 0:
            return render_template("edit_product.html", product=product)
        else:
            flash(u'Must provide product', 'error')
            return redirect("/edit_product")
