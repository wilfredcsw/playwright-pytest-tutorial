from playwright.sync_api import Page, expect

def test_click_link(page: Page):
    page.goto("https://example.com")
    
    #click the link
    page.get_by_role("link", name="Learn more").click()

    #verify new page
    expect(page).to_have_url("https://www.iana.org/domains/reserved")