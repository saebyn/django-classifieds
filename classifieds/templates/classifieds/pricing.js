var prices = {
{% for price in prices %}
{{ price.pk }}: {{ price.price }},
{% endfor %}
};
var pricing_options = {
{% for option in options %}
{{ option.pk }}: {{ option.price }},
{% endfor %}
};

$(document).ready( function () {
	$("input[name='pricing'], input[name='pricing_options']").change( function () {
		var price = prices[$("input[name='pricing']:checked").val()];
		if ( price == undefined )
			price = 0;
		
		var options = $("input[name='pricing_options']:checked");
		options.each ( function (i) {
			price += pricing_options[$(options[i]).val()];
		});
		var strprice = '' + price;
		
		decimal = strprice.split('.')[1];
		if ( decimal == undefined )
			strprice += '.00';
		else if ( decimal.length == 1 )
			strprice += '0';
		else if ( decimal.length > 2 ) {
			strprice = '' + (price + 0.01);
			strprice = strprice.substr(0, strprice.indexOf('.')+3);
		}
		
		$("#total").text("$" + strprice);
	});
});
