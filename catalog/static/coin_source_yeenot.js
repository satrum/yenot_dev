function toggleColumn() {
$("td:nth-child("+8+"),td:nth-child("+9+"),td:nth-child("+10+"),td:nth-child("+11+"),td:nth-child("+12+"), td:nth-child("+13+"),td:nth-child("+14+"),td:nth-child("+15+"),td:nth-child("+16+"),th:nth-child("+8+"),th:nth-child("+9+"),th:nth-child("+10+"),th:nth-child("+11+"),th:nth-child("+12+"),th:nth-child("+13+"),th:nth-child("+14+"),th:nth-child("+15+"),th:nth-child("+16+")").hide();
$("td:nth-child("+17+"),td:nth-child("+18+"),td:nth-child("+19+"),td:nth-child("+20+"),td:nth-child("+21+"), td:nth-child("+22+"),th:nth-child("+17+"),th:nth-child("+18+"),th:nth-child("+19+"),th:nth-child("+20+"),th:nth-child("+21+"),th:nth-child("+22+")").show();
};
function toggleColumn2() {
$("td:nth-child("+8+"),td:nth-child("+9+"),td:nth-child("+10+"),td:nth-child("+11+"),td:nth-child("+12+"), td:nth-child("+13+"),td:nth-child("+14+"),td:nth-child("+15+"),td:nth-child("+16+"),th:nth-child("+8+"),th:nth-child("+9+"),th:nth-child("+10+"),th:nth-child("+11+"),th:nth-child("+12+"),th:nth-child("+13+"),th:nth-child("+14+"),th:nth-child("+15+"),th:nth-child("+16+")").show();
$("td:nth-child("+17+"),td:nth-child("+18+"),td:nth-child("+19+"),td:nth-child("+20+"),td:nth-child("+21+"), td:nth-child("+22+"),th:nth-child("+17+"),th:nth-child("+18+"),th:nth-child("+19+"),th:nth-child("+20+"),th:nth-child("+21+"),th:nth-child("+22+")").hide();

};
function rty() {
	$('.type_m2').replaceWith( "<div class=type_m onclick=javascript:toggleColumn2();qwe(this)> <h4 class=us_top_text_3>MARKET</h4></div>");
	$('.type_mt').replaceWith( "<div class=type_mt2 onclick=javascript:toggleColumn();rty(this)> <h4 class=us_top_text_3>SOCIAL</h4></div>");
};
function qwe() {
	$('.type_m').replaceWith( "<div class=type_m2 onclick=javascript:toggleColumn2();qwe(this)> <h4 class=us_top_text_3>MARKET</h4></div>");
	$('.type_mt2').replaceWith( "<div class=type_mt onclick=javascript:toggleColumn();rty(this)> <h4 class=us_top_text_3>SOCIAL</h4></div>");
};
 