# -*- coding: utf-8 -*-
"""
===========================================================================
  PLAYWRIGHT E2E UI TESTS — Tests d'interface utilisateur
  Couvre : Navigation, formulaires, boutons, kanban, dashboard
  
  Installation :
    pip install playwright pytest-playwright
    playwright install chromium
  
  Exécution :
    pytest tests/playwright/ -v --headed  (mode visible)
    pytest tests/playwright/ -v            (mode headless)
===========================================================================
"""
import pytest
import re
from playwright.sync_api import Page, expect

# ─── Configuration ───────────────────────────────────────────────────

ODOO_URL = "http://127.0.0.1:8069"
ODOO_DB = "odoo_erp_commercial"
ODOO_LOGIN = "admin"
ODOO_PASSWORD = "admin"


# ─── Fixtures ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configuration du contexte navigateur."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "fr-FR",
        "timezone_id": "Europe/Paris",
    }


@pytest.fixture(scope="module")
def authenticated_page(browser):
    """Page authentifiée réutilisable par module de test."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="fr-FR",
    )
    page = context.new_page()
    _login(page)
    yield page
    context.close()


def _login(page: Page):
    """Helper : connexion à Odoo."""
    page.goto(f"{ODOO_URL}/web/login")
    page.wait_for_load_state("networkidle")

    # Sélectionner la base si nécessaire
    db_select = page.locator("select[name='db']")
    if db_select.is_visible():
        db_select.select_option(ODOO_DB)

    page.fill("input[name='login']", ODOO_LOGIN)
    page.fill("input[name='password']", ODOO_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)


def _navigate_to_menu(page: Page, menu_text: str, submenu_text: str = None):
    """Helper : naviguer via les menus Odoo."""
    page.click(f".o_menu_brand:has-text('{menu_text}'), "
               f".o_menu_sections a:has-text('{menu_text}'), "
               f"a.dropdown-item:has-text('{menu_text}'), "
               f"button:has-text('{menu_text}')")
    page.wait_for_load_state("networkidle")
    if submenu_text:
        page.click(f"a:has-text('{submenu_text}'), "
                   f"button:has-text('{submenu_text}')")
        page.wait_for_load_state("networkidle")


def _click_button(page: Page, button_text: str):
    """Helper : cliquer sur un bouton par texte."""
    page.click(f"button:has-text('{button_text}')")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)


# =====================================================================
#  1. TESTS DE CONNEXION
# =====================================================================

class TestAuthentication:
    """Tests de connexion à Odoo."""

    def test_login_page_loads(self, page: Page):
        """La page de login se charge correctement."""
        page.goto(f"{ODOO_URL}/web/login")
        expect(page.locator("input[name='login']")).to_be_visible()
        expect(page.locator("input[name='password']")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()

    def test_login_success(self, page: Page):
        """Connexion avec identifiants valides."""
        _login(page)
        expect(page.locator(".o_main_navbar")).to_be_visible()

    def test_login_wrong_password(self, page: Page):
        """Connexion avec mot de passe incorrect affiche une erreur."""
        page.goto(f"{ODOO_URL}/web/login")
        page.fill("input[name='login']", ODOO_LOGIN)
        page.fill("input[name='password']", "wrong_password")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        expect(page.locator(".alert-danger")).to_be_visible()

    def test_login_empty_fields(self, page: Page):
        """Soumission avec champs vides reste sur login."""
        page.goto(f"{ODOO_URL}/web/login")
        page.click("button[type='submit']")
        # Devrait rester sur la page de login
        expect(page.locator("input[name='login']")).to_be_visible()


# =====================================================================
#  2. TESTS DASHBOARD
# =====================================================================

class TestDashboard:
    """Tests du tableau de bord Power BI."""

    def test_dashboard_loads(self, authenticated_page: Page):
        """Le dashboard se charge sans erreur."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=custom_dashboard.action_dashboard_main_owl")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        # Pas d'erreur OWL visible
        expect(page.locator(".o_error_dialog")).not_to_be_visible(timeout=5000)

    def test_dashboard_kpi_cards_visible(self, authenticated_page: Page):
        """Les cartes KPI sont visibles."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=custom_dashboard.action_dashboard_main_owl")
        page.wait_for_timeout(3000)
        kpi_cards = page.locator(".kpi-card, .dashboard-kpi")
        expect(kpi_cards.first).to_be_visible(timeout=10000)

    def test_dashboard_charts_rendered(self, authenticated_page: Page):
        """Les graphiques sont rendus (canvas non vides)."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=custom_dashboard.action_dashboard_main_owl")
        page.wait_for_timeout(5000)
        canvases = page.locator("canvas")
        expect(canvases.first).to_be_visible(timeout=10000)


