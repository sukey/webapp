function show(id) {
  document.getElementById('nav').style.display = 'none';
  document.getElementById('activate').style.display = 'none';
  document.getElementById('report').style.display = 'none';
  document.getElementById('map-page').style.display = 'none';
  document.getElementById('about').style.display = 'none';
  document.getElementById('feedback').style.display = 'none';
  
  document.getElementById(id.substr(1)).style.display = 'block';
}
if (location.hash === ''){
  show('#nav');
} else {
  show(location.hash);
}
window.onhashchange = function(){
    show(location.hash);
}