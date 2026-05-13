from playwright.sync_api import Page, expect


def scan_sku_barcode(
    page: Page,
    barcode_value: str,
    quantity: str
):
    """
    Scan SKU barcode in Receiving Operation and enter quantity.
    Validation should be done in the test file.
    """

     # Scan barcode
    scan_input = page.get_by_test_id("sku-code-qr")

    expect(scan_input).to_be_visible(timeout=10000)
    expect(scan_input).to_be_enabled(timeout=10000)

    scan_input.click()
    scan_input.fill(barcode_value)

    expect(scan_input).to_have_value(barcode_value)

    page.get_by_role("button", name="enter-btn").click()

    # Wait for the popup confirmation button
    yes_button = page.get_by_text("Yes", exact=True)
    expect(yes_button).to_be_visible(timeout=30000)

    # Use the Yes button as an anchor to locate the popup container
    popup = yes_button.locator(
        "xpath=ancestor::*[.//input][1]"
    )

    quantity_input = popup.locator("input").first

    expect(quantity_input).to_be_visible(timeout=10000)
    expect(quantity_input).to_be_enabled(timeout=10000)

    quantity_input.click()
    quantity_input.fill(quantity)

    yes_button.click()

    print(f"Scanned barcode: {barcode_value}")
    print(f"Charge-in quantity: {quantity}")