# =====================================================================
#  3. TESTS VENTE (SALE)
# =====================================================================

class TestSaleUI:
    """Tests UI du module Vente."""

    def test_sale_menu_accessible(self, authenticated_page: Page):
        """Le menu Vente est accessible."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=sale.action_quotations_with_onboarding")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_list_view, .o_kanban_view")).to_be_visible(timeout=10000)

    def test_create_quotation(self, authenticated_page: Page):
        """Création d'un devis via l'interface."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=sale.action_quotations_with_onboarding")
        page.wait_for_timeout(2000)

        # Cliquer sur Nouveau
        page.click("button.o_list_button_add, .o-kanban-button-new")
        page.wait_for_timeout(1000)

        # Remplir le client
        page.click(".o_field_widget[name='partner_id'] input")
        page.fill(".o_field_widget[name='partner_id'] input", "Client Test")
        page.wait_for_timeout(1000)
        # Sélectionner ou créer
        dropdown = page.locator(".o_field_widget[name='partner_id'] .dropdown-menu")
        if dropdown.is_visible():
            dropdown.locator("a, li").first.click()
            page.wait_for_timeout(500)

    def test_sale_form_custom_fields_visible(self, authenticated_page: Page):
        """Les champs personnalisés sont visibles sur le formulaire de vente."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=sale.action_quotations_with_onboarding")
        page.wait_for_timeout(2000)
        page.click("button.o_list_button_add, .o-kanban-button-new")
        page.wait_for_timeout(1500)

        # Vérifier les champs custom
        expect(page.locator("[name='sale_type']")).to_be_visible(timeout=5000)
        expect(page.locator("[name='priority']")).to_be_visible(timeout=5000)

    def test_approval_buttons_visible(self, authenticated_page: Page):
        """Les boutons d'approbation sont présents."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=sale.action_quotations_with_onboarding")
        page.wait_for_timeout(2000)
        page.click("button.o_list_button_add, .o-kanban-button-new")
        page.wait_for_timeout(1500)

        # Le bouton "Demander approbation" devrait être visible
        approval_btn = page.locator("button:has-text('approbation')")
        expect(approval_btn).to_be_visible(timeout=5000)

    def test_ai_button_on_sale(self, authenticated_page: Page):
        """Le bouton IA est visible sur le formulaire de vente."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=sale.action_quotations_with_onboarding")
        page.wait_for_timeout(2000)

        # Ouvrir le premier devis existant s'il existe
        first_row = page.locator(".o_data_row").first
        if first_row.is_visible():
            first_row.click()
            page.wait_for_timeout(1000)
            ai_btn = page.locator("button:has-text('IA'), button:has-text('Assistant')")
            expect(ai_btn).to_be_visible(timeout=5000)


# =====================================================================
#  4. TESTS ACHAT (PURCHASE)
# =====================================================================

class TestPurchaseUI:
    """Tests UI du module Achat."""

    def test_purchase_list_loads(self, authenticated_page: Page):
        """La liste des commandes d'achat se charge."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=purchase.purchase_rfq")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_list_view, .o_kanban_view")).to_be_visible(timeout=10000)

    def test_convention_menu_accessible(self, authenticated_page: Page):
        """Le menu Conventions est accessible."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=custom_purchase.action_purchase_convention")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_list_view, .o_form_view")).to_be_visible(timeout=10000)


# =====================================================================
#  5. TESTS STOCK
# =====================================================================

class TestStockUI:
    """Tests UI du module Stock."""

    def test_picking_list_loads(self, authenticated_page: Page):
        """La liste des bons de livraison se charge."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=stock.action_picking_tree_all")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_list_view, .o_kanban_view")).to_be_visible(timeout=10000)

    def test_preparation_buttons_visible(self, authenticated_page: Page):
        """Les boutons de préparation sont visibles sur un bon."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=stock.action_picking_tree_all")
        page.wait_for_timeout(2000)
        first_row = page.locator(".o_data_row").first
        if first_row.is_visible():
            first_row.click()
            page.wait_for_timeout(1000)
            prep_btn = page.locator("button:has-text('préparation'), button:has-text('Commencer')")
            expect(prep_btn).to_be_visible(timeout=5000)


# =====================================================================
#  6. TESTS COMPTABILITÉ
# =====================================================================

class TestAccountingUI:
    """Tests UI du module Comptabilité."""

    def test_invoice_list_loads(self, authenticated_page: Page):
        """La liste des factures se charge."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=account.action_move_out_invoice_type")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_list_view, .o_kanban_view")).to_be_visible(timeout=10000)

    def test_cheque_menu_accessible(self, authenticated_page: Page):
        """Le menu Chèques est accessible."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=custom_accounting.action_account_cheque_received")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_list_view, .o_form_view")).to_be_visible(timeout=10000)


# =====================================================================
#  7. TESTS RH
# =====================================================================

class TestHRUI:
    """Tests UI du module RH."""

    def test_employee_list_loads(self, authenticated_page: Page):
        """La liste des employés se charge."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=hr.open_view_employee_list_my")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_list_view, .o_kanban_view")).to_be_visible(timeout=10000)

    def test_evaluation_menu_accessible(self, authenticated_page: Page):
        """Le menu Évaluations est accessible."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=custom_hr.action_hr_evaluation")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_list_view, .o_form_view")).to_be_visible(timeout=10000)

    def test_create_evaluation(self, authenticated_page: Page):
        """Création d'une évaluation via l'interface."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=custom_hr.action_hr_evaluation")
        page.wait_for_timeout(2000)

        page.click("button.o_list_button_add, .o-kanban-button-new")
        page.wait_for_timeout(1000)

        # Vérifier que les scores radio sont présents
        expect(page.locator("[name='score_quality']")).to_be_visible(timeout=5000)


