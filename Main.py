import requests
from flask import Flask, redirect, render_template, request, session, make_response, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError 
from database import db, User, Transaction
from helpers import login_required , apology
import datetime
from functools import wraps 
import json
from decimal import Decimal, InvalidOperation


app = Flask(__name__)
app.secret_key = "AZ12345"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ArmaanZ.db"  # Change the name of the database file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
db.init_app(app)
with app.app_context():
    db.create_all()
@app.route("/")
@login_required 
def index():
    """Show the portfolio """
    user_id = session["user_id"]
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    cash_db = User.query.filter_by(id=user_id).first()
    cash = cash_db.cash if cash_db else 0.0
    return render_template("index.html", database=transactions, cash=cash)


API_KEY = 'CG-mAxxE5yH4iuQ1uVqcY9tFRXG'
@app.route('/get/simple/price', methods=["GET"])
def get_bitcoin_price():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {'ids': 'bitcoin',
        'vs_currencies': 'usd'
    }
    headers = {
        'X-CoinGecko-API-Key': API_KEY,
        'accept': 'application/json'
    }
    

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        # The data structure is { 'bitcoin': { 'usd': price } }
        bitcoin_data = data.get('bitcoin', {})
        price = bitcoin_data.get('usd', "Price not available")
    try:
        price = float(bitcoin_data.get('usd', 0.0))
    except (TypeError, ValueError):
        return None
    return price

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if len(password) < 4:
            response = make_response ("Password must be greater than 4 characters.")
            response.status_code = 400
            return response
        if not confirmation:
            response = make_response("Must provide a confirmation.")
            response.status_code=400
            return response
        if password != confirmation:
            response = make_response("passwords dont match.")
            response.status_code = 400
            return response 

        hash = generate_password_hash(password)

        new_user = User(username=username, hash=hash)

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            response = make_response("Username already exists.")
            response.status_code=400
            return response

        session["user_id"] = new_user.id

        return redirect("/")
    return render_template("registration_form.html")

@app.route("/registration_form", methods=["GET"])
def show_registration_form():
    return render_template("registration_form.html")
   


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.hash, password):
            return ("Invalid username and/or password", 403)

        session["user_id"] = user.id

        return redirect("/")

    # User reached the route via GET (e.g., by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log the user out"""

    # Forget any user_id
    session.clear()

    # Redirect the user to the login form
    return redirect("/")

