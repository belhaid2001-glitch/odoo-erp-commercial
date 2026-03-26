# -*- coding: utf-8 -*-
"""
===========================================================================
  TEST DASHBOARD — Tests E2E pour custom_dashboard
  Couvre : DashboardKpi, DashboardMixin.get_full_dashboard_data
===========================================================================
"""
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'custom_dashboard')
class TestDashboardKpi(TransactionCase):
    """Tests du modèle KPI dashboard."""

    def test_01_create_kpi(self):
        """On peut créer un KPI de dashboard."""
        kpi = self.env['dashboard.kpi'].create({
            'name': 'Chiffre d\'affaires mensuel',
            'category': 'sale',
            'sequence': 10,
            'icon': 'fa-money',
            'description': 'Total des ventes du mois',
        })
        self.assertTrue(kpi.active)
        self.assertEqual(kpi.category, 'sale')

    def test_02_kpi_categories(self):
        """Toutes les catégories KPI sont valides."""
        for cat in ('sale', 'purchase', 'stock', 'accounting', 'hr', 'crm'):
            kpi = self.env['dashboard.kpi'].create({
                'name': f'KPI {cat}',
                'category': cat,
            })
            self.assertEqual(kpi.category, cat)

    def test_03_deactivate_kpi(self):
        """On peut désactiver un KPI."""
        kpi = self.env['dashboard.kpi'].create({
            'name': 'KPI à désactiver',
            'category': 'sale',
        })
        kpi.active = False
        self.assertFalse(kpi.active)


@tagged('post_install', '-at_install', 'custom_dashboard')
class TestDashboardData(TransactionCase):
    """Tests de la récupération des données du dashboard."""

    def test_10_get_full_dashboard_data(self):
        """get_full_dashboard_data retourne un dictionnaire structuré."""
        DashboardKpi = self.env['dashboard.kpi']
        data = DashboardKpi.get_full_dashboard_data()
        self.assertIsInstance(data, dict)
        # Vérifie les clés principales
        self.assertIn('kpis', data)
        self.assertIn('charts', data)
        self.assertIn('alerts', data)

    def test_11_kpis_structure(self):
        """Les KPIs contiennent les métriques de vente."""
        data = self.env['dashboard.kpi'].get_full_dashboard_data()
        kpis = data.get('kpis', {})
        # Vérifie quelques KPIs attendus
        for key in ('revenue_this_month', 'orders', 'quotations'):
            self.assertIn(key, kpis, f"KPI '{key}' attendu dans les données")

    def test_12_charts_structure(self):
        """Les données de graphiques sont structurées."""
        data = self.env['dashboard.kpi'].get_full_dashboard_data()
        charts = data.get('charts', {})
        for key in ('monthly_revenue', 'sales_by_type', 'stock_overview', 'crm_pipeline'):
            self.assertIn(key, charts, f"Graphique '{key}' attendu")

    def test_13_alerts_is_list(self):
        """Les alertes sont retournées sous forme de liste."""
        data = self.env['dashboard.kpi'].get_full_dashboard_data()
        alerts = data.get('alerts', [])
        self.assertIsInstance(alerts, list)

    def test_14_chart_monthly_revenue_data(self):
        """Les données mensuelles ont labels et datasets."""
        data = self.env['dashboard.kpi'].get_full_dashboard_data()
        monthly = data.get('charts', {}).get('monthly_revenue', {})
        self.assertIn('labels', monthly)
        self.assertIn('datasets', monthly)

    def test_15_get_dashboard_data_legacy(self):
        """get_dashboard_data (méthode legacy) retourne des données."""
        DashboardMixin = self.env['dashboard.mixin']
        data = DashboardMixin.get_dashboard_data()
        self.assertIsInstance(data, dict)

    def test_16_dashboard_no_crash_empty_db(self):
        """Le dashboard ne crash pas sur une base vide."""
        data = self.env['dashboard.kpi'].get_full_dashboard_data()
        self.assertIsNotNone(data)
        # Les valeurs numériques doivent être >= 0
        kpis = data.get('kpis', {})
        for key in ('revenue_this_month', 'orders', 'quotations'):
            if key in kpis:
                self.assertGreaterEqual(kpis[key], 0)
