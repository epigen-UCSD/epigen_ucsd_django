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
    prefix: 'samplesinrun_set'
});

} );
