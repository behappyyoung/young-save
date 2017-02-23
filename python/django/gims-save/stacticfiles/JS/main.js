$(function () {
    'use strict';
	if ( typeof $(".popup").draggable !== 'undefined'){
		$(".popup").draggable();	
	}
    
});
function go_cartagenia(){
    window.open("/mybackend/sso_cartagenia/", "_blank", 'height=800,width=1100');
}        