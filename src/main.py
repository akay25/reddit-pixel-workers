from classes.FakeMailBox import FakeMailBox
from classes.FakePerson import FakePerson
from reddit_account import create_account

USERS_COUNT = 100000

for i in range(USERS_COUNT):
    print(f"Creating user {i}")
    person = FakePerson()
    mailbox = FakeMailBox(person)

    # Attach mailbox to user
    person.mailbox = mailbox
    create_account(person, headless=False)
