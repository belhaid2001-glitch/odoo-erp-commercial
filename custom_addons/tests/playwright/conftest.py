# -*- coding: utf-8 -*-
"""
Conftest partagé pour les tests Playwright E2E Odoo.
Fournit les fixtures d'authentification et navigation.
"""
import pytest
from playwright.sync_api import Page

ODOO_URL = "http://127.0.0.1:8069"
ODOO_DB = "odoo_erp_commercial"
ODOO_LOGIN = "admin"
ODOO_PASSWORD = "admin"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "fr-FR",
        "timezone_id": "Europe/Paris",
    }


@pytest.fixture(scope="module")
def authenticated_page(browser):
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="fr-FR",
    )
    page = context.new_page()
    page.goto(f"{ODOO_URL}/web/login")
    page.wait_for_load_state("networkidle")
    db_select = page.locator("select[name='db']")
    if db_select.is_visible():
        db_select.select_option(ODOO_DB)
    page.fill("input[name='login']", ODOO_LOGIN)
    page.fill("input[name='password']", ODOO_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    yield page
    context.close()
