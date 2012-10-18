var map = new L.Map('map');

var cloudmadeUrl = 'http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/997/256/{z}/{x}/{y}.png',
  cloudmadeAttribution = 'Map data &copy; 2011 OpenStreetMap contributors, Imagery &copy; 2011 CloudMade',
  cloudmade = new L.TileLayer(cloudmadeUrl, {maxZoom: 18, attribution: cloudmadeAttribution});

map.on('click', onMapClick);

var popup = new L.Popup();

map.addLayer(cloudmade);
map.on('locationfound', onLocationFound);
map.on('locationerror', onLocationError);
map.locateAndSetView();

function onMapClick(e) {
  var latlngStr = '(' + e.latlng.lat.toFixed(3) + ', ' + e.latlng.lng.toFixed(3) + ')';

  popup.setLatLng(e.latlng);
  popup.setContent(latlngStr);
  map.openPopup(popup);
}

function onLocationFound(e) {
  var radius = e.accuracy / 2;

  //var circle = new L.Circle(e.latlng, radius);
  //map.addLayer(circle);

  //latlng type http://leaflet.cloudmade.com/reference.html#latlngs
  var latlng = new L.LatLng(51.53024, -0.07400);
  
  var latlngs=new Array();
        latlngs[0]=e.latlng; //LatLng(51.53024, -0.07634) (when testing from London Hackspace quiet room) :p
        latlngs[1]=latlng; //LatLng(51.53024, -0.07400);
        
  // create a red polyline from an arrays of LatLng points
  var polyline = new L.Polyline(latlngs, {color: 'red'});
  // zoom the map to the polyline
  map.fitBounds(new L.LatLngBounds(latlngs));

        var marker = new L.Marker(latlngs[0]);
  var marker2 = new L.Marker(latlngs[1]);
        // add the polyline to the map
        map.addLayer(polyline);
      map.addLayer(marker);
      map.addLayer(marker2);
  marker.bindPopup("The value of latlngs[0] is " + latlngs[0]).openPopup();
  marker2.bindPopup("The value of latlngs[0] is " + latlngs[1]).openPopup();
  
  var p1 = latlngs[0],
  p2 = latlngs[1],
  p3 = new L.LatLng(51.528, -0.07400),
  p4 = new L.LatLng(51.528, -0.07634),
  polygonPoints = [p1, p2, p3, p4],
  polygon = new L.Polygon(polygonPoints);

polygon.bindPopup("Herp, Derp, I am a Square.");
map.addLayer(polygon);

}

function onLocationError(e) {
  alert(e.message);
}