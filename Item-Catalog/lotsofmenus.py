# coding: utf-8
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Library, Base, MenuItem, User

engine = create_engine('sqlite:///librarymenuwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com")
session.add(User1)
session.commit()

# Menu for UrbanBurger
library1 = Library(user_id=1, name="Kids Books")

session.add(library1)
session.commit()

menuItem2 = MenuItem(user_id=1, name="Amelia Bedelia",
                     description="The queen of idioms",
                     price="$17.50", course="Short Story", library=library1)

session.add(menuItem2)
session.commit()

menuItem1 = MenuItem(user_id=1, name="The Travel",
                     description="Travel to a strange new land.",
                     price="$22.99", course="Novels Story", library=library1)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, name="Bark George",
                     description="He meows,why can’t George the dog bark?",
                     price="$15.50", course="Short Story", library=library1)

session.add(menuItem2)
session.commit()

menuItem3 = MenuItem(user_id=1, name="Ben's Trumprt",
                     description="The syncopated rhythms of Harlem",
                     price="$13.99", course="Long Story", library=library1)

session.add(menuItem3)
session.commit()

menuItem4 = MenuItem(user_id=1, name="Big Red Lolipop",
                     description="Little sisters can be such a pain.",
                     price="$7.99", course="Novels Story", library=library1)

session.add(menuItem4)
session.commit()

menuItem5 = MenuItem(user_id=1, name="The Birchark House",
                     description="Fascinating details of traditionals",
                     price="$19.99", course="Long Story", library=library1)

session.add(menuItem5)
session.commit()

menuItem6 = MenuItem(user_id=1, name="The Borrwers",
                     description="the miniature people",
                     price="$29.99", course="Long Story", library=library1)

session.add(menuItem6)
session.commit()

menuItem7 = MenuItem(user_id=1, name="Chains",
                     description="Tory family in New York City",
                     price="$13.49", course="Short Sory", library=library1)

session.add(menuItem7)
session.commit()

menuItem8 = MenuItem(user_id=1, name="FreightTrain",
                     description="train ride with bold colors galore!",
                     price="$5.99", course="Long Story", library=library1)

session.add(menuItem8)
session.commit()


# Menu for Super Stir Fry
library2 = Library(user_id=1, name="Science BookS")

session.add(library2)
session.commit()


menuItem1 = MenuItem(user_id=1, name="A Short History of Nearly Everything",
                     description="Bill Bryson the greatest scientific.",
                     price="$47.99", course="Short Story", library=library2)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, name="101 Great Science Experiments",
                     description="give plenty of ideas for next experiment",
                     price="$25", course="Long Story", library=library2)

session.add(menuItem2)
session.commit()

menuItem3 = MenuItem(user_id=1, name="The Gene: An Intimate History",
                     description="shows us how gene research began",
                     price="15", course="Novels Story", library=library2)

session.add(menuItem3)
session.commit()

menuItem4 = MenuItem(user_id=1, name="A Brief History of Time ",
                     description="Time is one of biggest scientific.",
                     price="71", course="Long Story", library=library2)

session.add(menuItem4)
session.commit()

menuItem5 = MenuItem(user_id=1, name="Knowledge Encyclopedia",
                     description="It is a celebration of science.",
                     price="50.99", course="Long Story", library=library2)

session.add(menuItem5)
session.commit()

menuItem6 = MenuItem(user_id=1, name="My First Human Body Book",
                     description="Human body is home of scientific procedures",
                     price="80.99", course="Long Story", library=library2)

session.add(menuItem6)
session.commit()


# Menu for Panda Garden
library3 = Library(user_id=1, name="Personal Development Books")

session.add(library3)
session.commit()


menuItem1 = MenuItem(user_id=1, name="Think and Grow Rich",
                     description="about achieving success written80_year_ago",
                     price="$88.99", course="Long Story", library=library3)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, name="The Power of Positive Thinking",
                     description="Positive thinking will make success happen",
                     price="$60.99", course="Short Story", library=library3)

session.add(menuItem2)
session.commit()

menuItem3 = MenuItem(user_id=1, name="Outliers The Story of Success",
                     description="Outliers scientific to achieve success",
                     price="$39.95", course="Novels Story", library=library3)

session.add(menuItem3)
session.commit()

menuItem4 = MenuItem(user_id=1, name="The Power of Full Egagement",
                     description="Everyone thinks time is the enemy.",
                     price="$66.99", course="Short Story", library=library3)

session.add(menuItem4)
session.commit()

menuItem5 = MenuItem(user_id=1, name="Let Go",
                     description="Let Go! is Pat Flynn’s inspiring story.",
                     price="$79.50", course="Short Story", library=library3)

session.add(menuItem5)
session.commit()

print "added menu items!"
