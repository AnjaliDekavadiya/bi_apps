/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { session } from "@web/session";
import { Domain } from "@web/core/domain";
import { sprintf } from "@web/core/utils/strings";

const { Component, useSubEnv, useState, onMounted, onWillStart, useRef } = owl;
import { loadJS, loadCSS } from "@web/core/assets"

class TenderDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            tenderStats: {
                'total_tender': 0,
                'active_tender': 0,
                'tender_in_process': 0,
                'pre_qualification_bid': 0,
                'pending_request': 0,
                'active_bid': 0,
                'pending_qualification': 0,
            },
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        this.tenderType = useRef('tenderType');
        this.tenderCategory = useRef('tenderCategory');
        this.tenderTimeline = useRef('tenderTimeline');

        onWillStart(async () => {
            await loadJS('/tk_tender_management/static/src/js/lib/moment.min.js');
            await loadJS('/tk_tender_management/static/src/js/lib/apexcharts.js');
            let tenderData = await this.orm.call('tender.dashboard', 'get_tender_stats', []);
            if (tenderData) {
                this.state.tenderStats = tenderData;
            }
        });

        onMounted(() => {
            this.renderTenderType();
            this.renderTenderCategory();
            this.renderTenderTimeline();
        })
    }
    viewTenderStatic(type) {
        let name, context;
        let model = 'tender.information';
        let domain = [];
        if (type == 'all') {
            name = 'Total Tender'
            context = { 'create': false }
        } else if (type == 'active_tender') {
            name = 'Active Tender'
            domain = [['stage', '=', 'bid_submission']]
            context = { 'create': false }
        } else if (type == 'in_progress') {
            name = 'In Progress'
            domain = [['stage', 'in', ['bid_evaluation', 'bid_selection']]]
            context = { 'create': false }
        } else if (type == 'pre_qualification') {
            name = 'Pre Qualification Bid'
            model = 'tender.bidding'
            domain = [['stage', '=', 'pre_qualification']]
            context = { 'create': false, 'search_default_group_by_tender': 1 }
        } else if (type == 'active_bid') {
            name = 'Active Bid'
            model = 'tender.bidding'
            domain = [['stage', '=', 'bid']]
            context = { 'create': false, 'search_default_group_by_tender': 1 }
        } else if (type == 'pending_request') {
            name = 'Pending Bid'
            model = 'tender.bidding'
            domain = [['allow_edit', '=', 'edit_request'], ['edit_request', '=', true]]
            context = { 'create': false, 'search_default_group_by_tender': 1 }
        } else if (type == 'pending_qualification') {
            name = 'Pending Qualification'
            model = 'tender.bidding'
            domain = [['stage', '=', 'pre_qualification'], ['qualify_status', '=', false]]
            context = { 'create': false, 'search_default_group_by_tender': 1 }
        }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: name,
            res_model: model,
            view_mode: 'list',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            context: context,
            domain: domain,
        });

    }
    renderTenderType() {
        const options = {
            series: this.state.tenderStats['tender_type'][1],
            chart: {
                type: 'donut',
                height: 410
            },
            colors: ['#95e2f9', '#f9aa4f', '#efe7ac', '#9daacf', '#62dfc7', '#ff5765'],
            dataLabels: {
                enabled: false
            },
            labels: this.state.tenderStats['tender_type'][0],
            legend: {
                position: 'bottom',
            },
        };
        this.renderGraph(this.tenderType.el, options);
    }
    renderTenderCategory() {
        const options = {
            series: [
                {
                    name: "Tender",
                    data: this.state.tenderStats['tender_category'][1],
                },
            ],
            chart: {
                type: 'bar',
                height: 350,
            },
            plotOptions: {
                bar: {
                    borderRadius: 0,
                    horizontal: true,
                    distributed: true,
                    barHeight: '80%',
                    isFunnel: true,
                },
            },
            colors: [
                '#F44F5E',
                '#E55A89',
                '#D863B1',
                '#CA6CD8',
                '#B57BED',
                '#8D95EB',
                '#62ACEA',
                '#4BC3E6',
            ],
            dataLabels: {
                enabled: false,
                formatter: function (val, opt) {
                    return opt.w.globals.labels[opt.dataPointIndex]
                },
                dropShadow: {
                    enabled: true,
                },
            },
            title: {
                text: 'Tender Category',
                align: 'middle',
            },
            xaxis: {
                categories: this.state.tenderStats['tender_category'][0],
            },
            legend: {
                show: false,
            },
        };
        this.renderGraph(this.tenderCategory.el, options);
    }
    renderTenderTimeline() {
        let data = this.state.tenderStats['tender_time_line']
        let tender_data = []
        for (const ss of data) {
            tender_data.push({
                'name': ss['name'],
                'data': [{
                    'x': 'Tender Duration',
                    'y': [new Date(ss['start_date']).getTime(), new Date(ss['end_date']).getTime()]
                }]
            })
        }
        const options = {
            series: tender_data,
            chart: {
                height: 350,
                type: 'rangeBar'
            },
            plotOptions: {
                bar: {
                    horizontal: true
                }
            },
            dataLabels: {
                enabled: true,
                formatter: function (val) {
                    var a = moment(val[0])
                    var b = moment(val[1])
                    var diff = b.diff(a, 'days')
                    return diff + (diff > 1 ? ' days' : ' day')
                }
            },
            fill: {
                type: 'gradient',
                gradient: {
                    shade: 'light',
                    type: 'vertical',
                    shadeIntensity: 0.25,
                    gradientToColors: undefined,
                    inverseColors: true,
                    opacityFrom: 1,
                    opacityTo: 1,
                    stops: [50, 0, 100, 100]
                }
            },
            xaxis: {
                type: 'datetime'
            }
        };
        this.renderGraph(this.tenderTimeline.el, options);
    }
    renderGraph(el, options) {
        const graphData = new ApexCharts(el, options);
        graphData.render();
    }

}
TenderDashboard.template = "tk_tender_management.template_tender_dashboard";
registry.category("actions").add("tender_dashboard", TenderDashboard);