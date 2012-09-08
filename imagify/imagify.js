//http://stackoverflow.com/questions/10812628/open-a-new-tab-in-the-background
function openNewBackgroundTab(url){
    var a = document.createElement("a");
    a.href = url;
    var evt = document.createEvent("MouseEvents");
    //the tenth parameter of initMouseEvent sets ctrl key
    evt.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0,
                                true, false, false, false, 0, null);
    a.dispatchEvent(evt);
}
function open(){
    $(this).addClass("clicked");
    openNewBackgroundTab($(this).attr("src"));
}


var container = $("<div>");
var imageURLs = $("a").not('[href^="#"]')
    .filter('[href*="jpg"],[href*="jpeg"]')
    .map(function(){
        return $(this).attr("href").trim();
    });
uniqueURLs = {};
jQuery.each(imageURLs,function(k,url){
    uniqueURLs[url] = true;
});


//console.debug(imageURLs);
//console.debug(uniqueURLs);

jQuery.each(uniqueURLs,function(url){
    container.append(
            $("<img/>")
            .attr("src",url)
            .load(function() {  
                //console.log($(this),$(this).width()); 
            })
            .click(open)
        ); 
});
var css = $("<link>").attr({"href":chrome.extension.getURL("imagify.css"),"rel":"stylesheet"});


var SPACE = 8;
var $document = $(document);
$(document).keypress(function(e) {
  var currScrollTop = $document.scrollTop() + SPACE;
  switch(e.which) {
    case 118:
        $("img").each(function(index){
            if($(this).offset().top - currScrollTop >= 0){
                open.call(this);
                return false;
            }
        });
        break;
    case 106:
        $("img").each(function(index){
            if($(this).offset().top - currScrollTop > 0){
                $document.scrollTop($(this).offset().top-SPACE);
                return false;
            }
        });
        break;
    case 107:
        $($("img").get().reverse()).each(function(index){
            if($(this).offset().top - currScrollTop < 0){
                $document.scrollTop($(this).offset().top-SPACE);
                return false;
            }
        });
        break;
  }
});

$("body, head").empty();
$("head").append(css);
$("body").append(container);