/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

export class DashboardMain extends Component {
    static template = "custom_dashboard.DashboardMain";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            data: null,
            loading: true,
            // --- Power BI-style Filters ---
            filters: {
                period: 'this_month',
                date_from: '',
                date_to: '',
                categories: ['sale', 'purchase', 'stock', 'accounting', 'crm', 'hr'],
            },
            showCustomDates: false,
            filterBarExpanded: true,
        });

        this.periodOptions = [
            { value: 'today', label: "Aujourd'hui", icon: 'fa-clock-o' },
            { value: 'this_week', label: 'Cette semaine', icon: 'fa-calendar-o' },
            { value: 'this_month', label: 'Ce mois', icon: 'fa-calendar' },
            { value: 'this_quarter', label: 'Ce trimestre', icon: 'fa-calendar-check-o' },
            { value: 'this_year', label: 'Cette année', icon: 'fa-calendar-plus-o' },
            { value: 'custom', label: 'Personnalisé', icon: 'fa-sliders' },
        ];

        this.categoryOptions = [
            { value: 'sale', label: 'Ventes', icon: 'fa-line-chart', color: '#1cc88a' },
            { value: 'purchase', label: 'Achats', icon: 'fa-truck', color: '#36b9cc' },
            { value: 'stock', label: 'Stock', icon: 'fa-cubes', color: '#e74a3b' },
            { value: 'accounting', label: 'Comptabilité', icon: 'fa-money', color: '#f6c23e' },
            { value: 'crm', label: 'CRM', icon: 'fa-bullseye', color: '#8b5cf6' },
            { value: 'hr', label: 'RH', icon: 'fa-users', color: '#4e73df' },
        ];

        this.revenueChartRef = useRef("revenueChart");
        this.categoryChartRef = useRef("categoryChart");
        this.stockChartRef = useRef("stockChart");
        this.crmChartRef = useRef("crmChart");
        this.charts = [];

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.loadData();
        });

        onMounted(() => {
            this.renderAllCharts();
        });

        onWillUnmount(() => {
            this.destroyCharts();
        });
    }

    // ==================== FILTERS ====================
    setPeriod(period) {
        this.state.filters.period = period;
        this.state.showCustomDates = (period === 'custom');
        if (period !== 'custom') {
            this.applyFilters();
        }
    }

    setDateFrom(ev) {
        this.state.filters.date_from = ev.target.value;
    }

    setDateTo(ev) {
        this.state.filters.date_to = ev.target.value;
    }

    applyCustomDates() {
        if (this.state.filters.date_from && this.state.filters.date_to) {
            this.applyFilters();
        }
    }

    toggleCategory(category) {
        const cats = this.state.filters.categories;
        const idx = cats.indexOf(category);
        if (idx >= 0) {
            if (cats.length > 1) {
                cats.splice(idx, 1);
            }
        } else {
            cats.push(category);
        }
        this.applyFilters();
    }

    selectAllCategories() {
        this.state.filters.categories = ['sale', 'purchase', 'stock', 'accounting', 'crm', 'hr'];
        this.applyFilters();
    }

    isCategoryActive(category) {
        return this.state.filters.categories.includes(category);
    }

    toggleFilterBar() {
        this.state.filterBarExpanded = !this.state.filterBarExpanded;
    }

    async applyFilters() {
        this.state.loading = true;
        this.destroyCharts();
        await this.loadData();
        setTimeout(() => this.renderAllCharts(), 100);
    }

    resetFilters() {
        this.state.filters.period = 'this_month';
        this.state.filters.date_from = '';
        this.state.filters.date_to = '';
        this.state.filters.categories = ['sale', 'purchase', 'stock', 'accounting', 'crm', 'hr'];
        this.state.showCustomDates = false;
        this.applyFilters();
    }

    // ==================== DATA ====================
    async loadData() {
        try {
            const filters = {
                period: this.state.filters.period,
                date_from: this.state.filters.date_from,
                date_to: this.state.filters.date_to,
                categories: this.state.filters.categories,
            };
            const data = await this.orm.call(
                "dashboard.kpi", "get_full_dashboard_data", [filters]
            );
            this.state.data = data;
            this.state.loading = false;
        } catch (e) {
            console.error("Dashboard load error:", e);
            this.state.loading = false;
        }
    }

    async refresh() {
        this.state.loading = true;
        this.destroyCharts();
        await this.loadData();
        // Use setTimeout to let the DOM update before rendering charts
        setTimeout(() => this.renderAllCharts(), 100);
    }

    // ==================== FORMATTING ====================
    fmt(value) {
        if (value === undefined || value === null) return "0";
        if (Math.abs(value) >= 1000000) {
            return (value / 1000000).toFixed(1) + " M";
        }
        if (Math.abs(value) >= 1000) {
            return (value / 1000).toFixed(0) + " K";
        }
        return Math.round(value).toLocaleString("fr-FR");
    }

    fmtCurrency(value) {
        if (value >= 1000000) return (value / 1000000).toFixed(1) + "M";
        if (value >= 1000) return (value / 1000).toFixed(0) + "K";
        return value.toLocaleString("fr-FR");
    }

    // ==================== CHARTS ====================
    destroyCharts() {
        for (const chart of this.charts) {
            if (chart) chart.destroy();
        }
        this.charts = [];
    }

    renderAllCharts() {
        if (!this.state.data || typeof Chart === "undefined") return;
        this.destroyCharts();
        this._renderRevenueChart();
        this._renderCategoryChart();
        this._renderStockChart();
        this._renderCrmChart();
    }

    _renderRevenueChart() {
        const el = this.revenueChartRef.el;
        if (!el) return;
        const d = this.state.data.charts.monthly_revenue;
        const chart = new Chart(el, {
            type: "line",
            data: {
                labels: d.labels,
                datasets: [
                    {
                        label: "Revenus",
                        data: d.revenue,
                        borderColor: "#1cc88a",
                        backgroundColor: "rgba(28, 200, 138, 0.08)",
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: "#1cc88a",
                        pointBorderColor: "#fff",
                        pointBorderWidth: 2,
                        borderWidth: 3,
                    },
                    {
                        label: "Dépenses",
                        data: d.expenses,
                        borderColor: "#e74a3b",
                        backgroundColor: "rgba(231, 74, 59, 0.05)",
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: "#e74a3b",
                        pointBorderColor: "#fff",
                        pointBorderWidth: 2,
                        borderWidth: 3,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "top", labels: { usePointStyle: true, padding: 20 } },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: "rgba(0,0,0,0.04)" },
                        ticks: { callback: (v) => this.fmtCurrency(v) },
                    },
                    x: { grid: { display: false } },
                },
                interaction: { intersect: false, mode: "index" },
            },
        });
        this.charts.push(chart);
    }

    _renderCategoryChart() {
        const el = this.categoryChartRef.el;
        if (!el) return;
        const d = this.state.data.charts.sales_by_type;
        const colors = ["#4e73df", "#1cc88a", "#36b9cc", "#f6c23e", "#e74a3b", "#8b5cf6"];
        const chart = new Chart(el, {
            type: "doughnut",
            data: {
                labels: d.labels,
                datasets: [{
                    data: d.data,
                    backgroundColor: colors.slice(0, d.labels.length),
                    borderWidth: 3,
                    borderColor: "#fff",
                    hoverOffset: 8,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { usePointStyle: true, padding: 16, font: { size: 12 } },
                    },
                },
            },
        });
        this.charts.push(chart);
    }

    _renderStockChart() {
        const el = this.stockChartRef.el;
        if (!el) return;
        const d = this.state.data.charts.stock_overview;
        const colors = [
            "rgba(78, 115, 223, 0.85)",
            "rgba(28, 200, 138, 0.85)",
            "rgba(231, 74, 59, 0.85)",
            "rgba(246, 194, 62, 0.85)",
            "rgba(54, 185, 204, 0.85)",
        ];
        const chart = new Chart(el, {
            type: "bar",
            data: {
                labels: d.labels,
                datasets: [{
                    label: "Opérations",
                    data: d.data,
                    backgroundColor: colors.slice(0, d.labels.length),
                    borderRadius: 8,
                    borderSkipped: false,
                    maxBarThickness: 60,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: "rgba(0,0,0,0.04)" },
                        ticks: { stepSize: 1, precision: 0 },
                    },
                    x: { grid: { display: false } },
                },
            },
        });
        this.charts.push(chart);
    }

    _renderCrmChart() {
        const el = this.crmChartRef.el;
        if (!el) return;
        const d = this.state.data.charts.crm_pipeline;
        const chart = new Chart(el, {
            type: "bar",
            data: {
                labels: d.labels,
                datasets: [{
                    label: "Montant estimé",
                    data: d.data,
                    backgroundColor: "rgba(139, 92, 246, 0.75)",
                    borderRadius: 8,
                    borderSkipped: false,
                    maxBarThickness: 40,
                }],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: "rgba(0,0,0,0.04)" },
                        ticks: { callback: (v) => this.fmtCurrency(v) },
                    },
                    y: { grid: { display: false } },
                },
            },
        });
        this.charts.push(chart);
    }

    // ==================== NAVIGATION ====================
    openAction(target) {
        const actions = {
            sale: "sale.action_quotations_with_onboarding",
            quotations: {
                type: "ir.actions.act_window",
                name: "Devis en cours",
                res_model: "sale.order",
                view_mode: "list,form",
                domain: [["state", "=", "draft"]],
            },
            purchase: "purchase.purchase_rfq",
            invoices: {
                type: "ir.actions.act_window",
                name: "Factures impayées",
                res_model: "account.move",
                view_mode: "list,form",
                domain: [
                    ["move_type", "=", "out_invoice"],
                    ["payment_state", "in", ["not_paid", "partial"]],
                    ["state", "=", "posted"],
                ],
            },
            stock: {
                type: "ir.actions.act_window",
                name: "Livraisons",
                res_model: "stock.picking",
                view_mode: "list,form",
                domain: [["picking_type_code", "=", "outgoing"]],
            },
            crm: "crm.crm_lead_all_pipeline",
        };
        const act = actions[target];
        if (act) this.action.doAction(act);
    }

    openAlertAction(alert) {
        if (alert.action) {
            this.action.doAction(alert.action);
        }
    }
}

registry.category("actions").add("custom_dashboard_main", DashboardMain);
