var itemtime = 5000;

var currver = null;

function getTickerRSS(){
	jQuery.ajax({
		url: "../../sukey/api/sukey-1.2.php",
		success: function(data){
			var sukey = jQuery(data).children('sukey');
			var ver = sukey.attr('version');
			if ((currver !== null) && (ver != currver))
				window.location.reload(true);
			currver = ver;
			var anns = sukey.find('tickertext').contents();
			ticker(anns,0);
		}
	});
}

function ticker(list,num){
	if(num >= list.length){
		setTimeout(getTickerRSS,itemtime);
	}else{
		jQuery("#ticker").animate(
			{ opacity: 0 }, 500,
			function() { jQuery(this).text(jQuery(list[num]).text()) })
		.animate(
			{ opacity: 1 }, 500,
			function() { setTimeout(function() { ticker(list, num+1) }, itemtime) });
	}
}
