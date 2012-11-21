var itemtime = 6000;
var TimeToFade = 500.0;
var msgIteration = 0;

var currver = null;


function getTickerRSS(){
  
  /*=======================XML Ajax Request=======================
 *    Parse json in javascript from suke public absolute path
 *    Last edit: 10/20/2012 by Matt Gaffen
 *=======================XML Ajax Request=======================*/
  
  var xmlhttp;
  if (window.XMLHttpRequest){// code for IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp=new XMLHttpRequest();
  }
  else{// code for IE6, IE5
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  
  //What to do once recieving ajax response:
  
  xmlhttp.onreadystatechange=function(){
  if (xmlhttp.readyState==4 && xmlhttp.status==200){
      feed = xmlhttp.responseXML;
      ticker(feed, 0);
    }
  }
  
  
  /*As we're fetching public data use 'GET' rather than 'POST'
   *http://www.w3schools.com/ajax/ajax_xmlhttprequest_send.asp*/
  
  xmlhttp.open("GET","http://www.sukey.org/sukey/api/sukey-1.2.php",true);
  xmlhttp.send();
  
}


/*=======================Fade Animations=======================
 *    To replace jQuery Functionality. Could probably do with refactoring.
 *    Last edit: 10/20/2012 by Matt Gaffen
 *=======================Fade Animations=======================*/

//Fade timer function - can be re-used across the web app

function fade(eid){
  var element = document.getElementById('ticker');
  if(element.FadeState == null)
  {
    if(element.style.opacity == null
        || element.style.opacity == ''
        || element.style.opacity == '1')
    {
      element.FadeState = 2;
    }
    else
    {
      element.FadeState = -2;
    }
  }
   
  if(element.FadeState == 1 || element.FadeState == -1)
  {
    element.FadeState = element.FadeState == 1 ? -1 : 1;
    element.FadeTimeLeft = TimeToFade - element.FadeTimeLeft;
  }
  else
  {
    element.FadeState = element.FadeState == 2 ? -1 : 1;
    element.FadeTimeLeft = TimeToFade;
    setTimeout("animateFade(" + new Date().getTime() + ",'" + eid + "')", 33);
  }  
}

//Fade animation function - can be re-used across the web app

function animateFade(lastTick, eid)
{  
  var curTick = new Date().getTime();
  var elapsedTicks = curTick - lastTick;
 
  var element = document.getElementById(eid);
 
  if(element.FadeTimeLeft <= elapsedTicks)
  {
    element.style.opacity = element.FadeState == 1 ? '1' : '0';
    element.style.filter = 'alpha(opacity = '
        + (element.FadeState == 1 ? '100' : '0') + ')';
    element.FadeState = element.FadeState == 1 ? 2 : -2;
    return;
  }
 
  element.FadeTimeLeft -= elapsedTicks;
  var newOpVal = element.FadeTimeLeft/TimeToFade;
  if(element.FadeState == 1)
    newOpVal = 1 - newOpVal;

  element.style.opacity = newOpVal;
  element.style.filter = 'alpha(opacity = ' + (newOpVal*100) + ')';
 
  setTimeout("animateFade(" + curTick + ",'" + eid + "')", 33);
}


//Iterate Through Updates

function switchStatus(list, num){
  fade('ticker');
  setTimeout(function(){document.getElementById("ticker").innerHTML=
  list.getElementsByTagName("tickertext")[msgIteration].childNodes[0].nodeValue}, TimeToFade);
  setTimeout(function(){fade('ticker')}, TimeToFade);
  msgIteration++
  alert(list.getElementsByTagName("tickertext").length);
}


/*=======================Initiate Ticker=======================
 *    Begin iterating through updates
 *    Last edit: 10/20/2012 by Matt Gaffen
 *=======================Initiate Ticker=======================*/

function ticker(list){
	setInterval(function(){
    fade('ticker');
    setTimeout(function(){
      
      var timestamp = list.getElementsByTagName("published")[msgIteration].childNodes[0].nodeValue;
      var date = new Date(timestamp*1000);
      
      document.getElementById("ticker").innerHTML=
      list.getElementsByTagName("tickertext")[msgIteration].childNodes[0].nodeValue
      + "<br/><br/>"
      + date.getDate() + ", " + date.getMonth() + ", " + date.getUTCFullYear()
    }, TimeToFade);
    setTimeout(function(){fade('ticker')}, TimeToFade);
    if(msgIteration >= list.getElementsByTagName("tickertext").length - 1){
      msgIteration = 0
    } else {
      msgIteration++
    }
  }, itemtime);
}
