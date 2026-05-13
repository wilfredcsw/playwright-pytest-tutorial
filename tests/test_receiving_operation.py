from playwright.sync_api import Page, expect
from utils.auth import login
import re
from utils.inbound_order import get_first_new_inbound_order_details
from utils.sku import get_customer_barcode_value_from_sku_master

def test_receiving_operation(page: Page):
    login(page)
    inbound_details = get_first_new_inbound_order_details(page)

    print("\n===== INBOUND DETAILS =====")
    print(f"Inbound Document No: {inbound_details['inbound_document_no']}")
    print(f"Company Name: {inbound_details['company_name']}")
    print(f"LPN Code: {inbound_details['lpn_code']}")
    print(f"SKU Code: {inbound_details['sku_code']}")
    print("===========================\n")

    barcode_value = get_customer_barcode_value_from_sku_master(
        page,
        company_name=inbound_details["company_name"],
        sku_code=inbound_details["sku_code"]
    )

    print(f"SKU Barcode Value: {barcode_value}")
    page.pause()

    page.goto("http://52.74.129.113/inbound-operation/receiving")

    expect(
        page.get_by_label("breadcrumb").get_by_text("Receiving", exact=True)
    ).to_be_visible()

    lpn_code = inbound_details['lpn_code']

    page.get_by_label("LPN Code").fill(lpn_code)

    page.get_by_role("button", name="Proceed").click()

    # Capture GRN No. before Call Bin
    grn_no = page.get_by_text(re.compile(r"^GRN\d+$")).inner_text()

    # Capture Inbound Document No. before Call Bin
    inbound_document_no = page.get_by_text(re.compile(r"^ID\d+$")).inner_text()

    # Open Call Bin modal
    page.get_by_role("button", name="Call Bin").click()

    # Select Empty bin type
    page.get_by_placeholder("Please search/select Bin Type").click()
    page.get_by_role("option", name="Empty").click()
    
    
    page.get_by_text("Call Bin").nth(2).click()

    # Wait until actual bin code appears in Current Bin section
    expect(
        page.get_by_text("Current Bin")
            .locator("xpath=..")
            .get_by_text(re.compile(r"^BIN\d+$"))
    ).to_be_visible(timeout=60000)

    # Capture called bin after it arrives
    called_bin_no = (
        page.get_by_text("Current Bin")
        .locator("xpath=..")
        .get_by_text(re.compile(r"^BIN\d+$"))
        .inner_text()
    )

    print("\n===== RECEIVING DETAILS =====")
    print(f"GRN No: {grn_no}")
    print(f"Inbound Document No: {inbound_document_no}")
    print(f"Called Bin No: {called_bin_no}")
    print("=============================\n")




