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

#======================================================================================================#
#select bin capacity and store bin
def store_bin_with_capacity(
    page: Page,
    capacity_percentage: str
):
    """
    Click Store Bin, select bin capacity, then confirm Store.

    Supported capacity values:
    - "25"
    - "50"
    - "75"
    - "100"
    """

    allowed_capacity = ["25", "50", "75", "100"]

    assert capacity_percentage in allowed_capacity, (
        f"Invalid capacity percentage: {capacity_percentage}. "
        f"Allowed values: {allowed_capacity}"
    )

    # 1. Click Store Bin button first
    store_bin_button = page.get_by_role("button", name="Store Bin")

    expect(store_bin_button).to_be_visible(timeout=10000)
    expect(store_bin_button).to_be_enabled(timeout=10000)

    store_bin_button.click()

    # 2. Wait for bin capacity dialog to appear
    expect(
        page.get_by_text("Please confirm the capacity load.")
    ).to_be_visible(timeout=10000)

    # 3. Select preferred capacity
    if capacity_percentage == "100":
        capacity_option_text = "100%Full"
    else:
        capacity_option_text = f"{capacity_percentage}%Partial Full"

    capacity_option = page.get_by_text(
        capacity_option_text,
        exact=True
    )

    expect(capacity_option).to_be_visible(timeout=10000)
    capacity_option.click()

    # 4. Click Store inside the capacity dialog
    dialog_store_button = page.locator("#main-layout").get_by_text(
        "Store",
        exact=True
    )

    expect(dialog_store_button).to_be_visible(timeout=10000)
    expect(dialog_store_button).to_be_enabled(timeout=10000)

    dialog_store_button.click()

    print(f"Store Bin completed with capacity: {capacity_percentage}%")