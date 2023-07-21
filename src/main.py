from classes.FakeMailBox import FakeMailBox
from classes.FakePerson import FakePerson
from reddit_account import create_account, get_email_verification_link

person = FakePerson()
mailbox = FakeMailBox(person)

# Attach mailbox to user
person.mailbox = mailbox


create_account(person, headless=False)
