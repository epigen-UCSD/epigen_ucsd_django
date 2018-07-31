$(document).ready( function () {
    $('.datatable').DataTable();

    $('.datatablesort5').DataTable({
    	"order": [[ 5, "desc" ]]
    });

    $('.datatablesort2').DataTable({
    	"order": [[ 2, "desc" ]]
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
    $.ajax({
      url:$(this).attr("data-href"),
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
