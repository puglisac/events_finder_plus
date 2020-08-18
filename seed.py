from app import app
from models import db, User

db.drop_all()
db.create_all()

user = User.register(email="alan.c.puglisi@gmail.com", pwd="password",
                     first="Alan", last="Puglisi", loc="Nashville, TN")
db.session.add(user)
db.session.commit()
