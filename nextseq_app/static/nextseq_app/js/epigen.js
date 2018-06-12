$(document).ready( function () {
    $('.datatable').DataTable();

    $( "#id_date" ).datepicker();
    
    $('.formset_row').formset({
    addText: 'add another samples',
    deleteText: 'remove',
    prefix: 'samplesinrun_set'
});

} );