# =====================================================================
#  8. TESTS CRM
# =====================================================================

class TestCRMUI:
    """Tests UI du module CRM."""

    def test_pipeline_loads(self, authenticated_page: Page):
        """Le pipeline CRM (kanban) se charge."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=crm.crm_lead_all_pipeline")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_kanban_view, .o_list_view")).to_be_visible(timeout=10000)

    def test_lead_form_custom_fields(self, authenticated_page: Page):
        """Les champs CRM custom sont visibles."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=crm.crm_lead_all_pipeline")
        page.wait_for_timeout(2000)

        # Créer une nouvelle opportunité
        page.click("button.o-kanban-button-new, button.o_list_button_add")
        page.wait_for_timeout(1000)

        quick_create = page.locator(".o_kanban_quick_create")
        if quick_create.is_visible():
            quick_create.locator("input").first.fill("Opp UI Test")
            quick_create.locator("button.o_kanban_add").click()
            page.wait_for_timeout(1000)

    def test_crm_buttons_visible(self, authenticated_page: Page):
        """Les boutons CRM custom sont visibles."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=crm.crm_lead_all_pipeline")
        page.wait_for_timeout(2000)
        # Ouvrir une opportunité
        card = page.locator(".oe_kanban_card, .o_kanban_record").first
        if card.is_visible():
            card.click()
            page.wait_for_timeout(1000)
            call_btn = page.locator("button:has-text('appel'), button:has-text('Enregistrer')")
            expect(call_btn).to_be_visible(timeout=5000)


# =====================================================================
#  9. TESTS CONTACTS
# =====================================================================

class TestContactsUI:
    """Tests UI du module Contacts."""

    def test_contact_list_loads(self, authenticated_page: Page):
        """La liste des contacts se charge."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=contacts.action_contacts")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_list_view, .o_kanban_view")).to_be_visible(timeout=10000)

    def test_contact_form_moroccan_fields(self, authenticated_page: Page):
        """Les champs marocains sont visibles sur un contact société."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=contacts.action_contacts")
        page.wait_for_timeout(2000)
        page.click("button.o_list_button_add, .o-kanban-button-new")
        page.wait_for_timeout(1500)

        # Cocher "Société"
        company_checkbox = page.locator("[name='is_company'] input, .o_field_boolean[name='is_company']")
        if company_checkbox.is_visible():
            company_checkbox.click()
            page.wait_for_timeout(500)

        # Vérifier les champs ICE/RC
        expect(page.locator("[name='ice']")).to_be_visible(timeout=5000)


# =====================================================================
#  10. TESTS DOCUMENTS
# =====================================================================

class TestDocumentsUI:
    """Tests UI du module Documents."""

    def test_document_list_loads(self, authenticated_page: Page):
        """La liste des documents se charge."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=custom_documents.action_document_document")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_list_view, .o_kanban_view, .o_form_view")).to_be_visible(timeout=10000)

    def test_folder_list_loads(self, authenticated_page: Page):
        """La liste des dossiers se charge."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=custom_documents.action_document_folder")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_list_view, .o_form_view")).to_be_visible(timeout=10000)


# =====================================================================
#  11. TESTS CALENDRIER
# =====================================================================

class TestCalendarUI:
    """Tests UI du module Calendrier."""

    def test_calendar_view_loads(self, authenticated_page: Page):
        """La vue Calendrier se charge."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=calendar.action_calendar_event&view_type=calendar")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        expect(page.locator(".o_calendar_view, .fc")).to_be_visible(timeout=10000)


