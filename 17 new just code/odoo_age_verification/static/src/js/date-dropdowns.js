/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

$(document).ready(function() {
    const monthNames = ["January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"
    ];
      var qntYears = 120;
      var selectYear = $("#year");
      var selectMonth = $("#month");
      var selectDay = $("#day");
      var currentYear = new Date().getFullYear();

      for (var y = 0; y < qntYears; y++){
        let date = new Date(currentYear);
        var yearElem = document.createElement("option");
        yearElem.value = currentYear
        yearElem.textContent = currentYear;
        selectYear.append(yearElem);
        currentYear--;
      }selectYear.prepend('<option value="" selected>YYYY</option>');

      for (var m = 0; m < 12; m++){
          let monthNum = new Date(2019, m).getMonth()
          let month = monthNames[monthNum];
          var monthElem = document.createElement("option");
          monthElem.value = monthNum + 1;
          monthElem.textContent = month;
          selectMonth.append(monthElem);
        }selectMonth.prepend('<option value="" selected>MM</option>');
        
        var d = new Date();
        var month = d.getMonth();
        var year = d.getFullYear();
        var day = d.getDate();
        
        // selectYear.val(year);
        selectYear.on("change", AdjustDays);
        // selectMonth.val(month);
        selectMonth.on("change", AdjustDays);
    
        AdjustDays();
        selectDay.val(day)
        selectDay.append('<option value="" selected>DD</option>');
        function AdjustDays(){
          var year = selectYear.val();
          var month = parseInt(selectMonth.val());
          if (year || month){
            selectDay.empty();
            selectDay.append('<option value="" selected>DD</option>');
          }

          //get the last day, so the number of days in that month
          var days = new Date(year, month, 0).getDate();
    
          //lets create the days of that month
          for (var d = 1; d <= days; d++){
            var dayElem = document.createElement("option");
            dayElem.value = d;
            dayElem.textContent = d;
            selectDay.append(dayElem);
          }
        }
    });
