/*  计算公式
 21天，6%；
 30天，6.3%；
 90天，6.8%；
 180天，7%；
 270天，7.5%；
 365天，7.8%；

 投资a元，b天定存计划，年化收益为c（c见上图）
 收益=a*c*（b/365）
 */

var moneyValue = 239000;
var dateValue = 90;
var profit = 4007.34;
$("input[name='mv']").each(function(i) {
    $(this).click(function() {
        $('#jq22-circle').css("left", (41 + 109 * i) + "px");
        for (var mm = 0; mm < 7; mm++) {
            if (mm == i) {
                $(".money-value-pos label").eq(mm).css({
                    "font-size": "24px",
                    "color": "#ff1f38"
                });
                $(".money-value-pos .bubble").eq(mm).fadeIn();

            } else {
                $(".money-value-pos label").eq(mm).css({
                    "font-size": "16px",
                    "color": "#fe9196"
                });
                $(".money-value-pos .bubble").eq(mm).fadeOut();

            }
        }

        moneyValue = $(this).val();
        dateValue = $("input[name='itd']:checked").val();
        if (dateValue == '21') {
            profit = moneyValue * 0.1 * (dateValue / 365)
        }
        if (dateValue == '30') {
            profit = moneyValue * 0.063 * (dateValue / 365)
        }
        if (dateValue == '90') {
            profit = moneyValue * 0.068 * (dateValue / 365)
        }
        if (dateValue == '180') {
            profit = moneyValue * 0.07 * (dateValue / 365)
        }
        if (dateValue == '270') {
            profit = moneyValue * 0.075 * (dateValue / 365)
        }
        if (dateValue == '365') {
            profit = moneyValue * 0.078 * (dateValue / 365)
        }
        if (moneyValue < 10000) {
            $("#moneyValue").html(moneyValue);
        } else {
            $("#moneyValue").html((moneyValue / 10000) + "万");
        }
        $("#dateValue").html(dateValue);
        $("#profit").html(profit.toFixed(2));
    })
});
$("input[name='itd']").each(function(i) {
    $(this).click(function() {
        $('#jq22-circle-two').css("left", (41 + 131 * i) + "px");
        for (var mm = 0; mm < 6; mm++) {
            if (mm == i) {
                $(".date-value-pos label").eq(mm).css({
                    "font-size": "24px",
                    "color": "#ff1f38"
                });
                $(".date-value-pos .bubble").eq(mm).fadeIn();
            } else {
                $(".date-value-pos label").eq(mm).css({
                    "font-size": "16px",
                    "color": "#fe9196"
                });
                $(".date-value-pos .bubble").eq(mm).fadeOut();
            }
        }

        dateValue = $(this).val();
        moneyValue = $("input[name='mv']:checked").val();
        if (dateValue == '21') {
            profit = moneyValue * 0.1 * (dateValue / 365)
        }
        if (dateValue == '30') {
            profit = moneyValue * 0.063 * (dateValue / 365)
        }
        if (dateValue == '90') {
            profit = moneyValue * 0.068 * (dateValue / 365)
        }
        if (dateValue == '180') {
            profit = moneyValue * 0.07 * (dateValue / 365)
        }
        if (dateValue == '270') {
            profit = moneyValue * 0.075 * (dateValue / 365)
        }
        if (dateValue == '365') {
            profit = moneyValue * 0.078 * (dateValue / 365)
        }
        if (moneyValue < 10000) {
            $("#moneyValue").html(moneyValue);
        } else {
            $("#moneyValue").html((moneyValue / 10000) + "万");
        }
        $("#dateValue").html(dateValue);
        $("#profit").html(profit.toFixed(2));
    })
});
