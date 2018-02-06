from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_config import Base, Category, CategoryItem, User

engine = create_engine('sqlite:///Catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

id_1 = 1
id_2 = 2
id_3 = 3

category_1 = Category(name="Soccer", id=1, user_id=1)
session.add(category_1)
session.commit()
category_2 = Category(name="Skiing", id=2, user_id=2)
session.add(category_2)
session.commit()
category_3 = Category(name="BasketBall", id=3, user_id=3)
session.add(category_3)
session.commit()

user_1 = User(id=1, name="muataz", email="muataz.gouda@gmail.com", hashed_password="icandoit")
session.add(user_1)
session.commit()
user_2 = User(id=2, name="ahmed", email="ahmed_123@gmail.com", hashed_password="iloveudacity")
session.add(user_2)
session.commit()

user_3 = User(id=3, name="mustafa", email="mustafa.abdullah@hotmail.com", hashed_password="whyme?")
session.add(user_3)
session.commit()
user_4 = User(id=4, name="Karim", email="karim.w@gmail.com", hashed_password="fullstacknanodegree")
session.add(user_4)
session.commit()

cat_item_1 = CategoryItem(id=1, name="soccer cleats", description="soccer shoes for soccer players", cat_name=category_1.name)
session.add(cat_item_1)
session.commit()
cat_item_2 = CategoryItem(id=2, name="soccer ball", description="soccer ball size 5", cat_name=category_1.name)
session.add(cat_item_2)
session.commit()
cat_item_3 = CategoryItem(id=3, name="BasketBall ball", description="Basketball ball", cat_name=category_3.name)
session.add(cat_item_3)
session.commit()
cat_item_4 = CategoryItem(id=4, name="skiing shoes", description="skiing shoes for skiing", cat_name=category_2.name)
session.add(cat_item_4)
session.commit()
cat_item_5 = CategoryItem(id=5, name="shinguards", description="shinguards for protecting players legs from tough clashes", cat_name=category_1.name)
session.add(cat_item_5)
session.commit()
cat_item_6 = CategoryItem(id=6, name="BasketBall shoes", description="basketball shoes", cat_name=category_3.name)
session.add(cat_item_6)
session.commit()

cat_item_7 = CategoryItem(id=7, name="goalkeeper gloves", description="gloves for goalkeepers", cat_name=category_1.name)
session.add(cat_item_7)
session.commit()

print("data has been inserted successfully")
