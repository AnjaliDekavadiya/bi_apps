/** @odoo-module **/
import { jsonrpc } from '@web/core/network/rpc_service';
    function startTime(){
			var today = new Date();
			var hr = today.getHours();
			var min = today.getMinutes();
			var sec = today.getSeconds();
			min = checkTime(min);
			sec = checkTime(sec);
			document.getElementById("new_clock").innerHTML = hr + ":" + min + ":" + sec;
			var curWeekDay = today.getDay();
			var curDay = today.getDate();
			var curMonth = today.getMonth() +1;
			var curYear = today.getFullYear();
			var date =curYear+"-"+curMonth+"-"+curDay;
			document.getElementById("start_date").innerHTML = date;
			var time = setTimeout(function(){ startTime() }, 500);
		 }
        var job_id_details = $("#job_order_id").val();
        $('#pause').css('display','none');
		$('#resume').css('display','none');
		$('#stop').css('display','none');

		var today = new Date();
			var hr = today.getHours();
			var min = today.getMinutes();
			var sec = today.getSeconds();
			min = checkTime(min);
			sec = checkTime(sec);
			var st = hr + ":" + min + ":" + sec;
		var start_time  , pause_time ,start_pause = 0 ,resume_time =0 ,delay_pause = 0
		function checkTime(i) {
			if (i < 10) {
				i = "0" + i;
			}
			return i;
		}
		$('#start').click(function() {
            var def1 = jsonrpc("/load_data", {
                        'job_data': job_id_details,
                     })
			startTime();
			var today = new Date();
			var hr = today.getHours();
			var min = today.getMinutes();
			var sec = today.getSeconds();
			min = checkTime(min);
			sec = checkTime(sec);
			document.getElementById("clock").innerHTML = hr + ":" + min + ":" + sec;
			start_time = document.getElementById("clock").innerHTML
			document.getElementById("status").innerHTML ="Start"
			document.getElementById('pause').style.display = "block"
			document.getElementById('start').style.display = "none"
			document.getElementById('stop').style.display = "block"
			})

		function pad(num) {
			return ("0"+num).slice(-2);
		}
		function diffTime(start,end) {
		  var s = start.split(":"), sMin = +s[1] + s[0]*60 + s[0]*60,
			  e =   end.split(":"), eMin = +e[1] + e[0]*60 + s[0]*60,
		   diff = eMin-sMin;
		  if (diff<0) { sMin-=12*60;  diff = eMin-sMin }
		  var h = Math.floor(diff / 60),
			  m = diff % 60;
			  s = m % 60;
		  return "" + pad(h) + ":" + pad(m) +":"+pad(s);
		}
		$('#pause').click(function() {
			document.getElementById("status").innerHTML ="Pause"
			document.getElementById('resume').style.display = "block"
		  	document.getElementById('pause').style.display = "none"
		  	pause_time = document.getElementById("new_clock").innerHTML
		  	document.getElementById("pause_time").innerHTML = pause_time
		  	var a = diffTime(start_time, document.getElementById("new_clock").innerHTML);
		  	start_pause =timeToDecimal(a);
		  	document.getElementById("duration").innerHTML = start_pause;
		  	document.getElementById("totduration").innerHTML = start_pause;
		  })

		$('#resume').click(function() {
			document.getElementById("status").innerHTML ="Restart"
			resume_time = document.getElementById("new_clock").innerHTML
			var b = diffTime(pause_time, document.getElementById("new_clock").innerHTML);
			delay_pause = timeToDecimal(b);
			document.getElementById('pause').style.display = "block"
			document.getElementById('resume').style.display = "none"
		})
		function timeToDecimal(t) {
            t = t.split(':');
            var a = t[0]*60;
            var b = parseInt(a) + parseInt(t[1]);
            var c = parseFloat(parseInt(b) / 60);
            return c
		}
		$('#stop').click(function() {
            var date = document.getElementById("start_date").innerHTML
            var last =document.getElementById("new_clock").innerHTML
            document.getElementById("status").innerHTML ="Stop"

            var total;
            var today = new Date();
            var hour=0;
            var minute=0;
            var second=0;
            var new_time = 0;
            var a = diffTime(start_time, document.getElementById("new_clock").innerHTML);
            start_pause =timeToDecimal(a);
            var delay = document.getElementById("new_clock").innerHTML;
                document.getElementById("stop_time").innerHTML = delay;
                document.getElementById("stop_date").innerHTML = delay;
                document.getElementById("duration").innerHTML = start_pause.toFixed(2);
                document.getElementById("totduration").innerHTML = start_pause.toFixed(2);
                var job_name = document.getElementById("order_name").innerHTML
                var project_name = document.getElementById("project_name").innerHTML
                var task_name = document.getElementById("task_name").innerHTML
                var time_details =  []
                var vals  = {'last_start_time' : start_time ,
                            'last_stop_time' : delay,
                            'total_duration' : start_pause.toFixed(2),};
                time_details.push({'time_details' : vals})
                jsonrpc("/load_order", {
                    'job_order': job_id_details,
                    'job_name':job_name,
                    'task_name':task_name,
                    'project_name':project_name,
                    'time_details':time_details,
                    'date':today,
                 })
                .then(function (output) {
                    window.location.href =  '/edit_timesheet/this-time-sheet-for-job-order-'+output;
                    })
                document.getElementById('pause').style.display = "none";
                document.getElementById('stop').style.display = "none";
                document.getElementById('resume').style.display = "none";
                document.getElementById('start').style.display = "block";
          })
        $('#close_button').click(function() {
		  	location.reload()
		  })
