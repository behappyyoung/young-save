$(function () {
    'use strict';
	if ( typeof $(".popup").draggable !== 'undefined'){
		$(".popup").draggable();	
	}
    
});
function get_current_date(){
    var d = new Date,
    dformat = [d.getFullYear() ,d.getMonth()+1,
               d.getDate()
               ].join('-')+' '+
              [d.getHours(),
               d.getMinutes(),
               d.getSeconds()].join(':');
    return dformat;
}
function go_cartagenia(){
    window.open("/mybackend/sso_cartagenia/", "_blank", 'toolbar,resizable');
}        

function user_message(mtype, msg, refresh=false){
    var yes_html ='';
	if(mtype=='error'){
		$('#modal-title').html('Error Message');
        yes_html = ' <button type="button" class="btn btn-default" data-dismiss="modal" >Close</button>';

	}else if(mtype=='status'){
 		$('#modal-title').html('Status');
        yes_html = ' <button type="button" class="btn btn-default" data-dismiss="modal" >Close</button>';

    }else if(mtype == 'wait'){
        $('#modal-title').html('Please Wait');
         msg = msg +  '<img class="wait-image" src="/static/IMAGES/icon_spinner.gif" />';
 	}else{
        $('#modal-title').html(mtype);
        yes_html = ' <button type="button" class="btn btn-default" data-dismiss="modal" >Close</button>';

    }
    $('#yes-button').html(yes_html);
    $('#model-message').html(msg);
    
    $('#gimsModal').modal("show");
    if(refresh){
         setTimeout(function() {
                window.location.reload();
        }, 1000);   
    }
 }
function confirm_message(submit_title="Confirm", msg='Ready?', f_arg='', f_name='afterConfirmed'){
    var f_name = (f_name=='')? 'afterConfirmed' : f_name;
    $('#modal-title').html(submit_title);
    $('#model-message').html(msg);
    $('#yes-button').html(' <button type="button" class="btn btn-default" data-dismiss="modal" >Cancel</button>\
        <button type="button" class="btn btn-primary" data-dismiss="modal" onClick="'+f_name+'(\''+f_arg+'\')">Confirm</button>');
    $('#gimsModal').modal("show");
 }

 function submit_form(form_id){
    form_id.submit();
 }
 function confirm_submit(form_id, msg='Ready to submit change?', submit_title="Submit Changes"){
    $('#modal-title').html(submit_title);
    $('#model-message').html(msg);
    $('#yes-button').html(' <button type="button" class="btn btn-default" data-dismiss="modal" >Cancel</button>\
        <button type="button" class="btn btn-primary" data-dismiss="modal" onClick="submit_form(' + form_id + ')">Submit</button>');
    $('#gimsModal').modal("show");
 }
function OpenPopupCenter(pageURL, title, w, h) {
            // var left = (screen.width - w) / 4;
            var popleft = window.screenLeft + 300;
            var poptop = (screen.height - h) / 4;  // for 25% - devide by 4  |  for 33% - devide by 3
            // console.log(pageURL, popleft, poptop, w, h);
            popupWin = window.open(pageURL, title, 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width=' + w + ', height=' + h + ', top=' + poptop + ', left=' + popleft);
} 