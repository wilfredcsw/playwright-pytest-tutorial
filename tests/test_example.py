from playwright.sync_api import Page, expect

def test_google(page: Page):
    page.goto("https://example.com")
    page.pause()
    expect(page).to_have_title("Example Domain")