/* using jquey live for events on the nav li elements. this needs to be wired to show/hide sections and also history.js - https://github.com/balupton/History.js */

$('nav#main li').on({
	click: function(e) {
		var t = $(this);
		var target = t.data('target');
		console.log(target);
	}
})