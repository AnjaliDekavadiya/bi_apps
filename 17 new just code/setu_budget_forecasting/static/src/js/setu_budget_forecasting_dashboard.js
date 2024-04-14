/** @odoo-module **/

import { loadJS } from "@web/core/assets";
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";

const { Component,onMounted, onWillStart, useState, useEffect,useRef } = owl;

export class setu_budget_forecasting_dashboard extends Component {
    setup() {
        super.setup();
        this.actionService = useService("action");
        
        this.orm = useService('orm');
        this.dashboardData = useState({});

        onWillStart(async () => {
            Object.assign(this.dashboardData, await this.orm.call(
                'crossovered.budget',
                'get_dashboard_data'));
                console.log(this.dashboardData);
                await loadJS("/web/static/lib/Chart/Chart.js")
        });
            onMounted(()=> {
                this.render_charts()
            });

    }


    // Render Charts
    render_charts() {
        if(Object.keys(this.dashboardData).length){
            var ctx = document.getElementById("chart_1").getContext("2d");
            var ctx2 = document.getElementById("chart_2").getContext("2d");
            var myChart = new Chart(ctx, {
                    type: "bar",
                    data: this.getBarChartData(this.dashboardData.Chart_1),
                    options: this.getChartOption(this.dashboardData.Chart_1)
             });
              var myChart2 = new Chart(ctx2, {
                    type: "bar",
                    data: this.getBarChartData(this.dashboardData.Chart_2),
                    options: this.getChartOption(this.dashboardData.Chart_2)
             });
        }
        else{
            $("#chart_1_no_data").removeClass("d-none");
            $("#chart_1").addClass("d-none");
            $("#chart_2").addClass("d-none");
            $("#chart_2_no_data").removeClass("d-none");
            $(".no_data_text").removeClass("d-none");
            var chart = new ApexCharts(document.querySelector("#chart_1_no_data"), this.getDummyOptions());
            var chart2 = new ApexCharts(document.querySelector("#chart_2_no_data"), this.getDummyOptions());
            chart.render();
            chart2.render();
        }
    }
//     on_click_selectBtn(ev) {
//        var select = $(ev.currentTarget)
//        var selectDropdown = select.parent().find('.selectDropdown')
//        if ($(selectDropdown).hasClass('toggle'))
//            $(selectDropdown).removeClass('toggle')
//        else
//            $(selectDropdown).addClass('toggle')
//    }
//
//    on_click_option(ev) {
//        var self = this;
//        var option = $(ev.currentTarget)
//        var selectBtn = option.parent().parent().parent().find('.selectBtn')
//        var selectDropdown = option.parent().parent()
//
//        $(selectBtn).html(option.html())
//        $("#DashboardName").html(option.html())
//        $(selectDropdown).removeClass('toggle')
//        $('.current_filter_msg').html('')
//        if ($(option).hasClass('option-cashin')) {
//            $("#apply_filter").addClass('filter-option-cashin')
//            $("#apply_filter").removeClass('filter-option-cashout')
//        }
//        if ($(option).hasClass('option-cashout')) {
//            $("#apply_filter").removeClass('filter-option-cashin')
//            $("#apply_filter").addClass('filter-option-cashout')
//        }
//    }

    // geterate chart.js chart data
    getBarChartData(chart){
        var datasets = []
        for(var i=0;i<Object.keys(chart.data).length;i++){
            datasets.push({'label': Object.keys(chart.data)[i], 'data' : Object.values(chart.data)[i], 'borderWidth' : 1,
                    backgroundColor :  this.getRandomColor()})
        }
        var barChartData = {
              labels: Object.values(chart.label),
              datasets: datasets
            };
        return barChartData
    }

    // generate chart options
    getChartOption(chart){
        var chartOptions = {
              responsive: true,
              legend: {
                position: "top"
              },
              title: {
                display: false,
                text: "Chart.js Bar Chart"
              },
              scales: {
                yAxes: [{
                  ticks: {
                    beginAtZero: true
                  }
                }]
              }
            }
        return chartOptions;
    }


    // generate dummy chart options
    getDummyOptions(){
        var options = {
            series: [{
                data: [44, 55, 41, 64, 22, 43, 21]
            },
            {
                data: [53, 32, 33, 52, 13, 44, 32]
            }],
            chart: {
                type: 'bar',
                height: 430
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    dataLabels: {
                        position: 'top',
                    },
                }
            },
            dataLabels: {
                enabled: false,
            },
            stroke: {
                show: true,
                width: 1,
                colors: ['#fff']
            },
            tooltip: {
                shared: true,
                intersect: false
            },
            xaxis: {
                categories: [2001, 2002, 2003, 2004, 2005, 2006, 2007],
            },
            colors:['#674a60', '#674a60']
        };
        return options;
    }

    // generating random color foe charts
    getRandomColor() {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    // Hide And Show tooltip-dialog in dashboard
    on_click_info_badge(ev){
         $(ev.target.parentElement.parentElement).find('.tooltip-dialog').slideToggle(500);
            setTimeout(function() {
                $(ev.target.parentElement.parentElement).find('.tooltip-dialog').slideToggle(500)
            }, 4000);
    }

}

setu_budget_forecasting_dashboard.template = 'SetuBudgetForecastingDashboard';

registry.category('actions').add('setu_budget_forecasting_dashboard', setu_budget_forecasting_dashboard);
