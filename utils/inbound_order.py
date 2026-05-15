from playwright.sync_api import Page, expect
import re


def wait_for_inbound_order_table(page: Page):
    """
    Wait until Inbound Order page and table data are loaded.
    Breadcrumb alone is not enough because it appears before table data.
    """

    expect(
        page.get_by_label("breadcrumb").get_by_text(
            "Inbound Order",
            exact=True
        )
    ).to_be_visible(timeout=30000)

    # Wait for at least one data row.
    # nth(0) is usually header row, nth(1) is first data row.
    expect(
        page.get_by_role("row").nth(1)
    ).to_be_visible(timeout=30000)


def find_first_new_row_across_pages(page: Page, max_pages: int = 10):
    """
    Find first inbound order row with status = New across pagination.
    """

    for page_number in range(1, max_pages + 1):
        print(f"\n===== CHECKING INBOUND ORDER PAGE {page_number} =====")

        wait_for_inbound_order_table(page)

        # First, directly check if any visible "New" status exists on current page
        new_statuses = page.get_by_text("New", exact=True)

        for i in range(new_statuses.count()):
            new_status = new_statuses.nth(i)

            if new_status.is_visible():
                print(f"Found New status on page {page_number}")

                selected_row = new_status.locator(
                    "xpath=ancestor::*[@role='row'][1]"
                )

                return selected_row

        print(f"No New status found on page {page_number}.")

        # Capture first data row before clicking next
        rows = page.get_by_role("row")

        first_row_text_before = ""

        if rows.count() > 1:
            first_row_text_before = rows.nth(1).inner_text().strip()

        next_page_button = page.get_by_role(
            "button",
            name="Go to next page"
        )

        if next_page_button.count() == 0:
            print("Next page button not found.")
            break

        if next_page_button.is_disabled():
            print("Next page button is disabled. No more pages.")
            break

        print("Clicking Go to next page button...")

        next_page_button.scroll_into_view_if_needed()
        expect(next_page_button).to_be_enabled(timeout=10000)
        next_page_button.click()

        # Wait for table to change after pagination
        if first_row_text_before:
            expect(
                page.get_by_role("row").nth(1)
            ).not_to_have_text(
                first_row_text_before,
                timeout=30000
            )

        print("Next page loaded successfully.")

    raise AssertionError(
        f"No inbound order with status New found after checking "
        f"{max_pages} page(s)."
    )


def get_first_new_inbound_order_details(page: Page):
    page.goto("http://52.74.129.113/order-management/inbound-order")

    wait_for_inbound_order_table(page)

    selected_row = find_first_new_row_across_pages(page)

    inbound_document_no = (
        selected_row
        .get_by_role("gridcell")
        .nth(0)
        .inner_text()
        .strip()
    )

    company_name = (
        selected_row
        .get_by_role("gridcell")
        .nth(5)
        .inner_text()
        .strip()
    )

    selected_row.dblclick()

    lpn_cell = (
        page.get_by_role("gridcell")
        .filter(has_text="TOTE")
        .first
    )

    expect(lpn_cell).to_be_visible(timeout=10000)

    line_item_row = lpn_cell.locator(
        "xpath=ancestor::*[@role='row'][1]"
    )

    lpn_code = (
        line_item_row
        .get_by_role("gridcell")
        .nth(0)
        .inner_text()
        .strip()
    )

    sku_code = (
        line_item_row
        .get_by_role("gridcell")
        .nth(1)
        .locator("a")
        .inner_text()
        .strip()
    )

    return {
        "inbound_document_no": inbound_document_no,
        "lpn_code": lpn_code,
        "company_name": company_name,
        "sku_code": sku_code,
    }