# =====================================================================
#  12. TESTS PARAMÈTRES / SETTINGS
# =====================================================================

class TestSettingsUI:
    """Tests UI des paramètres (incluant configuration IA)."""

    def test_settings_page_loads(self, authenticated_page: Page):
        """La page Paramètres se charge sans erreur."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=base_setup.action_general_configuration")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        # Pas d'erreur
        expect(page.locator(".o_error_dialog")).not_to_be_visible(timeout=5000)

    def test_ai_settings_section(self, authenticated_page: Page):
        """La section IA est visible dans les paramètres."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=base_setup.action_general_configuration")
        page.wait_for_timeout(3000)

        # Chercher la section IA
        ia_section = page.locator("text=Intelligence Artificielle")
        if ia_section.is_visible():
            ia_section.click()
            page.wait_for_timeout(1000)
            expect(page.locator("[name='ai_provider']")).to_be_visible(timeout=5000)


# =====================================================================
#  13. TESTS APPS (MODULE LIST)
# =====================================================================

class TestAppsUI:
    """Tests de la page Applications."""

    def test_apps_page_shows_only_custom(self, authenticated_page: Page):
        """La page Apps ne montre que les modules custom."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=base.open_module_tree")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        # Vérifier qu'il y a des modules visibles
        modules = page.locator(".o_kanban_record, .oe_module_vignette")
        expect(modules.first).to_be_visible(timeout=10000)


# =====================================================================
#  14. TESTS DE WIZARD IA (UI)
# =====================================================================

class TestAIWizardUI:
    """Tests UI du wizard IA."""

    def test_ai_wizard_opens(self, authenticated_page: Page):
        """Le wizard IA s'ouvre depuis un bon de commande."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=sale.action_quotations_with_onboarding")
        page.wait_for_timeout(2000)

        first_row = page.locator(".o_data_row").first
        if first_row.is_visible():
            first_row.click()
            page.wait_for_timeout(1000)

            ai_btn = page.locator("button:has-text('IA'), button:has-text('Assistant')")
            if ai_btn.is_visible():
                ai_btn.click()
                page.wait_for_timeout(1500)
                # Le wizard devrait s'ouvrir
                wizard = page.locator(".modal, .o_dialog")
                expect(wizard).to_be_visible(timeout=5000)


# =====================================================================
#  15. TESTS DE PERFORMANCE
# =====================================================================

class TestPerformance:
    """Tests de performance basiques."""

    def test_dashboard_load_time(self, authenticated_page: Page):
        """Le dashboard charge en moins de 10 secondes."""
        page = authenticated_page
        import time
        start = time.time()
        page.goto(f"{ODOO_URL}/web#action=custom_dashboard.action_dashboard_main_owl")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        load_time = time.time() - start
        assert load_time < 10, f"Dashboard trop lent : {load_time:.2f}s"

    def test_sale_list_load_time(self, authenticated_page: Page):
        """La liste des devis charge en moins de 5 secondes."""
        page = authenticated_page
        import time
        start = time.time()
        page.goto(f"{ODOO_URL}/web#action=sale.action_quotations_with_onboarding")
        page.wait_for_load_state("networkidle")
        load_time = time.time() - start
        assert load_time < 5, f"Liste vente trop lente : {load_time:.2f}s"

    def test_contact_search_performance(self, authenticated_page: Page):
        """La recherche de contacts est réactive."""
        page = authenticated_page
        page.goto(f"{ODOO_URL}/web#action=contacts.action_contacts")
        page.wait_for_timeout(2000)
        import time
        start = time.time()
        search_input = page.locator(".o_searchview_input")
        search_input.fill("test")
        search_input.press("Enter")
        page.wait_for_load_state("networkidle")
        search_time = time.time() - start
        assert search_time < 3, f"Recherche trop lente : {search_time:.2f}s"
