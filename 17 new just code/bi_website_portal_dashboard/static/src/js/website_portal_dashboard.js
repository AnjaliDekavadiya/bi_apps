/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";

    class chart{
		constructor(name,allData){
			this.canvas = document.getElementById(name);
			this.data = allData;
			this.canvas.width=600;
			this.canvas.height=300;
			this.ctx=this.canvas.getContext("2d");
			this.xGrid=25;
			this.yGrid=50;
			this.cellSize=25;
			this.entries=Object.entries(this.data['data']);
		}

		drawGridsX(){
			this.ctx.beginPath();
			while(this.xGrid<this.canvas.height-50){
				this.ctx.setLineDash([5, 3]);
				this.ctx.moveTo(50,this.xGrid+25);
				this.ctx.lineTo(this.canvas.width-30,this.xGrid+25);
				this.xGrid+=25;
			}
			while(this.yGrid<this.canvas.width){
				this.ctx.setLineDash([3, 1]);
				this.ctx.moveTo(this.yGrid,50);
				this.ctx.lineTo(this.yGrid,this.canvas.height-50);
				this.yGrid+=40;
			}
			this.ctx.strokeStyle="#a9aaab";
			this.ctx.stroke();
		}

		blocks(count){
			return count*25;
		}

		drawAxisX(){
			var yPlot=10;
			var pop=0;
			this.ctx.beginPath();
			this.ctx.setLineDash([0]);
			this.ctx.strokeStyle="#787777";
			this.ctx.moveTo(50,50);
			this.ctx.moveTo(50,this.blocks(8));
			this.ctx.font = "12px Calibri";

			for (var i=1;i<=9;i++){
				this.ctx.strokeText(pop,this.blocks(2)-7,this.blocks(yPlot));
				yPlot-=1;
				pop+=this.data['max']/8;
			}

			this.ctx.stroke();
		}

		sizeDict(d){
			var c=0;
			for (var i in d){
				++c;
			}
			return c;
		}

		drawBarsX(){
			var xPlot = 63;
			var yPlot = 100;
			this.ctx.beginPath();
			this.ctx.strokeStyle="#787777";
			this.ctx.font = "12px Calibri";
			this.ctx.moveTo(63,this.blocks(8));
			this.ctx.fillStyle = "#FF0000";
			var dist=1;
			var sizeData=this.sizeDict(this.data['data']);
			if (sizeData==1){
				xPlot=63+(40*6);
			};
			if (sizeData==5){
				xPlot=63+(40*2);
				dist=2;
			};
			if (sizeData==7){
				xPlot=63;
				dist=2;
			};
			if (sizeData==12){
				xPlot=63;
			};
			for (const[con, pop] of this.entries){
				yPlot=(pop/this.data['max'])*100;
				yPlot = (Math.floor(yPlot))*2;
				this.ctx.fillRect(xPlot,this.blocks(10)-yPlot,14,yPlot);
				this.ctx.strokeText(con,xPlot+14+con.length*2,this.blocks(10)+16);
				xPlot+=40*dist;
			};
			this.ctx.stroke();
		}


		drawGridsY(){
			var xGrid=25;
			var yGrid=170;
			this.ctx.beginPath();
			while(xGrid<this.canvas.height-20){
				this.ctx.setLineDash([3, 1]);
				this.ctx.moveTo(170,xGrid);
				this.ctx.lineTo(this.canvas.width-30,xGrid);
				xGrid+=25;
			}
			while(yGrid<this.canvas.width){
				this.ctx.setLineDash([3, 1]);
				this.ctx.moveTo(yGrid,25);
				this.ctx.lineTo(yGrid,this.canvas.height-25);
				yGrid+=50;
			}
			this.ctx.strokeStyle="#a9aaab";
			this.ctx.stroke();
		}

		drawAxisY(){
			var yPlot=3;
			var pop=0;
			this.ctx.beginPath();
			this.ctx.strokeStyle="#787777";
			this.ctx.setLineDash([0]);
			this.ctx.moveTo(170,this.canvas.height-10);
			this.ctx.font = "12px Calibri";

			for (var i=1;i<=9;i++){
				this.ctx.strokeText(pop,(20+50*yPlot),this.canvas.height-10);
				yPlot+=1;
				pop+=this.data['max']/8;
			}

			this.ctx.stroke();
		}

		replaceAll(string, search, replace) {
			return string.split(search).join(replace);
		}

		drawBarsY(){
			var xPlot = 0;
			var yPlot = 0;
			this.ctx.beginPath();
			this.ctx.strokeStyle="#787777";
			this.ctx.moveTo(165,this.canvas.height-50);
			this.ctx.fillStyle = "#FF0000";
			for (const[key, val] of this.entries){
				yPlot=(val[1]/this.data['max'])*400;
				yPlot = (Math.floor(yPlot));
				this.ctx.fillRect(170,this.canvas.height-43-xPlot,yPlot,10);
				var word = val[0].split(" ");
				if (word.length>3){
					var w = this.replaceAll(String(word.slice(0,3)),","," ");
					var q = this.replaceAll(String(word.slice(3,word.length)),","," ");
					this.ctx.strokeText(w,165,this.canvas.height-40-xPlot);
					this.ctx.strokeText(q,165,this.canvas.height-30-xPlot);
				}
				else{
					this.ctx.strokeText(val[0],165,this.canvas.height-40-xPlot);
				}
				xPlot+=25;
			};
			this.ctx.stroke();
		}

		draw_x_axis_chart(){
			this.drawGridsX();
			this.drawAxisX();
			this.drawBarsX();
		}

		draw_y_axis_chart(){
			this.drawGridsY();
			this.drawAxisY();
			this.drawBarsY();
		}

	}


	$(document).ready(function() {
		if ($(".breadcrumb-item.active")[0]){
			$(".dashboard_header_text_h").html($(".breadcrumb-item.active")[0].innerText);
		}
		else{
			$(".dashboard_header_text_h").html('Your Documents');
		}
	});


	$(document).ready(function() {
		var txtValue = document.getElementsByClassName("grid_td_img");
		for (var i=0; i<txtValue.length; i++){
			$('.grid_td_img.'+txtValue[i].classList[1]).css('background-color','#'+txtValue[i].classList[1]);
		}
	});

	$(document).ready(function() {
		var select_filter = document.getElementById("filter_options_condition");
		if(select_filter){
			select_filter.onchange = function() {
				var filter = $("#filter_options_condition").val();

				jsonrpc('/_set_filter_for_table',{
		            "index" : filter,
		            }).then(function (data) {
						$("#tedt").load(" #tedt");
					});
					loadCharts(filter);
					loadProductsCharts(filter);
					productsTables(filter);
				};
			}
	});

	jsonrpc('/_set_filter_for_table',{
        "index" : 1,
        }).then(function (data) {
			$("#tedt").load(" #tedt");
		});
	loadCharts(1);
	loadProductsCharts(1);
	productsTables(1);


	function checkLists(ele,list){
		for (var i=0; i<list.length; i++){
			if  (list[i].indexOf(ele) > -1) {
				return 1;
				}
		}
		return 0;
	}


	function productsTables(filter){
		var nodesSold = document.getElementsByClassName("sold_prds");
		var nodesPur = document.getElementsByClassName("purchase_prds");
		jsonrpc('/_get_product_ids',{
	        "index" : filter,
	        }).then(function (data) {
	        	if (data[0].length == 0){
	        		$(".no_solds").css('display','block');
	        	}
	        	else{
	        		$(".no_solds").css('display','none');
	        	}
	        	var cls,i;
				if(nodesSold.length > 0){
					for (i=0; i<nodesSold.length; i++){
						cls = checkLists(nodesSold[i].classList[0],data[0]);
						if  (cls) {
					    	nodesSold[i].classList.remove("o_hidden");
					    }
					    else{
					    	$("."+nodesSold[i].classList[0]).addClass('o_hidden');
					    }
					}
				}

				if (data[1].length == 0){
	        		$(".no_purchase").css('display','block');
	        	}
	        	else{
	        		$(".no_purchase").css('display','none');
	        	}
	        	if(nodesPur.length > 0){
					for (i=0; i<nodesPur.length; i++){
						cls = checkLists(nodesPur[i].classList[0],data[1]);
						if  (cls) {
					    	nodesPur[i].classList.remove("o_hidden");
					    }
					    else{
					    	$("."+nodesPur[i].classList[0]).addClass('o_hidden');
					    }
					}

	        	}

			});
	}


	function loadCharts(filter){
		var titles = [["Today's Sales Anaylsis","Today's Invoice Anaylsis","Today's Purchase Anaylsis","Today's Bill Anaylsis"],
						["Yesterday's Sales Anaylsis","Yesterday's Invoice Anaylsis","Yesterday's Purchase Anaylsis","Yesterday's Bill Anaylsis"],
						["Sales Anaylsis of the week","Invoice Anaylsis of the week","Purchase Anaylsis of the week","Bill Anaylsis of the week"],
						["Sales Anaylsis of the month","Invoice Anaylsis of the month","Purchase Anaylsis of the month","Bill Anaylsis of the month"],
						["Sales Anaylsis of the year","Invoice Anaylsis of the year","Purchase Anaylsis of the year","Bill Anaylsis of the year"],];
		var title_first = document.getElementById("chart_so_title_text");
		var title_second =  document.getElementById("chart_inv_title_text");
		var title_third = document.getElementById("chart_po_title_text");
		var title_fourth =  document.getElementById("chart_bill_title_text");
		if (title_first){
			title_first.innerHTML = titles[filter-1][0];
		}
		if (title_second){
			title_second.innerHTML = titles[filter-1][1];
		}
		if (title_third){
			title_third.innerHTML = titles[filter-1][2];
		}
		if (title_fourth){
			title_fourth.innerHTML = titles[filter-1][3];
		}

		jsonrpc('/_get_chart_data',{
            "index" : filter,
            }).then(function (data) {
            	if (title_first){
	                var chart_so = new chart("chart_so",data[0]);
	                chart_so.draw_x_axis_chart();
				}
				if (title_second){
	                var chart_inv = new chart("chart_inv",data[2]);
	                chart_inv.draw_x_axis_chart();
				}
				if (title_third){
	                var chart_po = new chart("chart_po",data[1]);
	                chart_po.draw_x_axis_chart();
				}
				if (title_fourth){
	                var chart_bill = new chart("chart_bill",data[3]);
	                chart_bill.draw_x_axis_chart();
				}
            });
	}


	function loadProductsCharts(filter){
		var prod_titles = [["Today's Top 10 Products Sold","Today's Top 10 Products Purchased"],
							["Yesterday's Top 10 Products Sold","Yesterday's Top 10 Products Purchased"],
							["Current Week's Top 10 Products Sold","Current Week's Top 10 Products Purchased"],
							["Current Month's Top 10 Products Sold","Current Month's Top 10 Products Purchased"],
							["Current Year's Top 10 Products Sold","Current Year's Top 10 Products Purchased"],];
		var title_fifth =  document.getElementById("product_chart_view_sold_title_text");
		var title_sixth =  document.getElementById("product_chart_view_purchase_title_text");
		var title_seventh =  document.getElementById("sold_product_table_view_header_text");
		var title_eighth =  document.getElementById("purchase_product_table_view_header_text");
		if (title_fifth){
			title_fifth.innerHTML = prod_titles[filter-1][0];
		}
		if (title_sixth){
			title_sixth.innerHTML = prod_titles[filter-1][1];
		}
		if (title_seventh){
			title_seventh.innerHTML = prod_titles[filter-1][0];
		}
		if (title_eighth){
			title_eighth.innerHTML = prod_titles[filter-1][1];
		}

		jsonrpc('/_get_chart_data/products',{
            "index" : filter,
            }).then(function (data) {
            	if (title_fifth){
	                var chart_sold = new chart("chart_product_sold",data[0]);
	                chart_sold.draw_y_axis_chart();
				}
				if (title_sixth){
	                var chart_purchase = new chart("chart_product_purchase",data[1]);
	                chart_purchase.draw_y_axis_chart();
				}
            });
	}

