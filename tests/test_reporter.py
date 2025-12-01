"""
Test suite for pytest-playwright-json reporter.

Tests organized by outcome type:
- Passing, Failing, Skipped, Xfail, Flaky, Parametrized
"""

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com/"


class TestPassing:
    """Tests that pass."""

    def test_page_title(self, page: Page) -> None:
        page.goto(BASE_URL)
        expect(page).to_have_title("Swag Labs")

    def test_login_form_visible(self, page: Page) -> None:
        page.goto(BASE_URL)
        expect(page.locator("#user-name")).to_be_visible()
        expect(page.locator("#password")).to_be_visible()

    def test_login_button_enabled(self, page: Page) -> None:
        page.goto(BASE_URL)
        expect(page.locator("#login-button")).to_be_enabled()

    def test_successful_login(self, page: Page) -> None:
        page.goto(BASE_URL)
        page.locator("#user-name").fill("standard_user")
        page.locator("#password").fill("secret_sauce")
        page.locator("#login-button").click()
        expect(page).to_have_url(f"{BASE_URL}inventory.html")


class TestFailing:
    """Tests that fail - to verify error reporting."""

    def test_wrong_title(self, page: Page) -> None:
        page.goto(BASE_URL)
        expect(page).to_have_title("Wrong Title")

    def test_element_not_found(self, page: Page) -> None:
        page.goto(BASE_URL)
        expect(page.locator("#missing")).to_be_visible(timeout=2000)

    def test_assertion_error(self, page: Page) -> None:
        page.goto(BASE_URL)
        assert 1 == 2, "Numbers don't match"


class TestErrorTypes:
    """Different Python error types."""

    def test_index_error(self, page: Page) -> None:
        page.goto(BASE_URL)
        _ = [1, 2][10]

    def test_key_error(self, page: Page) -> None:
        page.goto(BASE_URL)
        _ = {}["missing"]

    def test_type_error(self, page: Page) -> None:
        page.goto(BASE_URL)
        _ = "str" + 1

    def test_zero_division(self, page: Page) -> None:
        page.goto(BASE_URL)
        _ = 1 / 0


class TestSkipped:
    """Skipped tests."""

    @pytest.mark.skip(reason="Not implemented")
    def test_skip_explicit(self, page: Page) -> None:
        pass

    @pytest.mark.skipif(True, reason="Condition true")
    def test_skip_conditional(self, page: Page) -> None:
        pass


class TestXfail:
    """Expected failures."""

    @pytest.mark.xfail(reason="Known bug")
    def test_xfail_fails(self, page: Page) -> None:
        page.goto(BASE_URL)
        assert False

    @pytest.mark.xfail(reason="Should fail")
    def test_xfail_passes(self, page: Page) -> None:
        page.goto(BASE_URL)
        assert True


_counter = {}

class TestFlaky:
    """Flaky tests with retries."""

    @pytest.mark.flaky(reruns=2)
    def test_passes_on_retry(self, page: Page) -> None:
        page.goto(BASE_URL)
        _counter["retry"] = _counter.get("retry", 0) + 1
        assert _counter["retry"] >= 2


class TestParametrized:
    """Parametrized tests."""

    @pytest.mark.parametrize("user,pwd,ok", [
        ("standard_user", "secret_sauce", True),
        ("locked_out_user", "secret_sauce", False),
        ("bad_user", "bad_pass", False),
    ], ids=["valid", "locked", "invalid"])
    def test_login(self, page: Page, user: str, pwd: str, ok: bool) -> None:
        page.goto(BASE_URL)
        page.locator("#user-name").fill(user)
        page.locator("#password").fill(pwd)
        page.locator("#login-button").click()
        if ok:
            expect(page).to_have_url(f"{BASE_URL}inventory.html")
        else:
            expect(page.locator("[data-test='error']")).to_be_visible()


class TestScreenshots:
    """Screenshot capture tests."""

    def test_capture_screenshot(self, page: Page) -> None:
        page.goto(BASE_URL)
        page.screenshot(path="test-results/login.png")
        expect(page).to_have_title("Swag Labs")


