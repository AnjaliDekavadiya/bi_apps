/** @odoo-module */
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import { Component, onWillStart, useEffect, onMounted, useState} from "@odoo/owl";
import { KeepLast } from "@web/core/utils/concurrency";
var D3_COLORS = ["#1f77b4","#ff7f0e","#aec7e8","#ffbb78","#2ca02c","#98df8a","#d62728", "#ff9896","#9467bd","#c5b0d5","#8c564b","#c49c94","#e377c2","#f7b6d2", "#7f7f7f","#c7c7c7","#bcbd22","#dbdb8d","#17becf","#9edae5"];

export class SMSNotificationDashboard extends Component {
	// static props={}
	setup() {
		this.rpc = useService('rpc');
		this.action = useService('action');
		this.keepLast = new KeepLast();
        this.state = useState({
            line_data: {},
            gateway_data: {},
            connected_gateways: 0,
            total_count: 0,
            sent_count: 0,
            delivered_count: 0,
            undelivered_count: 0,
            failed_count: 0,
        });
        onWillStart(async () => loadJS("/web/static/lib/Chart/Chart.js"));		
				
		onMounted(async () => {
			await this.fetch_data();
			this.render_line_graph();
			this.render_pie_graph();
        });
	}

	async fetch_data(line_stage='all',pie_stage='total', days=7) {
        const smsdashboardData = await this.keepLast.add(
            this.rpc("/sms_notification/dashboard_data", {
                line_stage: line_stage,
				pie_stage: pie_stage,
				days : days,
            })
        );
        Object.assign(this.state, smsdashboardData);
    }

	reload_line_graph() {
		var self = this
		var selected_option = $('#line_obj_change option:selected').val()
		var line_chart_label = $('#line_chart_label')
		switch (selected_option) {
			case 'new':
				line_chart_label.text('New')
				break
			case 'sent':
				line_chart_label.text('Sent')
				break
			case 'delivered':
				line_chart_label.text('Delivered')
				break
			case 'undelivered':
				line_chart_label.text('Undelivered')
				break
			case 'failed':
				line_chart_label.text('Failed')
				break
			default:
				line_chart_label.text('')
		}
		$.when(
			self.fetch_data(
				selected_option,
				parseInt($('#pie_obj_change option:selected').val()),
				parseInt($('#line_date_change option:selected').val()),
			)
		).then(function () {
			return self.render_line_graph()
		})
	}

	reload_pie_graph() {
		var selected_stage = $('#pie_obj_change option:selected').val()
		var pie_chart_label = $('#pie_chart_label')
		switch (selected_stage) {
			case selected_stage:
				pie_chart_label.text(selected_stage.substr(0, 1).toUpperCase() + selected_stage.substr(1))
				break
			default:
				pie_chart_label.text('')
		}
		this.render_pie_graph(selected_stage)
	}



	render_line_graph() {
		$('#line_chart').replaceWith($('<canvas/>', { id: 'line_chart' }))
		var self = this
		self.line_chart = new Chart('line_chart', {
			type: 'line',
			data: {
				labels: self.state.line_data.labels,
				datasets: self.state.line_data.data.map(i => ({
					backgroundColor: D3_COLORS[1],
					borderColor: D3_COLORS[0],
					data: Object.values(i.count),
					label: i.state,
					fill: false,
				})),
			},
			beginAtZero: false,
			options: {
				maintainAspectfirefoxRatio: false,
				plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        enabled: false,
                    },
                },
				scales: {
					x: {
						gridLines: {
							display: false,
						},
					},
					y: {
						gridLines: {
							display: false,
						},
						ticks: {
							precision: 0,
						},
					},
				},
			},
		})
	}

	render_pie_graph(obj = 'total') {
		$('#pie_chart').replaceWith($('<canvas/>', { id: 'pie_chart' }))
		var self = this;
		self.pie_chart = new Chart('pie_chart', {
			type: 'pie',
			data: {
				labels: Object.keys(self.state.gateway_data),
				datasets: [{
					backgroundColor: Object.values(self.state.gateway_data).map(function (val, index) {
						return D3_COLORS[index % 20];
					}),
					data: Object.values(self.state.gateway_data).map(i => i[obj + '_count']),
				}],
				hoverOffset: 4,
			},
			options: {
				maintainAspectRatio: false,
				cutout: 80,
				plugins: {
                    legend: {
						position: 'bottom',
						labels: {
							usePointStyle: true,
						},
						onClick: explodePie,
				   },
                },
			},
			plugins: [{
				id : 'pie_chart',
				beforeDraw: function(chart, a, b) {
					if (chart.canvas.id === 'pie_chart') {
						var ctx = chart.ctx,
							cw = chart.width,
							ch = chart.height;
					    var vals = Object.values(self.state.gateway_data).map(i => i[obj + '_count']);
								
						var total = 0;
						for (var i in vals) {
							total += vals[i];
						}
						ctx.restore();
						{
							ctx.textBaseline = "top";
							var fontFamily = 'Poppins';
							ctx.font = '56px ' + fontFamily;
							ctx.textAlign = 'center';
							ctx.fillStyle = '#ffffff';
							ctx.clearRect(0, 0, cw, ch);
							ctx.fillStyle = '#000000';
							ctx.fillText(total, cw / 2, (ch / 5));
							ctx.font = '26px ' + fontFamily;
							ctx.fillStyle = '#7B8EB7';
							ctx.fillText('Total SMS', cw / 2, (ch / 2.5));
							ctx.save();
						ctx.save();
						}
			    }	}
            }]
			
		})
		
		var lastindex;
		function explodePie(e, legendItem, legend) {
			const index = legendItem.index;
			var i, ilen, total;
			for (i = 0, ilen = (self.pie_chart.data.datasets || []).length; i < ilen; ++i) {
				var meta = self.pie_chart.getDatasetMeta(i);
				total = meta.total;
				meta.data.forEach((m) => {
					if(lastindex && lastindex.index == index){
						if (m._index != lastindex.index) {
							m.hidden = !m.hidden;
						}
						else{
							m.hidden = false;
						}
					}
					else if(legendItem.hidden == true){
						if (m._index == index) {
							m.hidden = false;
						}
						else{
							m.hidden = true;
						}
					}
				});
			}
			legend.chart.update();
			legend.chart.toggleDataVisibility(legendItem.index);
			lastindex = legendItem;
			// render_pie(meta.total);
		}
	}

	on_action(e) {
		e.preventDefault()
		var target = $(e.currentTarget)
		var _action = target.data('action');
		switch (_action) {
			case 'send_sms':
				return this.action.doAction({
					name: 'Send SMS',
					type: 'ir.actions.act_window',
					res_model: 'wk.sms.sms',
					views: [[false, 'form']],
					target: 'new'
				})
			case 'configuration':
				return this.action.doAction({
					name: 'Gateway Configuration',
					type: 'ir.actions.act_window',
					res_model: 'sms.mail.server',
					views: [[false, 'form']],
					target: 'new'
				})
		}
	}

}
SMSNotificationDashboard.template = 'dashboard_template'
registry.category("actions").add('sms_notification.dashboard', SMSNotificationDashboard)
