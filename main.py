from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import selenium
import csv
import time
import sys

chrome_options = Options()
# chrome_options.headless = True
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_experimental_option("detach", False)
chrome_options.add_argument("--headless")
# WINDOW_SIZE = 720, 1080
# chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

DELAY = 1
ENROLLED = 0
BASE_URL = "https://stepik.org/course/"
DRIVER = webdriver.Chrome(chrome_options=chrome_options)
REGISTRATION_URL = "https://stepik.org/registration"
LOGIN_URL = "https://stepik.org/login"
CURRENT_PERSON = None


def register(
    Fio: str = None, Mail: str = None, Password: str = None, *args, **kwargs
) -> bool:
    DRIVER.get(REGISTRATION_URL)
    try:
        WebDriverWait(DRIVER, 10).until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "id_registration_full-name",
                )
            )
        )

    except selenium.common.exceptions.TimeoutException:
        return False
    try:
        DRIVER.find_element(By.ID, "id_registration_full-name").send_keys(Fio)
        DRIVER.find_element(By.ID, "id_registration_email").send_keys(Mail)
        DRIVER.find_element(By.ID, "id_registration_password").send_keys(Password)
        DRIVER.find_element(By.XPATH, '//*[@id="registration_form"]/button').click()
    except:
        return False
    time.sleep(2)
    if DRIVER.find_elements(By.XPATH, '//*[@id="registration_form"]/button'):
        return False
    return True


def login(Mail: str = None, Password: str = None, *args, **kwargs):
    DRIVER.get(LOGIN_URL)

    try:
        WebDriverWait(DRIVER, 10).until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "id_login_email",
                )
            )
        )
    except selenium.common.exceptions.TimeoutException:
        return False
    try:
        DRIVER.find_element(By.ID, "id_login_email").send_keys(Mail)
        DRIVER.find_element(By.ID, "id_login_password").send_keys(Password)
        DRIVER.find_element(By.XPATH, '//*[@id="login_form"]/button').click()
    except:
        return False
    time.sleep(2)
    if DRIVER.find_elements(By.XPATH, '//*[@id="login_form"]/button'):
        return False
    return True


def enroll(course_ids: list[str]) -> list[bool]:
    enrolled_courses = list()

    for course_id in course_ids:
        text = (
            "Зарегистрировано: "
            + str(ENROLLED)
            + " людей"
            + " | Регистрирует "
            + CURRENT_PERSON
            + " на "
            + str(course_id)
        )
        print("\r" + text + "                     ", end="")
        DRIVER.get(f"https://stepik.org/course/{course_id}/promo")
        try:
            WebDriverWait(DRIVER, 1).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "button.course-promo-enrollment__join-btn",
                    )
                )
            )
        except selenium.common.exceptions.TimeoutException:
            enrolled_courses.append(True)
            continue
        elements = DRIVER.find_elements(
            By.CSS_SELECTOR, "button.course-promo-enrollment__join-btn"
        )
        if elements:
            try:
                elements[-1].click()
            except:
                enrolled_courses.append(False)
        time.sleep(0.5)
        enrolled_courses.append(True)

    return enrolled_courses


if __name__ == "__main__":
    courses = list()
    with open("stepik_course_ids.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            courses.append(row[0].strip())
    amount = 0
    with open("data_base.csv", "r") as f:
        reader = csv.DictReader(f, delimiter=",")

        counter = 0
        for i, row in enumerate(reader):
            if amount == 800:
                break
            try:
                DRIVER.close()
            except:
                ...
            # if row["EduForm"].strip().lower() not in ["заочная", "очно-заочная"]:
            #     continue
            counter += 1
            if counter <= 77:
                continue
            amount += 1
            print(amount)
            DRIVER = webdriver.Chrome(chrome_options=chrome_options)
            row["Mail"] = row["Mail"].replace("pfur", "rudn")
            CURRENT_PERSON = row["Fio"]
            if not register(**row):
                if not login(**row):
                    continue
            try:
                time.sleep(1)
                ENROLLED += sum(enroll(courses))

            except selenium.common.exceptions.NoSuchWindowException:
                ...

            time.sleep(1)
    DRIVER.quit()
