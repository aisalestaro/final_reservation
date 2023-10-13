
import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import IntegrityError
from config import User
from config import User, Reservation
from datetime import datetime, timedelta
from flask import flash, redirect, url_for
from peewee import IntegrityError
from datetime import datetime


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


@app.route("/logout", methods=["POST"])
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
    user_id = current_user.id
    reservations = Reservation.select().where(Reservation.user_id == user_id)
    return render_template("reservation_history.html", reservations=reservations)



def make_reservation():
    # 現在ログインしているユーザーのIDを取得
    user_id = current_user.id
    room_type = request.form["room_type"]
    check_in_date = request.form.get("check_in_date")
    check_out_date = request.form.get("check_out_date")
    male_guests = request.form.get("male_guests")
    female_guests = request.form.get("female_guests")
    guest_name = request.form.get("guest_name")
    email = request.form.get("email")
    phone_number = request.form.get("phone_number")
    address = request.form.get("address")
    check_in_time = request.form.get("check_in_time", "00:00") 
    remarks = request.form.get("remarks", "なし")
    
    try:
        number_of_stays = (datetime.strptime(check_out_date, '%Y-%m-%d') - datetime.strptime(check_in_date, '%Y-%m-%d')).days
    except ValueError:
        flash("日付の形式が正しくありません")
        return redirect(url_for("reservation"))

    try:
        # データベースに保存
        Reservation.create(
            user=current_user.id,
            room_type=room_type,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            number_of_stays=number_of_stays,
            male_guests=int(male_guests) if male_guests else None,
            female_guests=int(female_guests) if female_guests else None,
            guest_name=guest_name if guest_name else None,
            email=email if email else None,
            phone_number=phone_number if phone_number else None,
            address=address if address else None,
            check_in_time=check_in_time if check_in_time else None,
            remarks=remarks if remarks else None,
            pub_date=datetime.now()
        )
        flash("予約が完了しました!")
        return redirect(url_for("mypage"))

    except IntegrityError as e:
        print(f"Debug: Exception caught: {e}") 
        flash(f"予約に失敗しました: {str(e)}")
        return redirect(url_for("reservation"))


@app.route("/reservation", methods=["GET", "POST"])
@login_required
def reservation():
    if request.method == "POST":
        return make_reservation()
    return render_template("reservation.html")



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)