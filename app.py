
import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import IntegrityError
from config import User
from config import User, Reservation

app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(id=int(user_id))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for("login"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST" and request.form["名前"] and request.form['パスワード'] and request.form["メールアドレス"]:
        print("aaa")
        if User.select().where(User.name == request.form["名前"]).first():
            flash("その名前はすでに使われています")
            return redirect(request.url)

        if User.select().where(User.email == request.form["メールアドレス"]).first():
            flash("そのメールアドレスはすでに使われています")
            return redirect(request.url)

        try:
            user = User.create(
                name=request.form["名前"],
                email=request.form["メールアドレス"],
                password=generate_password_hash(request.form["パスワード"]),
            )
            login_user(user)
            flash(f"ようこそ！ {user.name} さん")
            return redirect(url_for("index"))
        except IntegrityError:
            flash("登録に失敗しました")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    logged_in = request.method
    if request.method == "POST" and "メールアドレス" in request.form and "パスワード" in request.form:

        user = User.select().where(User.email == request.form["メールアドレス"]).first()
        print("a")
        if user and check_password_hash(user.password, request.form["パスワード"]):
            login_user(user)
            flash(f"ようこそ！ {user.name} さん")
            return redirect(url_for("mypage"))
        else:
            flash("認証に失敗しました")
    print(request.form)
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトしました！")
    return redirect(url_for("index"))


@app.route("/mypage", methods=["GET", "POST"])
@login_required
def mypage():
    return render_template("mypage.html")


@app.route("/check_availability", methods=["GET", "POST"])
@login_required
def check_availability():
    return render_template("check_availability.html")


@app.route("/reservation_history", methods=["GET", "POST"])
@login_required
def reservation_history():
    return render_template("reservation_history.html")


@app.route("/reservation", methods=["GET", "POST"])
@login_required
def reservation():
    if request.method == "POST":
        return make_reservation()
    return render_template("reservation.html")


def make_reservation():
    room_type = request.form["room_type"]
    check_in_date = request.form["check_in_date"]
    check_out_date = request.form["check_out_date"]
    male_guests = request.form.get("male_guests", 0)
    female_guests = request.form.get("female_guests", 0)
    guest_name = request.form.get("guest_name", "デフォルト値")
    address = request.form.get("address", "デフォルト値")
    email = request.form.get("email", "デフォルト値")
    phone_number = request.form.get("phone_number", "デフォルト値")
    check_in_time = request.form.get("pcheck_in_time", "デフォルト値")
    remarks = request.form.get("remarks", "デフォルト値")


    Reservation.create(
        room_type=room_type,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        number_of_stays=number_of_stays,
        male_guests=int(male_guests),
        female_guests=int(female_guests),
        guest_name=guest_name,
        address=address,
        email=email,
        phone_number=phone_number,
        check_in_time=check_in_time,
        remarks=remarks,
        pub_date=datetime.now()  # 今の日時を保存
    )
    flash("予約が完了しました!")
    return redirect(url_for("mypage"))



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)