from playwright.sync_api import Page, expect

def test_login(page: Page):
    page.goto("http://52.74.129.113/login")

    page.get_by_label("Dropdown").click()
    page.get_by_label("Workstation").fill("ST02")
    page.get_by_text("ST02").click()
    
    # Fill in the username and password fields
    page.get_by_label("Username / Email").fill("wilfredcsw")
    page.locator("#passwordInput").fill("@Testing123")

    # Click the login button
    page.get_by_role("button", name="Log In").click()
    
    # Verify that the user is redirected to the dashboard
    expect(page).to_have_url("http://52.74.129.113/dashboard/station-operation-dashboard")