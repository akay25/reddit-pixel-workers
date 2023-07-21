from classes.FakePerson import FakePerson
import re
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from random import randint, sample
from bs4 import BeautifulSoup
import time
from utils import get_logger

MAX_INTERESTS_TO_SELECT = 7


def sleep_randomly(min_time: int = 1, max_time: int = 5):
    if max_time < min_time:
        max_time = min_time + 5
    time.sleep(randint(min_time, max_time))


def is_duplicate_username(driver):
    error_message_elements = driver.find_elements(
        By.CLASS_NAME, "AnimatedForm__errorMessage"
    )

    for error_message_element in error_message_elements:
        if error_message_element.text == "That username is already taken":
            return True
    return False


def check_for_submit_rate_limit(driver):
    submit_status_element = None
    try:
        submit_status_element = driver.find_element(
            By.CSS_SELECTOR,
            "div.AnimatedForm__bottomNav > span > span.AnimatedForm__submitStatusMessage",
        )
    except Exception as e:
        return False
    if submit_status_element:
        if "Looks like you've been doing that a lot" in submit_status_element.text:
            return True

    return False


def get_email_verification_link(person: FakePerson, max_retries=10):
    try_count = 0
    while try_count < max_retries:
        try_count += 1
        sleep_randomly(10, 20)
        messages = person.mailbox.get_messages()
        if len(messages) > 0:
            for message in messages:
                if message.subject == "Verify your Reddit email address":
                    soup = BeautifulSoup(message.html_body, "lxml")

                    anchors = soup.find_all("a")
                    for anchor in anchors:
                        if anchor.text == "Verify Email Address":
                            return anchor.attrs["href"]
    return None


def select_gender_for_user(driver, person_sex):
    if person_sex == "F":
        gender_element = driver.find_element(By.CSS_SELECTOR, "input[value=FEMALE]")
    else:
        # Find male
        gender_element = driver.find_element(By.CSS_SELECTOR, "input[value=MALE]")

    gender_element.click()
    sleep_randomly(1, 4)
    # No need to press continue here


def find_continue_button(driver):
    dialog_div = driver.find_element(
        By.CSS_SELECTOR, "#SHORTCUT_FOCUSABLE_DIV > div.dialog"
    )

    continue_button = None
    child_divs = dialog_div.find_elements(By.TAG_NAME, "div")
    for child_div in child_divs:
        button_elements = child_div.find_elements(By.TAG_NAME, "button")
        if len(button_elements) == 1:
            button_element = button_elements[0]
            if "continue" in button_element.text.lower():
                continue_button = button_elements[0]
                break
    return continue_button


def select_random_interests_for_user(driver, max_interests=MAX_INTERESTS_TO_SELECT):
    interests_buttons_elements = driver.find_elements(
        By.XPATH,
        '//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[4]/div/div/div/div[1]/div/button',
    )
    selected_button_elements = sample(interests_buttons_elements, max_interests)

    selected_interests = []
    for interest_button_element in selected_button_elements:
        selected_interests.append(
            interest_button_element.text or interest_button_element.accessible_name
        )
        driver.execute_script("arguments[0].scrollIntoView();", interest_button_element)
        interest_button_element.click()
        sleep_randomly(1, 2)

    continue_button = find_continue_button(driver)
    continue_button.click()
    sleep_randomly(4, 8)

    return selected_interests


def select_all_given_subreddits(driver):
    subreddit_join_buttons = driver.find_elements(
        By.XPATH, "//button[contains(text(), 'My Button')]"
    )

    for button in subreddit_join_buttons:
        button.click()
        sleep_randomly(1, 2)


def continue_with_language(driver):
    continue_button = find_continue_button(driver)
    continue_button.click()
    sleep_randomly(4, 8)


def create_account(person: FakePerson, headless=True) -> bool:
    logger = get_logger("create_account")

    driver = uc.Chrome(headless=headless, use_subprocess=False)
    try:
        logger.info(
            f"Creating account with username: {person.username} and password: {person.password}..."
        )

        logger.debug("Setting up anonymous web identity...")
        driver.get("https://www.reddit.com/register/")
        sleep_randomly()

        logger.debug("Entering email...")
        driver.find_element(By.ID, "regEmail").send_keys(person.email)
        sleep_randomly()

        logger.debug("Submitting email step")
        email_submit_button = driver.find_element(
            By.CSS_SELECTOR,
            "div.Step__content > form > fieldset.AnimatedForm__field.m-small-margin > button",
        )
        email_submit_button.click()
        sleep_randomly()

        while True:
            person.username = person.username + str(randint(0, 9))
            logger.debug("Entering in username...")
            driver.find_element(By.ID, "regUsername").click()
            driver.find_element(By.ID, "regUsername").send_keys(person.username)
            sleep_randomly()

            if not is_duplicate_username(driver):
                break

        logger.debug("Entering in password...")
        driver.find_element(By.ID, "regPassword").send_keys(person.password)
        sleep_randomly()

        # TODO: Solve captcha

        logger.debug("Submitting token")
        driver.find_element(
            By.CSS_SELECTOR, "div.AnimatedForm__bottomNav > button"
        ).click()
        sleep_randomly(1, 5)

        if check_for_submit_rate_limit(driver):
            logger.info("Sleeping for 10 mins")
            sleep_randomly(600, 1000)
            driver.find_element(
                By.CSS_SELECTOR, "div.AnimatedForm__bottomNav > button"
            ).click()

        # Wait for page redirection and pop-up for gender selection
        sleep_randomly(10, 20)
        select_gender_for_user(driver, person.sex)
        person.interests = select_random_interests_for_user(driver)

        select_all_given_subreddits(driver)

        # Email confirmation
        logger.info("Checking email...")
        email_verification_link = get_email_verification_link(person)

        assert email_verification_link is not None, "Email verification link not found"
        logger.info("Verifying email...")
        driver.get(email_verification_link)
        sleep_randomly()
        logger.info("Successfully created account!")
        driver.close()
        return
    except Exception as e:
        logger.error(f"Error. Trying again...{e}")
        driver.close()
        time.sleep(120)
        create_account(person)
        return
