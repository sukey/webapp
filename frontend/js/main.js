/* lib - all in one file for speed */

/**
 * Copyright (c) 2007-2012 Ariel Flesler - aflesler(at)gmail(dot)com | http://flesler.blogspot.com
 * Dual licensed under MIT and GPL.
 * @author Ariel Flesler
 * @version 1.4.3.1
 */
;(function($){var h=$.scrollTo=function(a,b,c){$(window).scrollTo(a,b,c)};h.defaults={axis:'xy',duration:parseFloat($.fn.jquery)>=1.3?0:1,limit:true};h.window=function(a){return $(window)._scrollable()};$.fn._scrollable=function(){return this.map(function(){var a=this,isWin=!a.nodeName||$.inArray(a.nodeName.toLowerCase(),['iframe','#document','html','body'])!=-1;if(!isWin)return a;var b=(a.contentWindow||a).document||a.ownerDocument||a;return/webkit/i.test(navigator.userAgent)||b.compatMode=='BackCompat'?b.body:b.documentElement})};$.fn.scrollTo=function(e,f,g){if(typeof f=='object'){g=f;f=0}if(typeof g=='function')g={onAfter:g};if(e=='max')e=9e9;g=$.extend({},h.defaults,g);f=f||g.duration;g.queue=g.queue&&g.axis.length>1;if(g.queue)f/=2;g.offset=both(g.offset);g.over=both(g.over);return this._scrollable().each(function(){if(e==null)return;var d=this,$elem=$(d),targ=e,toff,attr={},win=$elem.is('html,body');switch(typeof targ){case'number':case'string':if(/^([+-]=)?\d+(\.\d+)?(px|%)?$/.test(targ)){targ=both(targ);break}targ=$(targ,this);if(!targ.length)return;case'object':if(targ.is||targ.style)toff=(targ=$(targ)).offset()}$.each(g.axis.split(''),function(i,a){var b=a=='x'?'Left':'Top',pos=b.toLowerCase(),key='scroll'+b,old=d[key],max=h.max(d,a);if(toff){attr[key]=toff[pos]+(win?0:old-$elem.offset()[pos]);if(g.margin){attr[key]-=parseInt(targ.css('margin'+b))||0;attr[key]-=parseInt(targ.css('border'+b+'Width'))||0}attr[key]+=g.offset[pos]||0;if(g.over[pos])attr[key]+=targ[a=='x'?'width':'height']()*g.over[pos]}else{var c=targ[pos];attr[key]=c.slice&&c.slice(-1)=='%'?parseFloat(c)/100*max:c}if(g.limit&&/^\d+$/.test(attr[key]))attr[key]=attr[key]<=0?0:Math.min(attr[key],max);if(!i&&g.queue){if(old!=attr[key])animate(g.onAfterFirst);delete attr[key]}});animate(g.onAfter);function animate(a){$elem.animate(attr,f,g.easing,a&&function(){a.call(this,e,g)})}}).end()};h.max=function(a,b){var c=b=='x'?'Width':'Height',scroll='scroll'+c;if(!$(a).is('html,body'))return a[scroll]-$(a)[c.toLowerCase()]();var d='client'+c,html=a.ownerDocument.documentElement,body=a.ownerDocument.body;return Math.max(html[scroll],body[scroll])-Math.min(html[d],body[d])};function both(a){return typeof a=='object'?a:{top:a,left:a}}})(jQuery);

/* new map init function */
/* however I don't understand all the js in here as some is just copied across */
var map;
function initmap() {
	var options = {
		center: new L.LatLng(51.53024, -0.07400),
		zoom: 11,
		scrollWheelZoom: false
	};

	var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib = 'Map data &copy; OpenStreetMap contributors';
	
	var tiles = new L.TileLayer(osmUrl, {
		maxZoom: 18,
		attribution: osmAttrib
	});
	this.map = new L.Map('map', options)
	this.map.addLayer(tiles);
/* 	geolocate and don't follow */
	this.map.locate({setView: true, watch: false});
	

	map.on({
		click: function(e) {
			var latlngStr = '(' + e.latlng.lat.toFixed(3) + ', ' + e.latlng.lng.toFixed(3) + ')';

			popup.setLatLng(e.latlng);
			popup.setContent(latlngStr);
			map.openPopup(popup);
		},
		locationfound: function(e) {

		var radius = e.accuracy / 2;

		var marker = new L.Marker(e.latlng);
		map.addLayer(marker);

			var circle = new L.Circle(e.latlng, radius);
			map.addLayer(circle);

	var WifiIcon = L.Icon.extend({
			iconUrl: 'wifi.png',
			shadowUrl: null,
			iconSize: new L.Point(32, 37),
			shadowSize: null,
			iconAnchor: new L.Point(14, 37),
			popupAnchor: new L.Point(2, -32)
		});

		var geojsonLayer = new L.GeoJSON(null, {
		    pointToLayer: function (latlng){
		        return new L.CircleMarker(latlng, {
		            radius: 8,
		            fillColor: "#ff7800",
		            color: "#000",
		            weight: 1,
		            opacity: 1,
		            fillOpacity: 0.8
		        });
		    }
		});

		var wifiJSON = new L.GeoJSON(fsWifi, {
		    pointToLayer: function (latlng){
		        return new L.Marker(latlng, {
		            icon: new WifiIcon()
		        });
		    }
		});

		geojsonLayer.on("featureparse", function (e) {
		    var popupContent = "";
		    if (e.geometryType == "Point") {
		        popupContent += "<p></p>";
		    }
		    if (e.properties && e.properties.popupContent) {
		        popupContent += e.properties.popupContent;
		    }
		    e.layer.bindPopup(popupContent);
		    if (e.properties && e.properties.style && e.layer.setStyle) {
		        e.layer.setStyle(e.properties.style);
		    }
		});

		wifiJSON.on("featureparse", function (e) {
		    var popupContent = "<p></p>";
		    popupContent += "<p></p>";
		    if (e.properties && e.properties.popupContent) {
		        popupContent += e.properties.popupContent;
		    }
		    e.layer.bindPopup(popupContent);
		});


		map.addLayer(wifiJSON);

		wifiJSON.addGeoJSON(fsWifi);
		wifiJSON.addGeoJSON(converted_json);
	
		}
	});
}

	var views = $('section.view');
	var hash = location.hash.substring(3);

$(document).ready(function() {

/* checks if the url has a location hash and goes to view if so */
	if (hash.length) {
		toView(hash);
	} else {
/* this scrolls down 1 px on load to hide safari mobile status bar [might work on other mobile browsers] */
		setTimeout(function() {window.scrollTo(0, 1);}, 0);
	}

/* set map window height - 40 */
	$('#map').height($(window).height()-40);
	
/* set useragent string for feedback form */
	$('input#useragent').val(navigator.userAgent);

/* using jquery live for events on the nav li elements. this could be wired to history.js - https://github.com/balupton/History.js */
	$('nav#main li').on({
		click: function(e) {
			var t = $(this);
			var target = t.data('target');			
			toView(target);
		}
	});

});

function toView(target) {
	var targetel = $('#' + target);
	views.hide();
	targetel.show();
	location.hash = '!/' + target;
	var t = setTimeout(function() {
		$(window).scrollTo(targetel, 1);
		if (target == 'map-view') {
			initmap();
		}
	}, 1);
};
