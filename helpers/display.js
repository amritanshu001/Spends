$(document).ready(function() {
    $("td.tooltipTrigger").hover(function () {
        $(this).children("span.tooltip").show()
    },
    function() {
        $(this).children("span.tooltip").hide()
    })
})