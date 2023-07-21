import pickle
from classes import FakeMailBox, FakePerson, Reddit
from utils import get_logger


logger = get_logger(__name__)
USERS_COUNT = 2  # 100000

created_user_count = 0
while created_user_count < USERS_COUNT:
    logger.info(f"Creating user #{created_user_count+1}")
    person = FakePerson()
    mailbox = FakeMailBox(person)
    # Attach mailbox to user
    person.mailbox = mailbox

    reddit_bot = Reddit(person, headless=False)
    res = reddit_bot.create_account()

    if res:
        with open(f"user-{created_user_count}", "wb") as f:
            pickle.dump(person, f)
        created_user_count += 1
    # Find a way to store this user globally
