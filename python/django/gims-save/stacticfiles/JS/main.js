$(function () {
    'use strict';
	if ( typeof $(".popup").draggable !== 'undefined'){
		$(".popup").draggable();	
	}
    
});
function go_cartagenia(){
    window.open("/mybackend/sso_cartagenia/", "_blank", 'height=800,width=1100');
}        

function user_message(mtype, msg, refresh=false){
	if(mtype=='error'){
		$('#modal-title').html('Error Message');
	}else if(mtype=='status'){
 		$('#modal-title').html(mtype + ' Message');
 	}else{
        $('#modal-title').html(mtype);
    }

    $('#model-message').html(msg);
    $('#yes-button').html(' <button type="button" class="btn btn-default" data-dismiss="modal" >Close</button>')
    $('#gimsModal').modal("show");
    if(refresh){
    	window.location.reload();
    }
 }