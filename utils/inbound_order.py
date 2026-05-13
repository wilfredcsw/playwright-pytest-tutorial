from playwright.sync_api import Page, expect

def get_first_new_inbound_order_details(page: Page):
    page.goto("http://52.74.129.113/order-management/inbound-order")

    expect(
        page.get_by_label("breadcrumb").get_by_text("Inbound Order", exact=True)
    ).to_be_visible()

    new_status = page.get_by_text("New", exact=True).first
    expect(new_status).to_be_visible()

    selected_row = new_status.locator("xpath=ancestor::*[@role='row'][1]")

    inbound_document_no = selected_row.get_by_role("gridcell").nth(0).inner_text()

    # Adjust nth index if Company is in a different column
    company_name = selected_row.get_by_role("gridcell").nth(5).inner_text()

    selected_row.dblclick()

    lpn_cell = page.get_by_role("gridcell").filter(has_text="TOTE").first
    expect(lpn_cell).to_be_visible()

    line_item_row = lpn_cell.locator("xpath=ancestor::*[@role='row'][1]")

    lpn_code = line_item_row.get_by_role("gridcell").nth(0).inner_text()
    sku_code = (
        line_item_row
        .get_by_role("gridcell")
        .nth(1)
        .locator("a")
        .inner_text()
    )

    return {
        "inbound_document_no": inbound_document_no,
        "lpn_code": lpn_code,
        "company_name": company_name,
        "sku_code": sku_code,
    }