@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    if request.method == "GET":
        return render_template("add_cash.html")
    else:
        new_cash = request.form.get("new_cash")

        if not new_cash:
            return apology("Input the amount of money")

        # Convert the new cash to Decimal for precision in financial calculation
        try:
            new_cash_decimal = Decimal(new_cash)
        except InvalidOperation:
            return apology("Invalid amount")

        user_id = session["user_id"]
        user = User.query.get(user_id)  # Assumes we have a User model

        if not user:
            return apology("User not found")

        user_cash = user.cash
        # Add the cash amounts
        uptd_cash = user_cash + new_cash_decimal

        user.cash = uptd_cash
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return apology("An error occurred while adding cash")

        flash("Added cash successfully!")

        return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = request.form.get("symbol").lower()  # Convert the symbol to lowercase since CoinGecko uses lowercase ids

        if not symbol:
            return apology("Must provide a symbol.")

        # First, attempt to resolve the symbol to an id using the CoinGecko /coins/list endpoint
        list_url = 'https://api.coingecko.com/api/v3/coins/list'
        response = requests.get(list_url)
        if response.status_code == 200:
            coins_list = response.json()
            # You may need to handle pagination here if the response is paginated
            coin = next((item for item in coins_list if item['symbol'] == symbol), None)
            if coin is None:
                return apology(f"Symbol '{symbol}' does not exist.")

            # Now use the resolved id to get the price
            price_url = 'https://api.coingecko.com/api/v3/simple/price'
            params = {
                'ids': coin['id'],  # Use the id resolved from the symbol
                'vs_currencies': 'usd'
            }
            headers = {
                'X-CoinGecko-API-Key': API_KEY,
                'accept': 'application/json'
            }

            response = requests.get(price_url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if coin['id'] in data:
                    price = data[coin['id']]['usd']
                    return render_template("quoted.html", name=coin['id'].capitalize(), price=price)
                else:
                    return apology(f"Data for '{coin['id']}' not found.")
            else:
                return apology("Unable to fetch data.")
        else:
            return apology("Could not retrieve the list of coins.")


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

date = datetime.datetime.now()

def clean_price(price_str):
    return float(price_str.replace('$','').replace(',',''))

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    user_id = session['user_id']
    user = User.query.get(user_id)

    # Fetch the current bitcoin price
    bitcoin_price = get_bitcoin_price()  # Ensure this returns a float
    if bitcoin_price is None:
        flash("Unable to fetch Bitcoin price", category='error')
        return redirect(url_for('index'))

    bitcoin_price_decimal = Decimal(str(bitcoin_price))
    max_bitcoin = user.cash / bitcoin_price_decimal if bitcoin_price_decimal > 0 else 0

    if request.method == "GET":
        return render_template("buy.html", bitcoin_price=bitcoin_price, user_cash=user.cash, max_bitcoin=max_bitcoin)

    # POST request handling
    symbol = "BTC"  # Set the symbol directly since you're only dealing with Bitcoin
    try:
        cash_to_spend = Decimal(request.form.get("cash"))
        if cash_to_spend <= 0 or cash_to_spend > user.cash:
            flash("Invalid cash amount", category='error')
            return redirect(url_for('buy'))
    except InvalidOperation:
        flash("Invalid cash amount", category='error')
        return redirect(url_for('buy'))

    shares = cash_to_spend / bitcoin_price_decimal

    # Wrap database operations in a transaction
    try:
        user.cash -= cash_to_spend
        transaction = Transaction(user_id=user_id, symbol=symbol, shares=shares, price=bitcoin_price)
        db.session.add(transaction)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while processing the transaction: " + str(e), category='error')
        return redirect(url_for('buy'))

    flash("Bought successfully!", category='message')
    return redirect(url_for("index"))

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    user_id = session['user_id']
    user = User.query.get(user_id)

    # Fetch the current bitcoin price
    bitcoin_price = get_bitcoin_price()
    if bitcoin_price is None:
        flash("Unable to fetch Bitcoin price", category='error')
        return redirect(url_for('index'))

    bitcoin_price_decimal = Decimal(str(bitcoin_price))

    # Calculate the total bitcoin shares the user owns
    total_shares = sum([transaction.shares for transaction in user.transactions if transaction.symbol == 'BTC'])

    if request.method == "GET":
        return render_template("sell.html", bitcoin_price=bitcoin_price, total_shares=total_shares)

    # POST request handling
    try:
        shares_to_sell = Decimal(request.form.get("shares"))
        if shares_to_sell <= 0 or shares_to_sell > total_shares:
            flash("Invalid share amount", category='error')
            return redirect(url_for('sell'))
    except InvalidOperation:
        flash("Invalid share amount", category='error')
        return redirect(url_for('sell'))

    # Calculate the cash value of the sold shares
    cash_from_sale = shares_to_sell * bitcoin_price_decimal

    # Wrap database operations in a transaction
    try:
        user.cash += cash_from_sale
        # Record a sell transaction as a negative number of shares
        sell_transaction = Transaction(user_id=user_id, symbol='BTC', shares=-shares_to_sell, price=bitcoin_price)
        db.session.add(sell_transaction)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while processing the transaction: " + str(e), category='error')
        return redirect(url_for('sell'))

    flash("Sold successfully!", category='message')
    return redirect(url_for("index"))


@app.route("/history")
@login_required
def history():
    user_id = session['user_id']

    # Fetch all transactions of the logged-in user
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()

    return render_template("history.html", transactions=transactions)
