from playwright.sync_api import Page, expect
from utils.auth import login

def test_get_latest_new_inbound_lpn(page: Page):
    login(page)

    page.goto("http://52.74.129.113/order-management/inbound-order")

    expect(
        page.get_by_label("breadcrumb").get_by_text("Inbound Order", exact=True)
    ).to_be_visible()

    # Find the first visible New status badge
    new_status = page.get_by_text("New", exact=True).first
    expect(new_status).to_be_visible()

    # Go up to the row that contains this New status
    selected_row = new_status.locator("xpath=ancestor::*[@role='row'][1]")

    inbound_document_no = selected_row.get_by_role("gridcell").nth(0).inner_text()
    print(f"Selected Inbound Document No: {inbound_document_no}")

    selected_row.dblclick()

    # Capture first LPN code
    lpn_cell = page.get_by_role("gridcell").filter(has_text="TOTE").first

    expect(lpn_cell).to_be_visible()

    lpn_code = lpn_cell.inner_text()

    print(f"LPN Code: {lpn_code}")


    # Navigate to Receiving page
    page.goto("http://52.74.129.113/inbound-operation/receiving")

    # Verify Receiving page loaded
    expect(
        page.get_by_label("breadcrumb").get_by_text("Receiving", exact=True)
    ).to_be_visible()

    # Fill LPN Code
    page.get_by_label("LPN Code").fill(lpn_code)

    # Click Proceed
    page.get_by_role("button", name="Proceed").click()
    