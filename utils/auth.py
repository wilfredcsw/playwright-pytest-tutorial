import re
from playwright.sync_api import Page, expect
from utils.config import APP_URL, APP_USERNAME, APP_PASSWORD

def login(page: Page):
    page.goto(APP_URL)

    page.get_by_label("Dropdown").click()
    page.get_by_label("Workstation").fill("ST02")
    page.get_by_text("ST02").click()

    page.get_by_label("Username / Email").fill(APP_USERNAME)
    page.locator("#passwordInput").fill(APP_PASSWORD)

    page.get_by_role("button", name="Log In").click()

    expect(page).to_have_url(
        re.compile(r".*/dashboard/station-operation-dashboard")
    )