class TestNavigation:
    """Navigation flow tests."""

    def test_login_and_cart(self, page: Page) -> None:
        page.goto(BASE_URL)
        page.locator("#user-name").fill("standard_user")
        page.locator("#password").fill("secret_sauce")
        page.locator("#login-button").click()
        page.locator(".shopping_cart_link").click()
        expect(page).to_have_url(f"{BASE_URL}cart.html")

    def test_logout(self, page: Page) -> None:
        page.goto(BASE_URL)
        page.locator("#user-name").fill("standard_user")
        page.locator("#password").fill("secret_sauce")
        page.locator("#login-button").click()
        page.locator("#react-burger-menu-btn").click()
        page.locator("#logout_sidebar_link").click()
        expect(page).to_have_url(BASE_URL)


class TestVisualComparison:
    """Visual/Image comparison tests using Playwright screenshots."""

    def test_login_page_full(self, page: Page) -> None:
        """Capture full page screenshot of login page."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        screenshot = page.screenshot(full_page=True)
        assert len(screenshot) > 0, "Screenshot should not be empty"

    def test_screenshot_comparison_fail(self, page: Page) -> None:
        """This test intentionally fails to generate screenshot artifacts."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        # Take screenshot
        screenshot = page.screenshot()
        # Intentionally fail - screenshot size won't match this arbitrary value
        assert len(screenshot) == 12345, f"Screenshot comparison failed: expected 12345 bytes, got {len(screenshot)}"

    def test_login_button_element(self, page: Page) -> None:
        """Capture screenshot of login button element."""
        page.goto(BASE_URL)
        login_button = page.locator("#login-button")
        screenshot = login_button.screenshot()
        assert len(screenshot) > 0, "Screenshot should not be empty"

    def test_login_form_element(self, page: Page) -> None:
        """Capture screenshot of the login form container."""
        page.goto(BASE_URL)
        login_form = page.locator(".login_wrapper")
        screenshot = login_form.screenshot()
        assert len(screenshot) > 0, "Screenshot should not be empty"

    def test_inventory_page_full(self, page: Page) -> None:
        """Capture full page screenshot after login."""
        page.goto(BASE_URL)
        page.locator("#user-name").fill("standard_user")
        page.locator("#password").fill("secret_sauce")
        page.locator("#login-button").click()
        page.wait_for_load_state("networkidle")
        screenshot = page.screenshot(full_page=True)
        assert len(screenshot) > 0, "Screenshot should not be empty"

    def test_product_card_element(self, page: Page) -> None:
        """Capture screenshot of first product card."""
        page.goto(BASE_URL)
        page.locator("#user-name").fill("standard_user")
        page.locator("#password").fill("secret_sauce")
        page.locator("#login-button").click()
        page.wait_for_load_state("networkidle")
        first_product = page.locator(".inventory_item").first
        screenshot = first_product.screenshot()
        assert len(screenshot) > 0, "Screenshot should not be empty"

    def test_header_element(self, page: Page) -> None:
        """Capture screenshot of header after login."""
        page.goto(BASE_URL)
        page.locator("#user-name").fill("standard_user")
        page.locator("#password").fill("secret_sauce")
        page.locator("#login-button").click()
        header = page.locator(".header_container")
        screenshot = header.screenshot()
        assert len(screenshot) > 0, "Screenshot should not be empty"

    def test_save_screenshots_to_files(self, page: Page) -> None:
        """Save multiple screenshots to test-results folder."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")

        # Save login page screenshot
        page.screenshot(path="test-results/visual-login-page.png")

        # Save login button screenshot
        page.locator("#login-button").screenshot(path="test-results/visual-login-button.png")

        # Login and save inventory page
        page.locator("#user-name").fill("standard_user")
        page.locator("#password").fill("secret_sauce")
        page.locator("#login-button").click()
        page.wait_for_load_state("networkidle")
        page.screenshot(path="test-results/visual-inventory-page.png")

        # Save product card screenshot
        page.locator(".inventory_item").first.screenshot(path="test-results/visual-product-card.png")
