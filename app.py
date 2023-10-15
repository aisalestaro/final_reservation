
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
from flask_mail import Mail, Message
from config import Inventory 
from datetime import datetime, date, timedelta
from calendar import monthrange
import calendar



app = Flask(__name__, static_folder="./templates/images")

app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'zituyuu777@gmail.com'  
app.config['MAIL_PASSWORD'] = 'tsft oyqa bjlo dsan'  
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

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


@app.route("/reservation_history", methods=["GET", "POST"])
@login_required
def reservation_history():
    user_id = current_user.id
    reservations = Reservation.select().where(Reservation.user_id == user_id)
    return render_template("reservation_history.html", reservations=reservations)



def make_reservation():
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
        
        # メール送信
        msg = Message('予約完了のお知らせ', sender='your_email@gmail.com', recipients=[email])
        msg.body = f"""
    【予約詳細】
        部屋タイプ: {room_type}
        チェックイン日: {check_in_date}
        チェックアウト日: {check_out_date}
        滞在日数: {number_of_stays}
        男性ゲスト数: {male_guests if male_guests else 'None'}
        女性ゲスト数: {female_guests if female_guests else 'None'}
        ゲスト名: {guest_name if guest_name else 'None'}
        メールアドレス: {email if email else 'None'}
        電話番号: {phone_number if phone_number else 'None'}
        住所: {address if address else 'None'}
        チェックイン時間: {check_in_time if check_in_time else 'None'}
        備考: {remarks if remarks else 'None'}
        """
        mail.send(msg)
        
        return redirect(url_for("mypage"))
    except IntegrityError as e:
        print(f"Debug: Exception caught: {e}")
        flash(f"予約に失敗しました: {str(e)}")
        return redirect(url_for("reservation"))




def get_month_data(year, month):
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = datetime(year, month + 1, 1) - timedelta(days=1)
    day = first_day_of_month
    month_data = []
    week_data = []
    day_offset = day.weekday()  # 0: Monday, 1: Tuesday, ..., 6: Sunday
    week_data.extend([None] * day_offset)  # Padding days before the first day of the month

    while day <= last_day_of_month:
        week_data.append({
            'date': day,
            'available': day.weekday() not in [5, 6]  # Assume unavailable on weekends for example
        })
        if day.weekday() == 6:  # Sunday
            month_data.append(week_data)
            week_data = []
        day += timedelta(days=1)

    if week_data:  # If the last week is not complete
        week_data.extend([None] * (7 - len(week_data)))  # Padding days after the last day of the month
        month_data.append(week_data)

    return month_data


def send_cancelation_notification(email, room_type, check_in_date, check_out_date):
    msg = Message('予約キャンセルのお知らせ', sender='your_email@gmail.com', recipients=[email])
    msg.body = f"""
    【キャンセル詳細】
        部屋タイプ: {room_type}
        チェックイン日: {check_in_date}
        チェックアウト日: {check_out_date}
        """    
    mail.send(msg)


@app.route("/reservation", methods=["GET", "POST"])
@login_required
def reservation():
    if request.method == "POST":
        return make_reservation()

    year = request.args.get('year', type=int, default=datetime.now().year)
    month = request.args.get('month', type=int, default=datetime.now().month)
    month_data = get_month_data(year, month)
    prev_month = (month - 1) % 12 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = (month + 1) % 12 or 12
    next_year = year + 1 if month == 12 else year

    month_name_jp = f'{month}月({year}年)'
    days_label_jp = ['月', '火', '水', '木', '金', '土', '日']

    availability_message = ''
    check_in_date = request.args.get('check_in_date')
    check_out_date = request.args.get('check_out_date')
    if check_in_date and check_out_date:
        # ここで在庫を確認するロジックを実装します。
        # この例では単純化のために常に在庫があると仮定しています。
        available = True  
        if not available:
            availability_message = '予約不可の日程です。'

    return render_template(
        'reservation.html',
        month=month_data,
        current_month_label=month_name_jp,
        prev_month_label=f'＜前月　{prev_month}月({prev_year}年)　翌月＞',
        next_month_label=f'＜前月　{next_month}月({next_year}年)　翌月＞',
        prev_month=f'{prev_year}-{prev_month:02d}',
        next_month=f'{next_year}-{next_month:02d}',
        days_label=days_label_jp,
        availability_message=availability_message
    )



@app.route("/cancel_reservation/<int:reservation_id>", methods=["POST"])
@login_required
def cancel_reservation(reservation_id):
    try:
        reservation = Reservation.get(id=reservation_id, user=current_user.id)
        send_cancelation_notification(
            reservation.email,
            reservation.room_type,
            reservation.check_in_date,
            reservation.check_out_date
        )
        reservation.delete_instance()
        flash("予約がキャンセルされました")
    except Reservation.DoesNotExist:
        flash("予約が見つかりません")
    return redirect(url_for("reservation_history"))



@app.route("/company", methods=["GET", "POST"])
def company():
    return render_template("company.html")



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
