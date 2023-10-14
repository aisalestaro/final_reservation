import os
import datetime
import logging
from dotenv import load_dotenv
from playhouse.db_url import connect
from peewee import Model, IntegerField, CharField, TextField, TimestampField, DateField, ForeignKeyField, AutoField, DateTimeField
from flask_login import UserMixin

load_dotenv()

# 実行したSQLをログで出力する設定
logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

db = connect(os.environ.get("DATABASE", "sqlite:///db.sqlite"))

if not db.connect():
    print("接続NG")
    exit()


class User(Model, UserMixin):
    class Meta:
        database = db
    id = IntegerField(primary_key=True)
    name = CharField()
    email = CharField(unique=True)
    password = CharField()
    join_date = DateTimeField(default=datetime.datetime.now)


class Reservation(Model):
    class Meta:
        database = db
    id = AutoField()
    user = ForeignKeyField(User, backref='reservations')
    guest_name = CharField()
    address = TextField()
    email = CharField()
    male_guests = IntegerField()
    female_guests = IntegerField()
    phone_number = CharField()
    room_type = CharField(default='Double Room')  
    check_in_date = DateField()
    check_out_date = DateField()
    number_of_stays = IntegerField()
    check_in_time = CharField(null=True) 
    remarks = TextField()
    pub_date = DateTimeField()


class Inventory(Model):
    class Meta:
        database = db
    date = DateField(unique=True)
    available_rooms = IntegerField(default=10) 


db.create_tables([Inventory])
db.create_tables([User])
db.create_tables([Reservation])