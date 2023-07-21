import pickle
from classes.FakeMailBox import FakeMailBox
from classes.FakePerson import FakePerson
from reddit_account import create_account

USERS_COUNT = 2  # 100000

created_user_count = 0
while created_user_count < USERS_COUNT:
    print(f"Creating user {created_user_count}")
    person = FakePerson()
    mailbox = FakeMailBox(person)

    # Attach mailbox to user
    person.mailbox = mailbox
    res = create_account(person, headless=False)
    if res:
        with open(f"user-{created_user_count}", "wb") as f:
            pickle.dump(person, f)
        created_user_count += 1
    # Find a way to store this user globally
