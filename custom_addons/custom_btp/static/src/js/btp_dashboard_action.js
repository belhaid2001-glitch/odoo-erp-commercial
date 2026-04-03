/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

export class BtpDashboard extends Component {
    static template = "custom_btp.BtpDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            data: null,
            loading: true,
        });

        this.statesChartRef = useRef("statesChart");
        this.avancementChartRef = useRef("avancementChart");
        this.typesChartRef = useRef("typesChart");
        this.villesChartRef = useRef("villesChart");
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

    // ==================== DATA ====================
    async loadData() {
        try {
            const data = await this.orm.call(
                "btp.chantier", "get_btp_dashboard_data", []
            );
            this.state.data = data;
            this.state.loading = false;
        } catch (e) {
            console.error("BTP Dashboard load error:", e);
            this.state.loading = false;
        }
    }

    async refresh() {
        this.state.loading = true;
        this.destroyCharts();
        await this.loadData();
        setTimeout(() => this.renderAllCharts(), 150);
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

    fmtDH(value) {
        if (value === undefined || value === null) return "0 DH";
        if (Math.abs(value) >= 1000000) {
            return (value / 1000000).toFixed(2) + " M DH";
        }
        if (Math.abs(value) >= 1000) {
            return (value / 1000).toFixed(0) + " K DH";
        }
        return Math.round(value).toLocaleString("fr-FR") + " DH";
    }

    // ==================== NAVIGATION ====================
    openChantiers() {
        this.action.doAction("custom_btp.action_btp_chantier");
    }

    openChantiersEnCours() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Chantiers en cours",
            res_model: "btp.chantier",
            view_mode: "kanban,tree,form",
            domain: [["state", "in", ["en_cours", "reprise"]]],
        });
    }

    openChantiersRetard() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Chantiers en retard",
            res_model: "btp.chantier",
            view_mode: "tree,form",
            domain: [["state", "in", ["en_cours", "reprise"]], ["retard_jours", ">", 0]],
        });
    }

    openChantier(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Chantier",
            res_model: "btp.chantier",
            res_id: id,
            view_mode: "form",
            views: [[false, "form"]],
        });
    }

    openEngins() {
        this.action.doAction("custom_btp.action_btp_engin");
    }

    openSituations() {
        this.action.doAction("custom_btp.action_btp_situation");
    }

    openApprovisionnements() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Approvisionnements en attente",
            res_model: "btp.approvisionnement",
            view_mode: "tree,form",
            domain: [["state", "=", "demande"]],
        });
    }

    openPointages() {
        this.action.doAction("custom_btp.action_btp_pointage");
    }

    openDocuments() {
        this.action.doAction("custom_btp.action_btp_document");
    }

    openRessources() {
        this.action.doAction("custom_btp.action_btp_ressource");
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
        this._renderStatesChart();
        this._renderAvancementChart();
        this._renderTypesChart();
        this._renderVillesChart();
    }

    _renderStatesChart() {
        const el = this.statesChartRef.el;
        if (!el || !this.state.data.states_chart.length) return;
        const d = this.state.data.states_chart;
        const colors = [
            '#6c757d', '#17a2b8', '#007bff', '#0056b3',
            '#28a745', '#dc3545', '#20c997', '#ffc107',
            '#fd7e14', '#6f42c1', '#e83e8c'
        ];
        const chart = new Chart(el, {
            type: "doughnut",
            data: {
                labels: d.map(x => x.state),
                datasets: [{
                    data: d.map(x => x.count),
                    backgroundColor: colors.slice(0, d.length),
                    borderWidth: 2,
                    borderColor: '#fff',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: { position: "bottom", labels: { font: { size: 11 }, padding: 12 } },
                    tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${ctx.parsed}` } },
                },
            }
        });
        this.charts.push(chart);
    }

    _renderAvancementChart() {
        const el = this.avancementChartRef.el;
        if (!el || !this.state.data.chart_avancements.length) return;
        const d = this.state.data.chart_avancements;
        const chart = new Chart(el, {
            type: "bar",
            data: {
                labels: d.map(x => x.name),
                datasets: [{
                    label: "Avancement %",
                    data: d.map(x => x.avancement),
                    backgroundColor: d.map(x => x.retard > 0 ? '#dc354580' : '#28a74580'),
                    borderColor: d.map(x => x.retard > 0 ? '#dc3545' : '#28a745'),
                    borderWidth: 1,
                    borderRadius: 4,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: (ctx) => `${ctx.parsed.x.toFixed(1)}%` } },
                },
                scales: {
                    x: { beginAtZero: true, max: 100, ticks: { callback: v => v + '%' } },
                    y: { ticks: { font: { size: 11 } } },
                },
            }
        });
        this.charts.push(chart);
    }

    _renderTypesChart() {
        const el = this.typesChartRef.el;
        if (!el || !this.state.data.types_marche.length) return;
        const d = this.state.data.types_marche;
        const colors = ['#4e73df', '#1cc88a', '#f6c23e'];
        const chart = new Chart(el, {
            type: "pie",
            data: {
                labels: d.map(x => x.type),
                datasets: [{
                    data: d.map(x => x.count),
                    backgroundColor: colors.slice(0, d.length),
                    borderWidth: 2,
                    borderColor: '#fff',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom", labels: { font: { size: 11 }, padding: 12 } },
                },
            }
        });
        this.charts.push(chart);
    }

    _renderVillesChart() {
        const el = this.villesChartRef.el;
        if (!el || !this.state.data.villes_data.length) return;
        const d = this.state.data.villes_data.slice(0, 8);
        const colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#8b5cf6', '#fd7e14', '#20c997'];
        const chart = new Chart(el, {
            type: "bar",
            data: {
                labels: d.map(x => x.ville),
                datasets: [{
                    label: "Chantiers",
                    data: d.map(x => x.count),
                    backgroundColor: colors.slice(0, d.length),
                    borderWidth: 0,
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } },
                    x: { ticks: { font: { size: 11 } } },
                },
            }
        });
        this.charts.push(chart);
    }
}

registry.category("actions").add("btp_dashboard_main", BtpDashboard);
