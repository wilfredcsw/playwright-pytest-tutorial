from playwright.sync_api import Page, expect

def get_customer_barcode_value_from_sku_master(
    page: Page,
    company_name: str,
    sku_code: str
):
    page.goto("http://52.74.129.113/sku/sku-master")

    page.get_by_test_id("code").click()
    page.get_by_test_id("code").fill(sku_code)

    page.get_by_role("combobox", name="Company").click()
    page.get_by_role("combobox", name="Company").fill(company_name)
    page.get_by_role("option", name=company_name).click()

    # Open matching SKU row
    page.get_by_label(sku_code).first.dblclick()

    # Wait for SKU detail area
    expect(
        page.get_by_role("tab", name="Barcodes", exact=True)
    ).to_be_visible()

    # Open Barcodes tab
    page.get_by_role("tab", name="Barcodes", exact=True).click()

    # Wait until barcode data is loaded
    expect(
        page.get_by_text("Customer", exact=True)
    ).to_be_visible(timeout=10000)

    barcode_rows = page.get_by_role("row")

    customer_barcode_value = None

    for i in range(barcode_rows.count()):
        row = barcode_rows.nth(i)
        cells = row.get_by_role("gridcell")

        if cells.count() < 3:
            continue

        sku_code_text = cells.nth(0).inner_text().strip()
        barcode_type = cells.nth(1).inner_text().strip()
        barcode_value = cells.nth(2).inner_text().strip()

        if sku_code_text == sku_code and "customer" in barcode_type.lower():
            customer_barcode_value = barcode_value
            break

    assert customer_barcode_value is not None, (
        f"No Customer barcode found for SKU: {sku_code}"
    )

    return customer_barcode_value