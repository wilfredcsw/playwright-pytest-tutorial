from playwright.sync_api import Page, expect
from utils.auth import login
import re
from utils.inbound_order import get_first_new_inbound_order_details
from utils.sku import get_customer_barcode_value_from_sku_master
from utils.sku_scanner import scan_sku_barcode, store_bin_with_capacity

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
    ).to_be_visible(timeout=90000)

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

    # Scan barcode and charge in quantity
    charge_in_quantity = "10"

    scan_sku_barcode(
        page,
        barcode_value=barcode_value,
        quantity=charge_in_quantity
    )

    # Wait until Total Charge In updates after scan confirmation
    expect(
        page.get_by_text(
            f"Total Charge In:{charge_in_quantity}",
            exact=True
        )
    ).to_be_visible(timeout=30000)

    # Verify Total Expected and Total Charge In are tally
    total_expected_locator = page.get_by_text(
        re.compile(r"Total Expected:\s*\d+")
    )

    total_charge_in_locator = page.get_by_text(
        re.compile(r"Total Charge In:\s*\d+")
    )

    expect(total_expected_locator).to_be_visible(timeout=10000)
    expect(total_charge_in_locator).to_be_visible(timeout=10000)

    total_expected_text = total_expected_locator.inner_text()
    total_charge_in_text = total_charge_in_locator.inner_text()

    total_expected = int(
        re.search(r"Total Expected:\s*(\d+)", total_expected_text).group(1)
    )

    total_charge_in = int(
        re.search(r"Total Charge In:\s*(\d+)", total_charge_in_text).group(1)
    )

    assert total_expected == total_charge_in, (
        f"Total Expected and Total Charge In are not tally. "
        f"Expected: {total_expected}, Charge In: {total_charge_in}"
    )

    print(
        f"Total Expected and Total Charge In tally: "
        f"{total_expected} = {total_charge_in}"
    )

    # Verify correct record(s) are added in Scanned Item(s) listing
    scanned_item_rows = (
        page.get_by_role("row")
        .filter(has_text=inbound_details["lpn_code"])
        .filter(has_text=inbound_details["sku_code"])
        .filter(has_text=called_bin_no)
    )

    row_count = scanned_item_rows.count()

    assert row_count > 0, (
        "No scanned item record found. "
        f"Expected LPN={inbound_details['lpn_code']}, "
        f"SKU={inbound_details['sku_code']}, "
        f"Storage={called_bin_no}"
    )

    print("\n===== SCANNED ITEM RECORD(S) FOUND =====")

    scanned_items = []

    for i in range(row_count):
        row = scanned_item_rows.nth(i)

        expect(row).to_be_visible(timeout=10000)

        cells = row.get_by_role("gridcell")

        scanned_lpn_code = cells.nth(0).inner_text().strip()
        scanned_sku_cell_text = cells.nth(1).inner_text().strip()
        scanned_sku_code = scanned_sku_cell_text.splitlines()[0].strip()
        scanned_qty = cells.nth(2).inner_text().strip()
        scanned_sku_uom = cells.nth(3).inner_text().strip()
        scanned_batch_no = cells.nth(4).inner_text().strip()
        scanned_expiry_date = cells.nth(5).inner_text().strip()
        scanned_manufacturer_date = cells.nth(6).inner_text().strip()
        scanned_storage_no = cells.nth(7).inner_text().strip()

        scanned_item = {
            "lpn_code": scanned_lpn_code,
            "sku_code": scanned_sku_code,
            "qty": scanned_qty,
            "sku_uom": scanned_sku_uom,
            "batch_no": scanned_batch_no,
            "expiry_date": scanned_expiry_date,
            "manufacturer_date": scanned_manufacturer_date,
            "storage_no": scanned_storage_no,
        }

        scanned_items.append(scanned_item)

        print(f"\nRecord {i + 1}:")
        print(f"LPN Code: {scanned_lpn_code}")
        print(f"SKU Code: {scanned_sku_code}")
        print(f"Qty: {scanned_qty}")
        print(f"SKU UOM: {scanned_sku_uom}")
        print(f"Batch No.: {scanned_batch_no}")
        print(f"Expiry Date: {scanned_expiry_date}")
        print(f"Manufacturer Date: {scanned_manufacturer_date}")
        print(f"Storage No.: {scanned_storage_no}")

        assert scanned_lpn_code == inbound_details["lpn_code"], (
            f"Scanned item LPN mismatch in record {i + 1}. "
            f"Expected: {inbound_details['lpn_code']}, Actual: {scanned_lpn_code}"
        )

        assert inbound_details["sku_code"] == scanned_sku_code, (
            f"Scanned item SKU mismatch in record {i + 1}. "
            f"Expected SKU: {inbound_details['sku_code']}, Actual SKU Code: {scanned_sku_code}"
        )

        assert scanned_storage_no == called_bin_no, (
            f"Scanned item storage/bin mismatch in record {i + 1}. "
            f"Expected: {called_bin_no}, Actual: {scanned_storage_no}"
        )

    print("\n===== END SCANNED ITEM RECORD(S) =====")

    # Store bin after successful charge-in
    selected_capacity = "50"  # Change this value to test different capacity options: "25", "50", "75", "100"

    store_bin_with_capacity(
        page,
        capacity_percentage=selected_capacity
    )

    # Wait until GRN Summary popup appears
    summary_title = page.get_by_text("GRN Summary", exact=True)

    expect(summary_title).to_be_visible(timeout=30000)

    # Scope to GRN Summary popup
    summary_popup = summary_title.locator(
        "xpath=ancestor::*[.//*[normalize-space()='Complete']][1]"
    )

    expect(summary_popup).to_be_visible(timeout=10000)

    # Verify GRN Summary scanned item is tally
    expect(
        summary_popup.get_by_text("Scanned Items (Current Workstation)", exact=True)
    ).to_be_visible(timeout=10000)

    # SKU appears twice in the cell: SKU code + description.
    # We only need to confirm the expected SKU exists in the scanned item section.
    expect(
        summary_popup.get_by_text(inbound_details["sku_code"], exact=True).first
    ).to_be_visible(timeout=10000)

    # Verify received quantity is shown in the summary table
    expect(
        summary_popup.get_by_text(charge_in_quantity, exact=True).last
    ).to_be_visible(timeout=10000)

    summary_text = summary_popup.inner_text()

    assert inbound_details["sku_code"] in summary_text, (
        f"GRN Summary SKU not found. "
        f"Expected SKU: {inbound_details['sku_code']}"
    )

    assert charge_in_quantity in summary_text, (
        f"GRN Summary received qty not found. "
        f"Expected Received Qty: {charge_in_quantity}"
    )

    print("\n===== GRN SUMMARY SCANNED ITEM VERIFIED =====")
    print(f"SKU Code: {inbound_details['sku_code']}")
    print(f"Received Qty: {charge_in_quantity}")
    print("============================================\n")

    # Click Complete inside GRN Summary popup
    complete_button = summary_popup.get_by_text("Complete", exact=True)

    expect(complete_button).to_be_visible(timeout=10000)

    complete_button.scroll_into_view_if_needed()
    complete_button.click(timeout=10000, force=True)

    # Verify Complete action actually worked by checking redirect back to Receiving page
    expect(page).to_have_url(
        re.compile(r".*/inbound-operation/receiving/?$"),
        timeout=30000
    )

    expect(
        page.get_by_label("breadcrumb").get_by_text("Receiving", exact=True)
    ).to_be_visible(timeout=10000)
    
    print("Clicked Complete on GRN Summary popup")
    print("Completed Putaway Successfully")

    