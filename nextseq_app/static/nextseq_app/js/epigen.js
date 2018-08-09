$.ajaxSetup({
    beforeSend: function(xhr, settings) {
	function getCookie(name) {
	    var cookieValue = null;
	    if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
		    var cookie = jQuery.trim(cookies[i]);
		    // Does this cookie string begin with the name we want?
		    if (cookie.substring(0, name.length + 1) == (name + '=')) {
			cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
			break;
		    }
		}
	    }
	    return cookieValue;
	}
	if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
	    // Only send the token to relative URLs i.e. locally.
	    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	}
    }
});


$(document).ready( function () {
    $('.datatable').DataTable();

    $('.datatablesort5').DataTable({
    	"order": [[ 5, "desc" ]]
    });

    $('.datatablesort2').DataTable({
    	"order": [[ 2, "desc" ]]
    });
    $('.datatablesort1').DataTable({
	"order": [[ 1, "asc" ]]
    });

    $( "#id_date" ).datepicker();
    
    $('.formset_row').formset({
	addText: 'add another samples',
	deleteText: 'remove',
	prefix: 'librariesinrun_set'
    });

    $(".dmpajax").on("click",function(e){
	e.preventDefault();

	var runinfoid = this.id;
	var runinfoiddate = 'date-'+this.id
	var that = this;
	var url1=$(this).attr("data-href");
	var url2=url1.replace("demultiplexing","demultiplexing2")

	$.ajax({
	    url:url1,
	    cache:false,
	    dataType: 'json',
	    success:function (data){
		if (!data.is_direxists){
		    alert('Error: None of the folder name contains '+runinfoid)
		    return
		}
		if (data.mkdirerror){
		    alert(data.mkdirerror)
		    return
		}
		if (data.mkdirerror2){
		    
		    if (!confirm(data.mkdirerror2)){
			return 
		    }else{
			
			// nested ajex call DemultiplexingView2 to continue
			$.ajax({
			    type:"POST",
			    url:url2,
			    cache:false,
			    data: {somedata: 'somedata'}
			})
			$("#"+runinfoiddate).text(data.updatedate)
			$(that).replaceWith('<span class="badge badge-success badge-status-blue">JobSubmitted</span>')

			return
		    }

		}
		
		if (data.writesamplesheeterror){
		    alert(data.writesamplesheeterror)
		    return
		}
		if (data.writetosamplesheet){
		    $("#"+runinfoiddate).text(data.updatedate)
		    // $(that).removeClass('btn btn-danger btn-sm btn-status-orange dmpajax')
		    // $(that).addClass('btn btn-success btn-sm btn-status-green disabled');
		    $(that).replaceWith('<span class="badge badge-success badge-status-blue">JobSubmitted</span>')

		    return
		}

	    }

	});
    })

} );
