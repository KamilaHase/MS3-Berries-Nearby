import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import (
    generate_password_hash, check_password_hash, safe_str_cmp)
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


# list of offers
@app.route("/offers")
def offers():
    offers = list(mongo.db.offers.find())
    location = mongo.db.location.find()
    return render_template("offers.html", offers=offers, location=location)


# search functionality
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    offers = list(mongo.db.offers.find({"$text": {"$search": query}}))
    return render_template("offers.html", offers=offers)


# register new user
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        # check if email already exists in db
        existing_username = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        # check if passwords are same
        password_confirm = safe_str_cmp(password, confirm)

        if existing_username:
            flash("This username has already been used.")
            return redirect(url_for("register"))

        elif not password_confirm:
            flash('Passwords do not match, please try again')
            return redirect(url_for('register'))

        register = {
            "first_name": request.form.get("first_name").lower(),
            "last_name": request.form.get("last_name").lower(),
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


# sign in existing user
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # check if username already exists in db
        existing_username = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_username:
            # ensure inserted password matches username input
            if check_password_hash(
               existing_username["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome! You are signed in as {}".format(
                        request.form.get("username")))
                return redirect(url_for(
                        "profile", username=session["user"]))

            else:
                # invalid password match
                flash("Incorrect username and/or password.")
                return redirect(url_for("signin"))

        else:
            # user doesn't exist
            flash("Incorrect username and/or password.")
            return redirect(url_for("signin"))

    return render_template("signin.html")


# profile page
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    offers = list(mongo.db.offers.find({"created_by": session["user"]}))
    # show user's offers
    print(offers)
    if session["user"]:
        return render_template(
            "profile.html", username=username, offers=offers)

    return redirect(url_for("signin"))


# sign out
@app.route("/signout")
def signout():
    # remove user from session cookie
    flash("You have been signed out.")
    session.pop("user")
    return redirect(url_for("signin"))


# add new offer
@app.route("/add_offer", methods=["GET", "POST"])
def add_offer():
    if request.method == "POST":
        price_free = "on" if request.form.get("price_free") else "off"

        offers = {
            "category_fruits": request.form.get("category_fruits"),
            "contact": request.form.get("contact"),
            "category_location": request.form.get("category_location"),
            "date_of_pick_up": request.form.get("date_of_pick_up"),
            "description": request.form.get("description"),
            "equipment": request.form.get("equipment"),
            "time_start": request.form.get("time_start"),
            "time_end": request.form.get("time_end"),
            "price_free": price_free,
            "price": request.form.get("price"),
            "created_by": session["user"]
        }
        mongo.db.offers.insert_one(offers)

        flash("Offer Successfully Added")
        return redirect(url_for("offers"))

    fruit_categories = mongo.db.fruit_categories.find().sort(
        "category_fruits", 1)
    location = mongo.db.location.find().sort(
        "category_location", 1)
    return render_template(
        "add_offer.html", fruit_categories=fruit_categories, location=location)


# edit existing offer
@app.route("/edit_offer/<offer_id>", methods=["GET", "POST"])
def edit_offer(offer_id):
    if request.method == "POST":
        price_free = "on" if request.form.get("price_free") else "off"

        submit = {
            "category_fruits": request.form.get("category_fruits"),
            "contact": request.form.get("contact"),
            "category_location": request.form.get("category_location"),
            "date_of_pick_up": request.form.get("date_of_pick_up"),
            "description": request.form.get("description"),
            "equipment": request.form.get("equipment"),
            "time_start": request.form.get("time_start"),
            "time_end": request.form.get("time_end"),
            "price_free": price_free,
            "price": request.form.get("price"),
            "created_by": session["user"]
        }
        mongo.db.offers.update({"_id": ObjectId(offer_id)}, submit)

        flash("Offer Successfully Updated")

    offer = mongo.db.offers.find_one({"_id": ObjectId(offer_id)})
    fruit_categories = mongo.db.fruit_categories.find().sort(
        "category_fruits", 1)
    location = mongo.db.location.find().sort("category_location", 1)

    return render_template(
        "edit_offer.html", offer=offer, fruit_categories=fruit_categories,
        location=location)


# delete an offer
@app.route("/delete_offer/<offer_id>")
def delete_offer(offer_id):
    mongo.db.offers.delete_one({"_id": ObjectId(offer_id)})
    mongo.db.reports.delete_many({"offer_id": offer_id})
    flash("Offer Deleted")
    return redirect(url_for("offers"))


# send a report of an offer
@app.route('/report_offer/<offer_id>', methods=['GET', 'POST'])
def report_offer(offer_id):
    if request.method == 'POST':
        mongo.db.reports.insert_one(
            {
                'report_content': request.form.get('report_content'),
                'reported_by': session["user"],
                'offer_id': offer_id
            })
        mongo.db.offers.update_one(
            {"_id": ObjectId(offer_id)},
            {"$set": {"reported": True}})
        flash('Offer reported, thank you.')
    return redirect(url_for('offers'))


# list of reports
@app.route('/reports')
def reports():
    reports = mongo.db.reports.find()
    offers = mongo.db.offers.find()
    return render_template("reports.html", reports=reports, offer=offers)


# report details
@app.route('/report_detail/<report_id>')
def report_detail(report_id):
    report = mongo.db.reports.find_one({"_id": ObjectId(report_id)})
    offer = mongo.db.offers.find_one({"_id": ObjectId(report['offer_id'])})
    report_detail = {
        'report': report,
        'user': mongo.db.users.find_one({"username": offer['created_by']}),
        'offer': offer
    }
    return render_template("report_detail.html", report=report_detail)


# show all categories of fruits
@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.fruit_categories.find().sort(
        "category_fruits", 1))
    return render_template("get_categories.html", categories=categories)


# add a new category
@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_fruits": request.form.get("category_fruits")
        }
        mongo.db.fruit_categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))
    return render_template("add_category.html")


# edit category
@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_fruits": request.form.get("category_fruits")
        }
        mongo.db.fruit_categories.update(
            {"_id": ObjectId(category_id)}, submit)
        flash("Category Successfully Updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.fruit_categories.find_one(
        {"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


# delete category
@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.fruit_categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))


# error page 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template("error/404.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
