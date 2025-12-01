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
