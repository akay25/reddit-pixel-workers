from classes.FakePerson import FakePerson
import re
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from random import randint
from bs4 import BeautifulSoup
import time
from utils import get_logger


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


def get_email_verification_link(person: FakePerson):
    while True:
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


def make_graphql_request_to_reddit(driver, data):
    cookies = driver.get_cookies()
    # Capture cookies for request usage
    headers = {
        "authority": "gql.reddit.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNjg5OTc5OTU4LjkyODUyNiwiaWF0IjoxNjg5ODkzNTU4LjkyODUyNiwianRpIjoiUXM5dXRMTzRnVnJveDJzcV96ZDVoZ29JbGs2NkJnIiwiY2lkIjoiOXRMb0Ywc29wNVJKZ0EiLCJsaWQiOiJ0Ml9mdzJxN2ZtdG4iLCJhaWQiOiJ0Ml9mdzJxN2ZtdG4iLCJsY2EiOjE2ODk4OTM1MTc2MzgsInNjcCI6ImVKeGtrZEdPOUNBSWhkLUZhNV9nZjVVX200MVZPa05XcFFIc1pONS1ZeXVkSm52VkEtZFQ0ZlFfWUkxVUlNQkdCQUZpU3R5YlFZQWttRE9aUWdETU5EcHJpU1FRNEVscUxHOElRQm1ia1ExWmFNY2FXM3dnQktpY0U3ZVZIcGMyb2FVYmk1NGR2NnB5TGp5cE9VZmwzTmptTFd4UDlETWJxMDJwV05aVG1jUjFwWFFXTF9vWk85UzM5dVV6X1NhMFI4T0txdkdCb3lNWThfSFpXTVppR3ZmeG5wcjBaRjB3cTczTFFXcGY2ckc3OWtXVDBESzRfUnh2dkRhVEdYSmVtcDdSX3QzMVMtakFQY19MOU5xQkdhdjdYcnJ0V2J0XzFRNVV6aWpSV0p6NE5CeTVjdmtldndUYk5lbGY0M1prTEw0WmNkTWJmbXM2T25KeDR0Q244ZlViQUFEX18xOFMyRkUiLCJyY2lkIjoiWGhFODI5UVBodzNkZzd2bl9TWGxkby1Hazl5Y2tuS2hGS2tlZUx2d0RXSSIsImZsbyI6Mn0.emoe7NLn_ROiCSwZXqDTl1WZN8T2j3sXugzKtzmwdkNom5XPkU0CUibWZwYpfQ6l41lCcTt-GbFrXXG7PVlDHIveXjeXV5RNORR3iXLbT0RQXGiThgh1uzMKj9fbirtmKPn6f93DoPHdJWtZffMlH25qil8TlFRYmhZisRUCZJ88lk-luxd_vsqg4HTzpFnyql4ZlE9pv9KZEFuUCtx0u2ew0MSqlbM44k1AEAFCTxNwHTh_i2dhYy-cX-IIVjL9y3q35hjKhnuqblTDbRNq9Y2c4NvqNSp8qJFarCC7GwsfNaAh0FqS7wPIakauchTulpsyzgXIDUlvSkgJwx--tA",
        "content-type": "application/json",
        "origin": "https://www.reddit.com",
        "referer": "https://www.reddit.com/",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "x-reddit-compression": "1",
        "x-reddit-loid": "000000000fw2q7fmtn.2.1689893517638.Z0FBQUFBQmt1YnFOMzJfZEVpOFpIRmJaNjRBRjdxTVNsSUYxbER6MWg2ZnAzWG95c243cXJ3N3ExNU80aWJMTnhDeG1jX29tYXBUSmdEMHBnbTRvcTlKV0xDZXJyalZGWFoyc0NfLVI4dTFXTmtBSDhEZm11aXEycEY0b3JMQTV2alExWEhQR0NXenA",
        "x-reddit-session": "nmnmgrprglbelnogra.0.1689893568985.Z0FBQUFBQmt1YnJCY1gyNHF1M3lWdEwxWEhBVl9GM05ISVhwTmRRWjZLTTh5R29fQ2NVc0UwNXAzSTNKeFM3MDFKTW8tanZjY3Fzbi1leERLejZtczZFYlFPekxYdVNDZ2s4c2Rza3lXOEh1VlRfeWNMSUhfS1JBbjQ2SFIzTUw4bnFBMWpSWXVqOTI",
    }

    return requests.post("https://gql.reddit.com/", headers=headers, json=json_data)


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
        make_graphql_request_to_reddit(driver, {})

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
        sleep_randomly(10, 20)

        # Request for updating gender
        #         curl 'https://gql.reddit.com/' \
        #   -H 'authority: gql.reddit.com' \
        #   -H 'accept: */*' \
        #   -H 'accept-language: en-US,en;q=0.9' \
        #   -H 'authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNjg5OTc5OTU4LjkyODUyNiwiaWF0IjoxNjg5ODkzNTU4LjkyODUyNiwianRpIjoiUXM5dXRMTzRnVnJveDJzcV96ZDVoZ29JbGs2NkJnIiwiY2lkIjoiOXRMb0Ywc29wNVJKZ0EiLCJsaWQiOiJ0Ml9mdzJxN2ZtdG4iLCJhaWQiOiJ0Ml9mdzJxN2ZtdG4iLCJsY2EiOjE2ODk4OTM1MTc2MzgsInNjcCI6ImVKeGtrZEdPOUNBSWhkLUZhNV9nZjVVX200MVZPa05XcFFIc1pONS1ZeXVkSm52VkEtZFQ0ZlFfWUkxVUlNQkdCQUZpU3R5YlFZQWttRE9aUWdETU5EcHJpU1FRNEVscUxHOElRQm1ia1ExWmFNY2FXM3dnQktpY0U3ZVZIcGMyb2FVYmk1NGR2NnB5TGp5cE9VZmwzTmptTFd4UDlETWJxMDJwV05aVG1jUjFwWFFXTF9vWk85UzM5dVV6X1NhMFI4T0txdkdCb3lNWThfSFpXTVppR3ZmeG5wcjBaRjB3cTczTFFXcGY2ckc3OWtXVDBESzRfUnh2dkRhVEdYSmVtcDdSX3QzMVMtakFQY19MOU5xQkdhdjdYcnJ0V2J0XzFRNVV6aWpSV0p6NE5CeTVjdmtldndUYk5lbGY0M1prTEw0WmNkTWJmbXM2T25KeDR0Q244ZlViQUFEX18xOFMyRkUiLCJyY2lkIjoiWGhFODI5UVBodzNkZzd2bl9TWGxkby1Hazl5Y2tuS2hGS2tlZUx2d0RXSSIsImZsbyI6Mn0.emoe7NLn_ROiCSwZXqDTl1WZN8T2j3sXugzKtzmwdkNom5XPkU0CUibWZwYpfQ6l41lCcTt-GbFrXXG7PVlDHIveXjeXV5RNORR3iXLbT0RQXGiThgh1uzMKj9fbirtmKPn6f93DoPHdJWtZffMlH25qil8TlFRYmhZisRUCZJ88lk-luxd_vsqg4HTzpFnyql4ZlE9pv9KZEFuUCtx0u2ew0MSqlbM44k1AEAFCTxNwHTh_i2dhYy-cX-IIVjL9y3q35hjKhnuqblTDbRNq9Y2c4NvqNSp8qJFarCC7GwsfNaAh0FqS7wPIakauchTulpsyzgXIDUlvSkgJwx--tA' \
        #   -H 'content-type: application/json' \
        #   -H 'origin: https://www.reddit.com' \
        #   -H 'referer: https://www.reddit.com/' \
        #   -H 'sec-ch-ua: "Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"' \
        #   -H 'sec-ch-ua-mobile: ?0' \
        #   -H 'sec-ch-ua-platform: "Linux"' \
        #   -H 'sec-fetch-dest: empty' \
        #   -H 'sec-fetch-mode: cors' \
        #   -H 'sec-fetch-site: same-site' \
        #   -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36' \
        #   -H 'x-reddit-compression: 1' \
        #   -H 'x-reddit-loid: 000000000fw2q7fmtn.2.1689893517638.Z0FBQUFBQmt1YnFOMzJfZEVpOFpIRmJaNjRBRjdxTVNsSUYxbER6MWg2ZnAzWG95c243cXJ3N3ExNU80aWJMTnhDeG1jX29tYXBUSmdEMHBnbTRvcTlKV0xDZXJyalZGWFoyc0NfLVI4dTFXTmtBSDhEZm11aXEycEY0b3JMQTV2alExWEhQR0NXenA' \
        #   -H 'x-reddit-session: nmnmgrprglbelnogra.0.1689893568985.Z0FBQUFBQmt1YnJCY1gyNHF1M3lWdEwxWEhBVl9GM05ISVhwTmRRWjZLTTh5R29fQ2NVc0UwNXAzSTNKeFM3MDFKTW8tanZjY3Fzbi1leERLejZtczZFYlFPekxYdVNDZ2s4c2Rza3lXOEh1VlRfeWNMSUhfS1JBbjQ2SFIzTUw4bnFBMWpSWXVqOTI' \
        #   --data-raw '{"id":"670e8e8d3018","variables":{"input":{"customGender":null,"genderEnum":"FEMALE"}}}' \
        #   --compressed

        # Update interests
        #         curl 'https://gql.reddit.com/' \
        #   -H 'authority: gql.reddit.com' \
        #   -H 'accept: */*' \
        #   -H 'accept-language: en-US,en;q=0.9' \
        #   -H 'authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNjg5OTc5OTU4LjkyODUyNiwiaWF0IjoxNjg5ODkzNTU4LjkyODUyNiwianRpIjoiUXM5dXRMTzRnVnJveDJzcV96ZDVoZ29JbGs2NkJnIiwiY2lkIjoiOXRMb0Ywc29wNVJKZ0EiLCJsaWQiOiJ0Ml9mdzJxN2ZtdG4iLCJhaWQiOiJ0Ml9mdzJxN2ZtdG4iLCJsY2EiOjE2ODk4OTM1MTc2MzgsInNjcCI6ImVKeGtrZEdPOUNBSWhkLUZhNV9nZjVVX200MVZPa05XcFFIc1pONS1ZeXVkSm52VkEtZFQ0ZlFfWUkxVUlNQkdCQUZpU3R5YlFZQWttRE9aUWdETU5EcHJpU1FRNEVscUxHOElRQm1ia1ExWmFNY2FXM3dnQktpY0U3ZVZIcGMyb2FVYmk1NGR2NnB5TGp5cE9VZmwzTmptTFd4UDlETWJxMDJwV05aVG1jUjFwWFFXTF9vWk85UzM5dVV6X1NhMFI4T0txdkdCb3lNWThfSFpXTVppR3ZmeG5wcjBaRjB3cTczTFFXcGY2ckc3OWtXVDBESzRfUnh2dkRhVEdYSmVtcDdSX3QzMVMtakFQY19MOU5xQkdhdjdYcnJ0V2J0XzFRNVV6aWpSV0p6NE5CeTVjdmtldndUYk5lbGY0M1prTEw0WmNkTWJmbXM2T25KeDR0Q244ZlViQUFEX18xOFMyRkUiLCJyY2lkIjoiWGhFODI5UVBodzNkZzd2bl9TWGxkby1Hazl5Y2tuS2hGS2tlZUx2d0RXSSIsImZsbyI6Mn0.emoe7NLn_ROiCSwZXqDTl1WZN8T2j3sXugzKtzmwdkNom5XPkU0CUibWZwYpfQ6l41lCcTt-GbFrXXG7PVlDHIveXjeXV5RNORR3iXLbT0RQXGiThgh1uzMKj9fbirtmKPn6f93DoPHdJWtZffMlH25qil8TlFRYmhZisRUCZJ88lk-luxd_vsqg4HTzpFnyql4ZlE9pv9KZEFuUCtx0u2ew0MSqlbM44k1AEAFCTxNwHTh_i2dhYy-cX-IIVjL9y3q35hjKhnuqblTDbRNq9Y2c4NvqNSp8qJFarCC7GwsfNaAh0FqS7wPIakauchTulpsyzgXIDUlvSkgJwx--tA' \
        #   -H 'content-type: application/json' \
        #   -H 'origin: https://www.reddit.com' \
        #   -H 'referer: https://www.reddit.com/' \
        #   -H 'sec-ch-ua: "Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"' \
        #   -H 'sec-ch-ua-mobile: ?0' \
        #   -H 'sec-ch-ua-platform: "Linux"' \
        #   -H 'sec-fetch-dest: empty' \
        #   -H 'sec-fetch-mode: cors' \
        #   -H 'sec-fetch-site: same-site' \
        #   -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36' \
        #   -H 'x-reddit-compression: 1' \
        #   -H 'x-reddit-loid: 000000000fw2q7fmtn.2.1689893517638.Z0FBQUFBQmt1YnFOMzJfZEVpOFpIRmJaNjRBRjdxTVNsSUYxbER6MWg2ZnAzWG95c243cXJ3N3ExNU80aWJMTnhDeG1jX29tYXBUSmdEMHBnbTRvcTlKV0xDZXJyalZGWFoyc0NfLVI4dTFXTmtBSDhEZm11aXEycEY0b3JMQTV2alExWEhQR0NXenA' \
        #   -H 'x-reddit-session: nmnmgrprglbelnogra.0.1689893568985.Z0FBQUFBQmt1YnJCY1gyNHF1M3lWdEwxWEhBVl9GM05ISVhwTmRRWjZLTTh5R29fQ2NVc0UwNXAzSTNKeFM3MDFKTW8tanZjY3Fzbi1leERLejZtczZFYlFPekxYdVNDZ2s4c2Rza3lXOEh1VlRfeWNMSUhfS1JBbjQ2SFIzTUw4bnFBMWpSWXVqOTI' \
        #   --data-raw '{"id":"c79807b42f04","variables":{"topicIds":["6c90b78f-802f-4eaa-a7a1-e312d9034b21","6d96a00f-5118-44d7-ab65-f0f43cf91e73","ed262509-5dee-4653-9330-10303246e6cb","3ff7f08b-ff11-4c24-836b-4a8f012d7064","085faa24-4a50-4b6b-9db8-b936141037e9","16ebaaac-ba43-4d97-842e-8ab96282dd2b","5b802129-f5a2-4af8-9632-8353ea462b3d"],"schemeName":"topic_chaining_icons","maxSubreddits":10,"onboardingFlow":"ONBOARDING"}}' \
        #   --compressed

        # Randomize profiles
        # Continue button

        # page refresh

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
