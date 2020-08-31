$.ajaxSetup({
    beforeSend: function (xhr, settings) {
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


$(document).ready(function () {

    // datatable js related
    // https://stackoverflow.com/questions/10630853/change-values-of-select-box-of-show-10-entries-of-jquery-datatable
    $('.datatable').DataTable({
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20
    });

    $('.datatablesort5').DataTable({
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[5, "desc"]]
    });

    $('.datatablesort2').DataTable({
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[2, "desc"]]
    });

    $('.datatablesort1').DataTable({
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[1, "asc"]]
    });


    $('#datatabledetailnotes').DataTable({
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[3, "desc"], [1, "desc"]],
        "columnDefs": [{
            "orderable": false,
            "targets": [0, -1, -2],
        },
            // {
            //  "className": 'details-control',
            //  "targets": 0,
            // }

        ]

    });

    $('#datatabledetailnotes2').DataTable({
        "order": [[2, "desc"]],
        "columnDefs": [{
            "orderable": false,
            "targets": [0],
        },

        ]

    });

    $('#datatabledetailnotes tbody').on('click', 'td.details-control', function () {
        var thisurl = $(this).attr("data-href");
        var tr = $(this).closest('tr');
        if ($(this).hasClass("closing")) {
            $(this).removeClass("closing")
            tr.next().closest(".detailnotes").remove()
        }
        else {
            $(this).addClass("closing")

            $.ajax({
                url: thisurl,
                cache: false,
                dataType: 'json',
                success: function (data) {

                    if (data.notes) {
                        tr.after('<tr class="detailnotes"><td class="detailnotes" colspan="8"><div class="detailnotes">Notes:' + data.notes + '</div></td></tr>')


                    }
                }
            })

        }

    });

    $('#datatabledetailnotes2 tbody').on('click', 'td.details-control', function () {
        var thisurl = $(this).attr("data-href");
        var tr = $(this).closest('tr');
        if ($(this).hasClass("closing")) {
            $(this).removeClass("closing")
            tr.next().closest(".detailnotes").remove()


        }
        else {
            $(this).addClass("closing")

            $.ajax({
                url: thisurl,
                cache: false,
                dataType: 'json',
                success: function (data) {

                    if (data.notes) {
                        tr.after('<tr class="detailnotes"><td class="detailnotes" colspan="8"><div class="detailnotes">Notes:' + data.notes + '</div></td></tr>')


                    }
                }
            })

        }

    });


    $('#collab_setqcs_user tbody').on('click', 'td.details-control', function () {
        var thisurl = $(this).attr("data-href");
        var tr = $(this).closest('tr');
        if ($(this).hasClass("closing")) {
            $(this).removeClass("closing")
            tr.next().closest(".detailnotes").remove()
        }
        else {
            $(this).addClass("closing")

            $.ajax({
                url: thisurl,
                cache: false,
                dataType: 'json',
                success: function (data) {

                    if (data.notes) {
                        tr.after('<tr class="detailnotes"><td class="detailnotes" colspan="8"><div class="detailnotes">Notes:' + data.notes + '</div></td></tr>')


                    }
                }
            })

        }

    });

    $('select#nextseq_app_machine').on('change', function () {
        console.log(this.value);
        if (this.value.startsWith('IGM_')) {
            console.log('ffffff');
            document.getElementById('id_Flowcell_ID').value = 'TBD_' + Math.floor(Math.random() * 1000);

        }
        else {
            document.getElementById('id_Flowcell_ID').value = '';
        }
    });



    var samplesurl = $('#collab_samples').attr("data-href");
    $('#collab_samples').DataTable({
        "iDisplayLength": 10,
        "processing": true,
        "ajax": {
            url: samplesurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "sample_id" },
            { "data": "date" },
            { "data": "sample_type" },
            { "data": "service_requested" },
            { "data": "status" },
        ],
        "deferRender": true,
        "select": true,

        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a href="/epigen/samples/' + itemID + '">' + data + '</a>';
            }
        }],
    });



    $('#collab_samples_com').DataTable({

    })



    var metasampsurl = $('#collab_metadata_samples').attr("data-href");
    $('#collab_metadata_samples').DataTable({
        dom: 'lBfrtip',
        buttons: [
            'excel',
            {
                text: 'TSV',
                extend: 'csvHtml5',
                fieldSeparator: '\t',
                extension: '.tsv',
                fieldBoundary: ''
            }
        ],
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[2, "desc"]],
        "processing": true,
        "ajax": {
            url: metasampsurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "sample_id" },
            { "data": "description" },
            { "data": "date" },
            { "data": "group__name" },
            { "data": "sample_type" },
            { "data": "status" },
        ],
        "deferRender": true,
        "select": true,

        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
            }
        }],
    });


    $('#seqmanager_seq').DataTable({
        dom: 'lBfrtip',
        buttons: [
            'excel',
            {
                text: 'TSV',
                extend: 'csvHtml5',
                fieldSeparator: '\t',
                extension: '.tsv',
                fieldBoundary: ''
            }
        ],
        "select": true,
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[1, "asc"]],
    });




    var metalibsurl = $('#collab_metadata_libs').attr("data-href");
    $('#collab_metadata_libs').DataTable({
        dom: 'lBfrtip',
        buttons: [
            'excel',
            {
                text: 'TSV',
                extend: 'csvHtml5',
                fieldSeparator: '\t',
                extension: '.tsv',
                fieldBoundary: ''
            }
        ],
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "processing": true,
        "order": [[7, "desc"]],
        "ajax": {
            url: metalibsurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "library_id" },
            { "data": "library_description" },
            { "data": "sampleinfo__sample_id" },
            { "data": "sampleinfo__sample_type" },
            { "data": "sampleinfo__description" },
            { "data": "sampleinfo__species" },
            { "data": "sampleinfo__group__name" },
            { "data": "date_started" },
            { "data": "experiment_type" },
        ],
        "deferRender": true,
        "select": true,

        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a href="/metadata/lib/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 2,
            "render": function (data, type, row) {
                var itemID = row["sampleinfo__id"];
                return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
            }
        },

        ],
    });



    var metaseqsurl = $('#collab_metadata_seqs').attr("data-href");
    $('#collab_metadata_seqs').DataTable({
        dom: 'lBfrtip',
        buttons: [
            'excel',
            {
                text: 'TSV',
                extend: 'csvHtml5',
                fieldSeparator: '\t',
                extension: '.tsv',
                fieldBoundary: ''
            }
        ],
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "processing": true,
        "order": [[5, "desc"]],
        "ajax": {
            url: metaseqsurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "seq_id" },
            { "data": "libraryinfo__library_description" },
            { "data": "libraryinfo__sampleinfo__sample_id" },
            { "data": "libraryinfo__sampleinfo__description" },
            { "data": "libraryinfo__sampleinfo__group__name" },
            { "data": "date_submitted_for_sequencing" },
            { "data": "machine__sequencing_core" },
            { "data": "portion_of_lane" },
            { "data": "read_length" },
            { "data": "read_type" },

        ],
        "deferRender": true,
        "select": true,

        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a href="/metadata/seq/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 2,
            "render": function (data, type, row) {
                var itemID = row["libraryinfo__sampleinfo__id"];
                return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 6,
            "render": function (data, type, row) {
                if (row["machine__sequencing_core"] == null) {
                    return ''
                }
                else {
                    return row["machine__sequencing_core"] + '_' + row["machine__machine_name"];
                }
            }
        },
        ],
    });



    var usersetqcsurl = $('#collab_setqcs_user').attr("data-href");
    $('#collab_setqcs_user').DataTable({
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[2, "desc"]],
        "processing": true,
        "ajax": {
            url: usersetqcsurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "notes" },
            { "data": "set_id" },
            { "data": "set_name" },
            { "data": "last_modified" },
            { "data": "experiment_type" },
            { "data": "url" },
            { "data": "status" },
        ],
        "deferRender": true,
        "select": false,

        "columnDefs": [{
            "targets": 0,
            "createdCell": function (td, data, row, col) {
                var itemID = row["pk"];
                var n = row["notes"];
                if (n) {
                    $(td).addClass('details-control');
                    $(td).attr('data-href', '{% url \'collaborator_app:setqc_getnotes\' ' + itemID + ' %}');
                    $(td).text('');

                }
                else {
                    $(td).text('');
                }

            }

        },
        {
            "targets": 1,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 3,
            "render": function (data, type, row) {
                var date = row["last_modified"];
                var dt = new Date(date);
                var y = dt.getFullYear();
                var m = dt.getMonth() + 1;
                var d = dt.getDate();
                return y + '-' + (m <= 9 ? '0' + m : m) + '-' + (d <= 9 ? '0' + d : d);


            }
        },
        {
            "targets": 5,
            "render": function (data, type, row) {
                var reporturl = row["url"];
                if (reporturl) {
                    return '<a href="' + reporturl + '" target="_blank"><i class="fas fa-file-alt" style="font-size: 17px;color:#26D07C"></i></a>'
                }
                else {
                    return ''
                }

            }
        }],
    });




    var servicerequesturl = $('#service_request_all').attr("data-href");
    $('#service_request_all').DataTable({
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[1, "desc"]],
        "processing": true,
        "ajax": {
            url: servicerequesturl,
            dataSrc: ''
        },
        "columns": [
            { "data": "service_request_id" },
            { "data": "date" },
            { "data": "group" },
            { "data": "institute" },
            { "data": "research_contact" },
            { "data": "research_contact_email" },
            { "data": "quote_number" },
            { "data": "status" },

        ],
        "deferRender": true,
        "select": false,

        "columnDefs": [

        {
            "targets": 0,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                if (data == null) {
                    return ''
                }
                else {
                    return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
                }
            }
        },

        {
            "targets": 6,
            "render": function (data, type, row) {
                var returnvalue = ''
                
                for (i = 0; i < data.length; i++) {
                  var qid = data[i].replace(/ /g, "");
                  var returnvalue = returnvalue.concat('<a class="spacing-big" href="/manager/quote/'+qid+'/",data-toggle="tooltip" data-placement="right" title="'+data[i]+'" width="300"><i class="fas fa-file-alt" style="font-size: 17px;color:#0a2a66"></i></a>')
                }

                if (row["status"] == 'initiate'){
                    return returnvalue.concat('<a class="spacing" href="/manager/quote/' + qid + '/text_update/"><i class="fas fa-edit"></i></a>')
                }
                else{
                    return returnvalue
                }   
                

            }
        },
        {
            "targets": 8,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a class="spacing" href="/manager/servicerequest_update/' + itemID + '/"><i class="fas fa-edit"></i></a><a class="spacing" href="/manager/add_new_quote/' + itemID + '/"><i class="fas fa-plus"></i></a>'
                

            }
        }],
    });


    var quotesurl = $('#quotes_all').attr("data-href");
    $('#quotes_all').DataTable({
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[2, "desc"]],
        "processing": true,
        "ajax": {
            url: quotesurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "quote_number" },
            { "data": "service_request_id" },
            { "data": "date" },
            { "data": "group" },
            { "data": "research_contact" },
            { "data": "quote_amount" },
            { "data": "quote_pdf" },
        ],
        "deferRender": true,
        "select": false,

        "columnDefs": [

        {
            "targets": 1,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                if (data == null) {
                    return ''
                }
                else {
                    return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
                }
                
            }
        },
        {
            "targets": 6,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                var qid = row["quote_number"].replace(/ /g, "")
                if (data) {
                    return '<a class="spacing-big" href="/manager/quote/'+qid+'/" width="300"><i class="fas fa-file-alt" style="font-size: 17px;color:#0a2a66"></i></a>'
                }
                else {
                    return '';
                }
                
            }
        },

        {
            "targets": 7,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                var qid = row["quote_number"].replace(/ /g, "")
                return '<a class="spacing" href="/manager/quote_upload/' + itemID + '/' + qid + '/"><i class="fas fa-upload"></i></a><a class="spacing" href="/manager/quote_update/' + itemID + '/'+ qid + '/"><i class="fas fa-edit"></i></a><a onclick="return confirm(\'Are you sure you want to delete quote ' + row["quote_number"] + '?\');" href="/manager/quote_delete/' + itemID + '/'+ qid + '/"><i class="fas fa-trash-alt"></i></a>'
                

            }
        }],
    });



    var metasampsurl = $('#metadata_samples').attr("data-href");
    $('#metadata_samples').DataTable({
        dom: 'lBfrtip',
        buttons: [
            'excel',
            {
                text: 'TSV',
                extend: 'csvHtml5',
                fieldSeparator: '\t',
                extension: '.tsv',
                fieldBoundary: ''
            }
        ],
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[2, "desc"], [3, "desc"]],
        "processing": true,
        "ajax": {
            url: metasampsurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "sample_id" },
            { "data": "description" },
            { "data": "date" },
            { "data": "group__name" },
            { "data": "sample_type" },
            { "data": "status" },
        ],
        "deferRender": true,
        "select": true,

        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
            }
        }],
    });

    var metasampsurl = $('#metadata_samples_bio').attr("data-href");
    $('#metadata_samples_bio').DataTable({
        dom: 'lBfrtip',
        buttons: [
            'excel',
            {
                text: 'TSV',
                extend: 'csvHtml5',
                fieldSeparator: '\t',
                extension: '.tsv',
                fieldBoundary: ''
            }
        ],
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[2, "desc"], [3, "desc"]],
        "processing": true,
        "ajax": {
            url: metasampsurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "sample_id" },
            { "data": "description" },
            { "data": "date" },
            { "data": "group__name" },
            { "data": "sample_type" },
            { "data": "status" },
            { "data": null, defaultContent: "" },
        ],
        "deferRender": true,
        "select": true,

        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 6,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a class="spacing" href="/metadata/sample/' + itemID + '/update/"><i class="fas fa-edit"></i></a><a onclick="return confirm(\'Are you sure you want to delete sample ' + row["sample_id"] + '?\');" href="/metadata/sample/' + itemID + '/delete/"><i class="fas fa-trash-alt"></i></a>';
            }

        }],
    });

    var metalibsurl = $('#metadata_libs').attr("data-href");
    $('#metadata_libs').DataTable({
        dom: 'lBfrtip',
        buttons: [
            'excel',
            {
                text: 'TSV',
                extend: 'csvHtml5',
                fieldSeparator: '\t',
                extension: '.tsv',
                fieldBoundary: ''
            }
        ],
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "processing": true,
        "order": [[7, "desc"], [6, "desc"]],
        "ajax": {
            url: metalibsurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "library_id" },
            { "data": "library_description" },
            { "data": "sampleinfo__sample_id" },
            { "data": "sampleinfo__sample_type" },
            { "data": "sampleinfo__description" },
            { "data": "sampleinfo__species" },
            { "data": "sampleinfo__group__name" },
            { "data": "date_started" },
            { "data": "experiment_type" },
        ],
        "deferRender": true,
        "select": true,

        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a href="/metadata/lib/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 2,
            "render": function (data, type, row) {
                var itemID = row["sampleinfo__id"];
                return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
            }
        },

        ],
    });

    var metalibsurl = $('#metadata_libs_bio').attr("data-href");
    $('#metadata_libs_bio').DataTable({
        dom: 'lBfrtip',
        buttons: [
            'excel',
            {
                text: 'TSV',
                extend: 'csvHtml5',
                fieldSeparator: '\t',
                extension: '.tsv',
                fieldBoundary: ''
            }
        ],
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "order": [[7, "desc"], [6, "desc"]],
        "processing": true,
        "ajax": {
            url: metalibsurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "library_id" },
            { "data": "library_description" },
            { "data": "sampleinfo__sample_id" },
            { "data": "sampleinfo__sample_type" },
            { "data": "sampleinfo__description" },
            { "data": "sampleinfo__species" },
            { "data": "sampleinfo__group__name" },
            { "data": "date_started" },
            { "data": "experiment_type" },
            { "data": null, defaultContent: "" },
        ],
        "deferRender": true,
        "select": true,

        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a href="/metadata/lib/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 2,
            "render": function (data, type, row) {
                var itemID = row["sampleinfo__id"];
                return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 9,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a class="spacing" href="/metadata/lib/' + itemID + '/update/"><i class="fas fa-edit"></i></a><a onclick="return confirm(\'Are you sure you want to delete library ' + row["library_id"] + '?\');" href="/metadata/lib/' + itemID + '/delete/"><i class="fas fa-trash-alt"></i></a>';
            }

        }
        ],
    });


    var metaseqsurl = $('#metadata_seqs').attr("data-href");
    $('#metadata_seqs').DataTable({
        dom: 'lBfrtip',
        buttons: [
            'excel',
            {
                text: 'TSV',
                extend: 'csvHtml5',
                fieldSeparator: '\t',
                extension: '.tsv',
                fieldBoundary: ''
            }
        ],
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "processing": true,
        "order": [[5, "desc"], [4, "desc"]],
        "ajax": {
            url: metaseqsurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "seq_id" },
            { "data": "libraryinfo__library_description" },
            { "data": "libraryinfo__sampleinfo__sample_id" },
            { "data": "libraryinfo__sampleinfo__description" },
            { "data": "libraryinfo__sampleinfo__group__name" },
            { "data": "date_submitted_for_sequencing" },
            { "data": "machine__sequencing_core" },
            { "data": "portion_of_lane" },
            { "data": "read_length" },
            { "data": "read_type" },

        ],
        "deferRender": true,
        "select": true,

        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a href="/metadata/seq/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 2,
            "render": function (data, type, row) {
                var itemID = row["libraryinfo__sampleinfo__id"];
                return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 6,
            "render": function (data, type, row) {
                if (row["machine__sequencing_core"] == null) {
                    return ''
                }
                else {
                    return row["machine__sequencing_core"] + '_' + row["machine__machine_name"];
                }
            }
        },
        ],
    });


    var metaseqsurl = $('#metadata_seqs_bio').attr("data-href");
    $('#metadata_seqs_bio').DataTable({
        dom: 'lBfrtip',
        buttons: [
            'excel',
            {
                text: 'TSV',
                extend: 'csvHtml5',
                fieldSeparator: '\t',
                extension: '.tsv',
                fieldBoundary: ''
            }
        ],
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "processing": true,
        "order": [[5, "desc"], [4, "desc"]],
        "ajax": {
            url: metaseqsurl,
            dataSrc: ''
        },
        "columns": [
            { "data": "seq_id" },
            { "data": "libraryinfo__library_description" },
            { "data": "libraryinfo__sampleinfo__sample_id" },
            { "data": "libraryinfo__sampleinfo__description" },
            { "data": "libraryinfo__sampleinfo__group__name" },
            { "data": "date_submitted_for_sequencing" },
            { "data": "machine__sequencing_core" },
            { "data": "portion_of_lane" },
            { "data": "read_length" },
            { "data": "read_type" },
            { "data": null, defaultContent: "" },

        ],
        "deferRender": true,
        "select": true,

        "columnDefs": [{
            "targets": 0,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a href="/metadata/seq/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 2,
            "render": function (data, type, row) {
                var itemID = row["libraryinfo__sampleinfo__id"];
                return '<a href="/metadata/sample/' + itemID + '">' + data + '</a>';
            }
        },
        {
            "targets": 6,
            "render": function (data, type, row) {
                if (row["machine__sequencing_core"] == null) {
                    return ''
                }
                else {
                    return row["machine__sequencing_core"] + '_' + row["machine__machine_name"];
                }
            }
        },
        {
            "targets": 10,
            "render": function (data, type, row) {
                var itemID = row["pk"];
                return '<a class="spacing" href="/metadata/seq/' + itemID + '/update/"><i class="fas fa-edit"></i></a><a onclick="return confirm(\'Are you sure you want to delete sequencing ' + row["seq_id"] + '?\');" href="/metadata/seq/' + itemID + '/delete/"><i class="fas fa-trash-alt"></i></a>';
            }

        }
        ],
    });

    $('.ajax_sampleinput_form').parent().addClass('ui-widget');
    $('.ajax_sampleinput_form').autocomplete({
        source: "/metadata/ajax/load-samples/",
        minLength: 2,
    });

    $('.ajax_libinput_form').parent().addClass('ui-widget');
    $('.ajax_libinput_form').autocomplete({
        source: "/metadata/ajax/load-libs/",
        minLength: 2,
    });

    $('.ajax_userinput_form').parent().addClass('ui-widget');
    $('.ajax_userinput_form').autocomplete({
        source: "/setqc/ajax/load-users/",
        minLength: 2,
    });
    $('.ajax_collabinput_form').parent().addClass('ui-widget');
    $('.ajax_collabinput_form').autocomplete({
        source: "/manager/ajax/load-collabs/",
        minLength: 2,
    });
    $('.ajax_groupinput_form').parent().addClass('ui-widget');
    $('.ajax_groupinput_form').autocomplete({
        source: "/manager/ajax/load-groups/",
        minLength: 2,
    });



    $('#id_experiment_type').change(function () {
        var url = $("#librayspec").attr("data-protocal-url");
        var expId = $(this).val();
        $.ajax({
            url: url,
            data: {
                'exptype': expId
            },
            success: function (data) {
                $("#id_protocalinfo").html(data);
            }
        })
    });


    $('#id_group').bind('autocompleteselect', function (e, ui) {
        var url = $("#groupdependent").attr("data-collabs-url");
        var groupname = ui.item.value;
        $.ajax({
            url: url,
            cache: false,
            data: {
                'group': groupname
            },
            success: function (data) {
                $("#id_research_contact").html(data);
            }
        })
    });

    $('select#id_research_contact').on('change', function () {
        console.log(this.value);
        var url = $("#groupdependent").attr("data-email-url");
        var colllab_id = this.value;
        $.ajax({
            url: url,
            cache: false,
            data: {
                'colllab_id': colllab_id
            },
            success: function (data) {
                $("#id_research_contact_email").html(data);
            }
        })
    });

    if(document.getElementById("error-message-bulk")){
        console.log(document.getElementById("error-message-bulk").innerHTML);
        $('#link-bulk').addClass('active');
        $('#link-single').removeClass('active');
        $('#single_add').removeClass('active');
        $('#single_add').removeClass('show');
        $('#bulk_add').addClass('active');
        $('#bulk_add').addClass('show');



    }

    



    // $('#id_group').change(function (){
    //     var url = $("#groupdependent").attr("data-samplescollabs-url");
    //     var url2 = $("#groupdependent").attr("data-fiscalindex-url");
    //     var groupname = $(this).val();
    //     $.ajax({
    //         url:url,
    //         cache: false,
    //         data: {
    //             'group':groupname
    //         },
    //         success:function (data){
    //             $("#id_research_contact").html(data);
    //         }
    //     })
    //     $.ajax({
    //         url:url2,
    //         cache: false,
    //         data: {
    //             'group':groupname
    //         },
    //         success:function (data){
    //             $("#id_fiscal_person_index").html(data);
    //         }
    //     })

    // });


    // $('[data-toggle="tabajax"]').click(function(e) {
    //     var $this = $(this),
    //         loadurl = $this.attr('href'),
    //         targ = $this.attr('data-target');

    //     $.get(loadurl, function(data) {
    //         $(targ).html(data);
    //     });

    //     $this.tab('show');
    //     return false;
    // });
    $('#GroupAddAjax').on('submit', function (e) {
        e.preventDefault();
        var url = $(this).attr("action");
        $.ajax({
            url: url,
            cache: false,
            type: "POST",
            data: $("#GroupAddAjax").serialize(),
            success: function (data) {
                if (data.ok) {
                    alert('New group added, please go on!')
                    $('#GroupAddModal').modal('hide');
                    return
                }
                if (data.error) {
                    $('#GroupAddModal').modal('show');
                    $('#errormessage').html(data.error);
                    return

                }

            }
        });

    });
    $('#myModal').modal('show')
    $('#confirmtosave').on('click', function () {
        $("#bindtomodalok").trigger("click");
    });
    $('#confirmtopreview').on('click', function () {
        $("#previewfromwarningmodal").trigger("click");
    });
    $(document).ready(function () {
        $('#cancel-auto').click();
    });

    $('#cancel-auto').on('click', function () {
        $("#warningmodal").trigger("click");
    });
    // $('#review-tab').on('click',function(e) {
    //   location.reload();
    //   $( "#previewsub" ).trigger( "click" );

    //   console.log(e)
    // });
    // $('#calendar-trigger').on('click',function(e) {
    //     e.preventDefault();
    //     $( "#collapsecalendar").collapse('show');
    //     $( "#calendar-trigger" ).hide();
    // });      

    // $('#collapsecalendar').on('hide.bs.collapse', function() {
    //     $("#calendar-trigger" ).show();
    // });
    $('#collapseExample').on('shown.bs.collapse', function () {
        $('#showorhideexamples').html('Hide examples<span style="margin-left: 5px"><i class="fas fa-angle-double-right"></i></span>');
    });
    $('#collapseExample').on('hidden.bs.collapse', function () {
        $('#showorhideexamples').html('Show examples<span style="margin-left: 5px"><i class="fas fa-angle-double-right"></i></span>');
    });

    $("#id_date").datepicker();
    $("#id_date_requested").datepicker();
    $("#id_date_started").datepicker();
    $("#id_date_completed").datepicker();
    $("#id_date_submitted_for_sequencing").datepicker();

    $('[data-toggle="tooltip"]').tooltip();

    $('.close').on('click', function () {
        $(this).closest('.row').fadeOut();
    });


    $('.formset_row').formset({
        addText: 'add another samples',
        deleteText: 'remove',
        prefix: 'librariesinrun_set'
    });

    $('.servicerequestitemformset_row').formset({
        addText: 'add another service',
        deleteText: 'remove',
        prefix: 'form'
    });

    $('.chipformset_row').formset({
        addText: 'add another group',
        deleteText: 'remove',
        prefix: 'form'
    });

    $('select#id_experiment_type').on('change', function () {
        if (this.value == "ChIP-seq") {
            //document.getElementById('changeble_librariesform').innerHTML='{% include "setqc_app/libraiestoincludeformchip.html"%}'
            //location.reload();
            document.getElementById('regform').style.display = "none";
            document.getElementById('chipform').style.display = '';

        }
        else {
            document.getElementById('regform').style.display = '';
            document.getElementById('chipform').style.display = "none";
        }
    });

    $('select#id_step_to_run').on('change', function () {
        if (this.value == "step1") {
            $("#id_set_name").prop("disabled", true);
            $("#encode_experiment_type").prop("disabled", true);
            $("#id_notes").prop("disabled", true);
            $("#id_genome").prop("disabled", true);
        }
        else {
            $("#id_set_name").prop("disabled", false);
            $("#encode_experiment_type").prop("disabled", false);
            $("#id_notes").prop("disabled", false);
            $("#id_genome").prop("disabled", false);
        }
    });

    //console.log(document.getElementById('changeble_librariesform'))
    var changeble_form = $('#changeble_librariesform').find("select#id_experiment_type option:selected").text()
    if (changeble_form == "ChIP-seq") {
        $('#chipform').css('display', '');
        $('#regform').css('display', 'none');


    }
    else {
        $('#regform').css('display', '');
        $('#chipform').css('display', 'none');
    }


    $('form#chiponly').find("select#id_experiment_type option:not(:contains('ChIP-seq'))").attr('disabled', 'disabled')
    $('form#notchip').find("select#id_experiment_type option:contains('ChIP-seq')").attr('disabled', 'disabled')


    $("#id_samplesinfo").attr("wrap", "off");
    $("#id_libsinfo").attr("wrap", "off");
    $("#id_seqsinfo").attr("wrap", "off");
    $(".downloadajax").on("click", function (e) {
        e.preventDefault();
        var runinfoid = this.id;

        var url1 = $(this).attr("data-href");
        $("#downloadingform").attr("runid", runinfoid);
        $("#downloadingform").attr("data-href", url1);

    });
    $("#submitForm").on("click", function (e) {
        $("#downloadingform").submit();


    });
    $("#downloadingform").on("submit", function (e) {
        var runinfoid = $(this).attr("runid");
        var runinfoiddate = 'date-' + $(this).attr("runid")
        var runinfoidflow = 'flowcell-' + $(this).attr("runid")
        var postdata = $(this).serializeArray();
        var url1 = $(this).attr("data-href");
        console.log(url1);
        $.ajax({
            url: url1,
            cache: false,
            type: "POST",
            data: postdata,
            success: function (data) {
                if (data.parseerror) {
                    alert(data.parseerror)
                    return
                }
                if (data.flowduperror) {
                    alert(data.flowduperror)
                    return
                }
                $("#" + runinfoiddate).text(data.updatedate);
                $("#" + runinfoidflow).html(data.flowid);
                $("#downloadModal").modal("hide");
                $("#" + runinfoid).replaceWith('<span class="badge badge-success badge-status-blue">JobSubmitted</span>')

            }
        });
        e.preventDefault();

    });


    $(".dmpajax").on("click", function (e) {
        e.preventDefault();


        var runinfoid = this.id;
        var runinfoiddate = 'date-' + this.id
        var that = this;
        var url1 = $(this).attr("data-href");
        var url2 = url1.replace("demultiplexing", "demultiplexing2")

        $.ajax({
            url: url1,
            cache: false,
            dataType: 'json',
            success: function (data) {
                if (!data.is_direxists) {
                    alert('Error: None of the folder name contains ' + runinfoid)
                    return
                }
                if (data.mkdirerror) {
                    alert(data.mkdirerror)
                    return
                }
                if (data.mkdirerror2) {

                    if (!confirm(data.mkdirerror2)) {
                        return
                    } else {

                        // nested ajex call DemultiplexingView2 to continue
                        $.ajax({
                            type: "POST",
                            url: url2,
                            cache: false,
                            data: { somedata: 'somedata' }
                        })
                        $("#" + runinfoiddate).text(data.updatedate)
                        $(that).replaceWith('<span class="badge badge-success badge-status-blue">JobSubmitted</span>')

                        return
                    }

                }

                if (data.writesamplesheeterror) {
                    alert(data.writesamplesheeterror)
                    return
                }
                if (data.writetosamplesheet) {
                    $("#" + runinfoiddate).text(data.updatedate)
                    // $(that).removeClass('btn btn-danger btn-sm btn-status-orange dmpajax')
                    // $(that).addClass('btn btn-success btn-sm btn-status-green disabled');
                    $(that).replaceWith('<span class="badge badge-success badge-status-blue">JobSubmitted</span>')

                    return
                }

            }

        });
    })

    var currenturl = window.location.pathname;
    if (currenturl.includes("update")) {

        $("a.editable").addClass("active");

    }
    $("nav a").each(function () {
        var href = $(this).attr("href");
        if ($(this).hasClass("dropdown-item")) {
            if (currenturl == href) {
                $(this).parent().prev("a").addClass("active");
            }
        }
        else if (currenturl.split('/')[1] == $(this).attr("id")) {
            $(this).addClass("active")

        }

    });
    $("#sidebar a").each(function () {
        var href = $(this).attr("href");
        if (currenturl == href) {
            if ($(this).parent().hasClass("collapse")) {
                $(this).parent().prev("a").addClass("active");
            }
            else {
                $(this).addClass("active")
            }
        }
    });

    $(".list-group.checkboxsidebar > .list-group-item").each(function () {
        var checkitem = $(this);
        var thisid = checkitem.attr("name")
        checkitem.css('cursor', 'pointer');
        checkbox = $('<input type="checkbox" style="display:none;" checked/>');
        checkitem.prepend(checkbox);
        var checkedicon = $('<i class="fas checkboxsidebar fa-check-square"></i>')
        var uncheckedicon = $('<i class="far checkboxsidebar fa-square"></i>')
        // checkitem.addClass("active");
        checkitem.prepend(checkedicon)
        var relatedsection = document.getElementById(thisid);
        checkbox.on('change', function () {
            if (this.checked) {
                // checkitem.addClass("active");  
                relatedsection.style.display = "block";
                checkitem.find(".far").remove()
                checkitem.prepend(checkedicon)

            }
            else {
                // checkitem.removeClass("active");             
                relatedsection.style.display = "none";
                checkitem.find(".fas").remove()
                checkitem.prepend(uncheckedicon)

            }
        })

    })

    $(".runsetqc").on("click", function (e) {
        e.preventDefault();
        that = $(this)
        var url1 = $(this).attr("data-href");
        var url2 = url1.replace("runsetqc", "runsetqc2")
        var errorname = ['notfinishederror', 'libdirnotexisterror', 'writeseterror', 'fastqerror']
        $.ajax({
            url: url1,
            cache: false,
            dataType: 'json',
            success: function (data) {
                $.each(errorname, function (index, value) {
                    if (value in data) {
                        alert(data[value])
                        return
                    }
                });
                if (data.setidexisterror) {

                    if (!confirm(data.setidexisterror)) {
                        return
                    } else {

                        $.ajax({
                            type: "POST",
                            url: url2,
                            cache: false,
                            data: { somedata: 'somedata' }
                        })
                        $(that).replaceWith('<span class="badge badge-success badge-status-blue">JobSubmitted</span>')
                        return
                    }

                }
                if (data.writesetdone) {
                    $(that).replaceWith('<span class="badge badge-success badge-status-blue">JobSubmitted</span>')

                }


            }

        })
    });

    function add_radio_buttons(refs, seq) {
        var divtoadd = $('<div value=' + seq + ' class="radio-buttons-sc"></div>')
        divtoadd.appendTo('.refgenomes');
        for (ref in refs) {
            var radiobtn = $('<div class="radio"><label><input type="radio" \
               value='+ refs[ref] + ' name = "refradio" > ' + refs[ref] + '</label ></div>');
            radiobtn.appendTo('.radio-buttons-sc');
        }

    }

    /* Click on runsinglecell located in singlecell app will GET refrence genomes available to the sequence for confirming*/
    $(document).on('click', '.runsinglecell', function (e) {
        e.preventDefault();
        button = $(this)
        var seq = $(this).val()
        console.log(seq)
        $.ajax({
            type: "GET",
            cache: false,
            url: "/singlecell/ajax/submit/",
            data: {
                'seq': seq,
                'email': "no emailneeded rn"
            },
            dataType: 'json',
            success: function (data) {
                if (data['success'] === true) {
                    if (data['submitted'] === true) {
                        //submitted the seq without need to promp user
                        $(".runsinglecell[value=" + seq + "]").replaceWith(
                            '<button type="button" class="btn btn-sm badge-success badge-status-lightblue" disabled>Submitted</button>'
                        );
                        return
                    }
                    console.log(data['success'])
                    $(".popup-overlay, .popup-content").addClass("active");
                    console.log(data['refs'])
                    add_radio_buttons(data['refs'], seq)

                    //activate popup to confirm
                }
            }

        });
    });


    /* Click on runsinglecell located in singlecell app will GET refrence genomes available to the sequence for confirming*/
    $(document).on('click', '.runsinglecell-confirm', function (e) {
        e.preventDefault();
        var seq = $('.radio-buttons-sc').attr('value');
        var ref = $('input[name="refradio"]:checked').val();
        console.log(`ref chosen: ${ref}, seq: ${seq}`)
        $.ajax({
            type: "POST",
            cache: false,
            url: "/singlecell/ajax/submit/",
            data: {
                'seq': seq,
                'ref': ref,
            },
            dataType: 'json',
            success: function (data) {
                if (data['success'] == true) {
                    console.log(data['success'])
                    $(".popup-overlay, .popup-content").removeClass("active");
                    $(".radio-buttons-sc").remove();
                    $(".runsinglecell[value=" + seq + "]").replaceWith(
                        '<button type="button" class="btn btn-sm badge-success badge-status-lightblue" disabled>Submitted</button>'
                    );
                }
                else {
                    alert(data['error'])
                }
            }

        });
    });


    $(document).on('click', '.cooladmin-submit', function (e) {
        e.preventDefault();
        button = $(this)
        seq = $(button).val();
        console.log('cool admin firing')
        //console.log("submitting seq to cooladmin: ", seq)
        $.ajax({
            type: "POST",
            url: "/singlecell/ajax/submitcooladmin/",
            data: {
                'seq': seq,
            },
            dataType: 'json',
            success: function (data) {
                console.log(data)
                if (data['is_submitted'] == true) {
                    console.log('success')
                    $(button).replaceWith(

                        '<button type="button" class="btn btn-sm badge-success badge-status-lightblue" disabled>Submitted</button>'
                    );
                }
            }
        });
    });

    $('#datatable-sc').DataTable({

        "pageLength": 25,
        "order": [[3, "desc"], [0, "desc"]],
    });

    /*
        $("#save-ca-edit").on("click", function (e) {
            e.preventDefault();
            console.log("submitting new ca submission");
            button = $(this)
            $.ajax({
                type: "POST",
                cache: false,
                url: $(this).attr('singlecell-submission-url'),
                data: {
                    'seq': $(this).val(),
                    
                    'email': $(this).attr("email"),
                },
                dataType: 'json',
                success: function (data) {
                    if (data.is_submitted) {
                        console.log('data submitted')
                        $(button).replaceWith('<button type="button" class="btn btn-info btn-sm" disabled name="buttonTenX">Submitted</button>')
                        return
                    }
                    $(button).replaceWith('<button type="button" class="btn btn-warning btn-sm" disabled name="buttonTenX">')
                }
    
            })
        })*/

    $("#other").click(function (e) {
        $("#target").click();
    });

    /**This returns a button to link to html resutls AND a button for link sharing funcitionality */
    function tenx_results_button(seq) {
        if (seq === -1) {
            var href = "#"
            var share_button = '<a class="shareButtonSc btn btn-sm" disabled><i disabled class="fas fa-link"></i></a>'
        }
        else {
            href = ("/singlecell/websummary/" + seq);
            share_button = '<a style="display:inline-block;" class="shareButtonSc btn btn-sm" data-toggle="tooltip" data-placement="top" title="Copy link to share to clipboard." value="' + seq + '" ><i class="fas fa-link"></i></a>'
        }

        return ('<a style="display:inline-block;" type="button" href=' + href + ' class="btn btn-sm btn-success badge-status-green font-weight-bold" style="color:white">Results</a> ' + share_button);
    }

    //popup btn will make popup visible
    $(document).on('click', '.shareButtonSc', function (e) {
        var seq = $(this).attr('value');
        console.log(seq);
        //var toShareButton = '<li class="list-group-item share-button-li"><button value="' + seq + '" class="btn btn-sm btn-info share-button" data-toggle="tooltip" data-placement="top" title="Share a link to the data directory"><i class="fas fa-link"></i></button></li>'
        console.log('clicked')

        //hit ajax endpoint
        $.ajax({
            type: "GET",
            cache: false,
            url: "/singlecell/ajax/generate_link",
            data: {
                'seq': seq
            },
            dataType: 'json',
            success: function (data) {
                if (data['error']) {
                    return alert(data['error'])
                }
                console.log(data['link'])
                console.log('link generated and returned!')
                var link_string = 'http://epigenomics.sdsc.edu/zhc268/' + data['link'] + '/web_summary.html';

                //copy link to clipboard
                const el = document.createElement('textarea');
                el.value = link_string;
                document.body.appendChild(el);
                el.select();
                document.execCommand('copy');
                document.body.removeChild(el);

            }
        });
        $(".popup-options-sc").append(toShareButton);
        $(".popup-overlay, .popup-content").addClass("active");
    });


    //removes the "active" class to .popup and .popup-content when the "Close" button is clicked 
    $(".closePopup").on("click", function () {
        $(".popup-overlay, .popup-content").removeClass("active");
        $(".radio-buttons-sc").remove();
    });

    //share-button will generate or get link. 
    $(document).on('click', '.share-button', function (e) {
        var seq = $(this).attr('value');
        console.log(seq);
        console.log('clicked')
        //hit ajax endpoint
        $.ajax({
            type: "GET",
            cache: false,
            url: "/singlecell/ajax/generate_link",
            data: {
                'seq': seq
            },
            dataType: 'json',
            success: function (data) {
                if (data['error']) {
                    return alert(data['error'])
                }
                console.log(data['link'])
                console.log('link generated and returned!')
                var link_string = 'http://epigenomics.sdsc.edu/zhc268/' + data['link'] + '/web_summary.html';

                //copy link to clipboard
                const el = document.createElement('textarea');
                el.value = link_string;
                document.body.appendChild(el);
                el.select();
                document.execCommand('copy');
                document.body.removeChild(el);

                var link = '<p> Link generated and copied to clipboard: <a href="http://epigenomics.sdsc.edu/zhc268/' + data['link'] + '">' + link_string + '</a></p>'
                $(".share-button-li").append(link);



            }
        });
    });

    /* Start Singlecell functions
    *
    */
    //all 10xATAC QC datatable 
    var qcUrl_10xATAC = $('#datatable-all-scATAC-qc').attr("data-href");
    $("#datatable-all-scATAC-qc").DataTable({
        "ajax": {
            url: qcUrl_10xATAC,
            dataSrc: ''
        },
        "columns": [
            { data: 'seqinfo_seq_id' },
            { data: 'seqinfo__libraryinfo__sampleinfo__sample_id' }
        ]
    })

    //all seqs datatable
    var singlecellurl = $('#datatable-all-sc').attr("data-href");
    $('#datatable-all-sc').DataTable({
        //dom: 'lBfrtip',
        "order": [[4, "desc"], [0, "asc"]],
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "processing": true,
        //"order": [[5, "desc"], [4, "desc"]],
        "ajax": {
            url: singlecellurl,
            dataSrc: ''
        },
        "columns": [
            { data: "seqinfo__seq_id" },
            { data: "seqinfo__libraryinfo__sampleinfo__sample_id" },
            { data: "seqinfo__libraryinfo__experiment_type" },
            { data: "seqinfo__libraryinfo__sampleinfo__species" },
            { data: "date_last_modified" },
            { data: "seq_status" },
            { data: "tenx_pipeline_status" },
            { data: "cooladminsubmission__pipeline_status" },
            { data: "cooladmin_edit" },
            { data: "seqinfo__libraryinfo__sampleinfo__group" },
        ],
        "deferRender": true,
        "columnDefs": [
            {
                "targets": 0,
                "render": function (data, type, row) {
                    var itemID = row["seqinfo__id"];
                    return '<a href="/metadata/seq/' + itemID + '">' + data + '</a>';
                }
            },
            // 10x pipeline check
            {
                "targets": 6,
                "render": function (data, type, row) {
                    var status = data;
                    var seq = row['seqinfo__seq_id'];
                    if (status === "Yes") {
                        return (tenx_results_button(seq));
                    } else if (status === "Error!") {
                        return ('<button type="button" class="badge badge-success badge-status-red" data-toggle="tooltip" data-placement="top" title="Contact bioinformatics group!">Error!</button>');
                    } else if ((status === "ClickToSubmit" || status === "No") && row['seq_status'].toLowerCase() === "no") {
                        return ('<button type="button" class="btn btn-sm badge-status-blue" style="color:white" data-toggle="tooltip" data-placement="top" title="No FASTQ files available">ClickToSubmit</button>');
                    } else if ((status === "ClickToSubmit" || status === "No") && row['seq_status'].toLowerCase() === "yes") {
                        return ('<button type="button" class="btn btn-danger btn-sm btn-status-orange" disabled value=' + seq + '> ClickToSubmit </button>');
                    } else {
                        return ('<button type="button" class="btn btn-sm badge-success badge-status-lightblue" disabled>' + status + '</button>');
                    }
                }
            },
            {
                //cooladmin status
                "targets": 7,
                "render": function (data, type, row) {
                    var status = data;
                    var seq_id = row['seqinfo__seq_id'];
                    if (status === "ClickToSubmit" || status == null) {
                        //check fastq seq status
                        if (row["seq_status"] === "Yes") {
                            if (row['libraryinfo__experiment_type'] == "10xATAC" && (row['10x_status'].toLowerCase() === "yes" || row['10x_status'].toLowerCase() === "results")) {
                                return ('<button type="button" class="btn btn-danger btn-sm btn-status-orange" disabled value="' + seq_id + '"> ClickToSubmit </button>');
                            } else if (row['seqinfo__libraryinfo__experiment_type'] === "10xATAC" && row['tenx_pipeline_status'].toLowerCase() !== "results") {
                                return ('<button type="button" data-toggle="tooltip" data-placement="top" title="Run10xPipeline First" class="badge badge-success badge-status-blue cooladmin-submit" disabled> Run10xPipeline</button>');
                            } else {
                                return ('<button type="submit" class="btn btn-danger btn-sm btn-status-orange disabled value="' + seq_id + '"> ClickToSubmit</button>');
                            }
                        }
                        else { //no fastq file present
                            return ('<button type="button" data-toggle="tooltip" data-placement="top" title="FASTQ not present" disabled class="badge badge-success badge-status-blue cooladmin-submit" disabled> ClickToSubmit </button>');
                        }
                    } else if (status === ".status.fail") {//failed
                        return ('<button type="button" class="btn btn-success btn-sm badge-status-yellow cooladmin-status">Error!</button>')
                    } else if (status === ".status.process") {
                        return ('<button class="btn btn-sm badge-success badge-status-lightblue" disabled cooladmin-status"> Processing</button>')
                    } else {
                        return '<button type="button" class="btn btn-sm btn-success badge-status-green" style="color:white"><a href="' + '#' + '" style="color:white" target="_blank"> Results</a></button >'

                    }
                },
            },
            {
                "targets": 8,
                "render": function (data, type, row) {
                    var seq_id = row['seq_id']
                    if (row['seqinfo__libraryinfo__experiment_type'] !== "10xATAC" || row['10x_status'] === "Yes") {
                        return ('<a href="/singlecell/EditCoolAdmin/' + seq_id + '"><i class="fas fa-edit"></i></a>');
                    } else {
                        return ('<a href="#"><i class="fas fa-edit"></i></a>')
                    }
                }
            }
        ]
    });

    //user sequences
    var singlecellurl_user = $('#datatable-user-sc').attr("data-href");
    var sc_table = $('#datatable-user-sc').DataTable({
        "order": [[4, "desc"], [0, "asc"]],
        dom: 'lBfrtip',
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "processing": true,
        //"order": [[5, "desc"], [4, "desc"]],
        "ajax": {
            url: singlecellurl_user,
            dataSrc: ''
        },
        select: {
            style: 'multi'
        },

        "columns": [
            { data: "seqinfo__seq_id" },
            { data: "seqinfo__libraryinfo__sampleinfo__sample_id" },
            { data: "seqinfo__libraryinfo__experiment_type" },
            { data: "seqinfo__libraryinfo__sampleinfo__species" },
            { data: "date_last_modified" },
            { data: "seq_status" },
            { data: "tenx_pipeline_status" },
            { data: "cooladminsubmission__pipeline_status" },
            { data: "cooladmin_edit" },
            { data: "seqinfo__libraryinfo__sampleinfo__group" },
        ],
        buttons: [{
            text: 'Export',
            action: function (e, dt, type, indexes) {
                if (type === 'row') {
                    var data = sc_table.rows(indexes).data();
                    var itemID = data["seqinfo__seq_id"]

                    // do something with the ID of the selected items
                    console.log(itemID)
                }
            }
        }
        ],
        "deferRender": true,
        "columnDefs": [
            {
                "targets": 0,
                "render": function (data, type, row) {
                    var itemID = row["seqinfo__id"];
                    return '<a href="/metadata/seq/' + itemID + '">' + data + '</a>';
                }
            },
            // 10x pipeline check
            {
                "targets": 6,
                "render": function (data, type, row) {
                    var status = data;
                    var seq = row['seqinfo__seq_id'];
                    if (status === "Yes") {
                        return (tenx_results_button(seq));
                    } else if (status === "Error!") {
                        return ('<button type="button" class="badge badge-success badge-status-red" data-toggle="tooltip" data-placement="top" title="Contact bioinformatics group!">Error!</button>');
                    } else if ((status === "ClickToSubmit" || status === "No") && row['seq_status'] === "No") {
                        return ('<button type="button" class="btn btn-sm badge-status-blue" style="color:white" data-toggle="tooltip" data-placement="top" title="No FASTQ files available">ClickToSubmit</button>');
                    } else if ((status === "ClickToSubmit" || status === "No") && row['seq_status'] === "Yes") {
                        return ('<button type="button" class="runsinglecell btn btn-danger btn-sm btn-status-orange" value=' + seq + '> ClickToSubmit </button>');
                    } else {
                        return ('<button type="button" class="btn btn-sm badge-success badge-status-lightblue" disabled>' + status + '</button>');
                    }
                }
            },
            {
                //cooladmin status
                "targets": 7,
                "render": function (data, type, row) {
                    var status = data;
                    var seq_id = row['seqinfo__seq_id'];
                    if (status === "ClickToSubmit" || status == null) {
                        //check fastq seq status
                        if (row["seq_status"] === "Yes") {
                            if (row['seqinfo__libraryinfo__experiment_type'] == "10xATAC" && row['tenx_pipeline_status'] === "Yes") {
                                return ('<button type="button" class="btn btn-danger btn-sm btn-status-orange  cooladmin-submit" value="' + seq_id + '"> ClickToSubmit </button>');
                            } else if (row['seqinfo__libraryinfo__experiment_type'] === "10xATAC" && row['tenx_pipeline_status'] !== "Results") {
                                return ('<button type="button" data-toggle="tooltip" data-placement="top" title="Run10xPipeline First" class="badge badge-success badge-status-blue cooladmin-submit" disabled> Run10xPipeline</button>');
                            } else {
                                return ('<button type="submit" class="btn btn-danger btn-sm btn-status-orange cooladmin-submit" value="' + seq_id + '"> ClickToSubmit</button>');
                            }
                        }
                        else { //no fastq file present
                            return ('<button type="button" data-toggle="tooltip" data-placement="top" title="FASTQ not present" disabled class="badge badge-success badge-status-blue cooladmin-submit" disabled> ClickToSubmit </button>');
                        }
                    } else if (status === ".status.fail") {//failed
                        return ('<button type="button" class="btn btn-success btn-sm badge-status-yellow cooladmin-status">Error!</button>')
                    } else if (status === ".status.processing") {
                        return ('<button class="btn btn-sm badge-success badge-status-lightblue" disabled cooladmin-status"> Processing</button>')
                    } else {
                        return '<a href="' + status + '" style="color:white" target="_blank" type="button" class="btn btn-sm btn-success badge-status-green font-weight-bold" style="color:white">Results</a>'

                    }
                },
            },
            {//cooladmin edit button- links to edit page
                "targets": 8,
                "render": function (data, type, row) {
                    var seq_id = row['seqinfo__seq_id']
                    if (row['seqinfo__libraryinfo__experiment_type'] !== "10xATAC" || row['10x_status'] === "Yes") {
                        return ('<a href="/singlecell/EditCoolAdmin/' + seq_id + '"><i class="fas fa-edit"></i></a>');
                    } else {
                        return ('<a href="#"><i class="fas fa-edit"></i></a>')
                    }
                }
            }
            /*{// misc are for buttons
                "targets": 8,
                "render": function (data, type, row) {
                    var share_pill = '<a href="#" class="badge badge-pill badge-info">Share</a>'
                }
            }*/
        ]
    });

    //user sequences
    var singlecellurl_user = $('#datatable-collab-sc').attr("data-href");
    $('#datatable-collab-sc').DataTable({
        "order": [[4, "desc"], [0, "asc"]],
        //dom: 'lBfrtip',
        "aLengthMenu": [[20, 50, 75, -1], [20, 50, 75, "All"]],
        "iDisplayLength": 20,
        "processing": true,
        //"order": [[5, "desc"], [4, "desc"]],
        "ajax": {
            url: singlecellurl_user,
            dataSrc: ''
        },
        "columns": [
            { data: "seqinfo__seq_id" },
            { data: "seqinfo__libraryinfo__sampleinfo__sample_id" },
            { data: "seqinfo__libraryinfo__experiment_type" },
            { data: "seqinfo__libraryinfo__sampleinfo__species" },
            { data: "date_last_modified" },
            { data: "seq_status" },
            { data: "tenx_pipeline_status" },
            { data: "cooladminsubmission__pipeline_status" },
            { data: "cooladmin_edit" },
            { data: "seqinfo__libraryinfo__sampleinfo__group" },
        ],
        "deferRender": true,
        "columnDefs": [
            // {
            //     "targets": 0,
            //     "render": function (data, type, row) {
            //         var itemID = row["id"];
            //         return '<a href="/metadata/seq/' + itemID + '">' + data + '</a>';
            //     }
            // },
            // 10x pipeline check
            {
                "targets": 6,
                "render": function (data, type, row) {
                    var status = data;
                    var seq = row['seqinfo__seq_id'];
                    if (status === "Yes") {
                        return (tenx_results_button(seq));
                    } else if (status === "Error!") {
                        return ('<button type="button" class="badge badge-success badge-status-red" data-toggle="tooltip" data-placement="top" title="Contact bioinformatics group!">Error!</button>');
                    } else if (status === "No" && row['seq_status'] === "No") {
                        return ('<button type="button" class="btn btn-sm badge-status-blue" style="color:white" data-toggle="tooltip" data-placement="top" title="No FASTQ files available">ClickToSubmit</button>');
                    } else if (status === "No" && row['seq_status'] === "Yes") {
                        return ('<button type="button" disabled class="runsinglecell btn btn-danger btn-sm btn-status-orange" value=' + seq + '> Submit </button>');
                    } else {
                        return ('<button type="button" class="btn btn-sm badge-success badge-status-lightblue" disabled>' + status + '</button>');
                    }
                }
            },
            {
                //cooladmin status
                "targets": 7,
                "render": function (data, type, row) {
                    var status = data;
                    var seq_id = row['seqinfo__seq_id'];
                    if (status === "ClickToSubmit" || status == null) {
                        //check fastq seq status
                        if (row["seq_status"] === "Yes") {
                            if (row['seqinfo__libraryinfo__experiment_type'] == "10xATAC" && row['tenx_pipeline_status'] === "Yes") {
                                return ('<button type="button" class="btn btn-danger btn-sm btn-status-orange  cooladmin-submit" disabled value="' + seq_id + '"> Submit </button>');
                            } else if (row['seqinfo__libraryinfo__experiment_type'] === "10xATAC" && row['tenx_pipeline_status'] !== "Results") {
                                return ('<button type="button" data-toggle="tooltip" data-placement="top" title="Run10xPipeline First" class="badge badge-success badge-status-blue cooladmin-submit" disabled> Run10xPipeline</button>');
                            } else {
                                return ('<button type="submit" disabled class="btn btn-danger btn-sm btn-status-orange cooladmin-submit" value="#"> Submit</button>');
                            }
                        }
                        else { //no fastq file present
                            return ('<button type="button" data-toggle="tooltip" data-placement="top" title="FASTQ not present" disabled class="badge badge-success badge-status-blue cooladmin-submit" disabled> ClickToSubmit </button>');
                        }
                    } else if (status === ".status.fail") {//failed
                        return ('<button type="button" class="btn btn-success btn-sm badge-status-yellow cooladmin-status">Error!</button>')
                    } else if (status === ".status.processing") {
                        return ('<button class="btn btn-sm badge-success badge-status-lightblue" disabled cooladmin-status"> Processing</button>')
                    } else {
                        return '<a href="' + status + '" style="color:white" target="_blank" type="button" class="btn btn-sm btn-success badge-status-green font-weight-bold" style="color:white">Results</a>'

                    }
                },
            },

            /*{// misc are for buttons
                "targets": 8,
                "render": function (data, type, row) {
                    var share_pill = '<a href="#" class="badge badge-pill badge-info">Share</a>'
                }
            }*/
        ]
    });

    //Add on selection functions 
    sc_table.on('select', function (e, dt, type, indexes) {
        if (type === 'row') {
            var data = sc_table.rows(indexes).data().pluck('id');
            var itemID = data["seqinfo__seq_id"]

            // do something with the ID of the selected items
            console.log(data)

        }
    });

    //Cool admin form edit page details 
    $('#id_date_submitted').attr("readonly", true);
    $('#id_date_modified').attr("readonly", true);

    $("#id_pipeline_version").attr('title', 'Choose desired pipeline version');
    $("#id_useHarmony").attr('title', 'Default False. Perform harmony batch correction using the dataset IDs as batch IDs only for multiple sequences');
    $("#id_snapUsePeak").attr('title', 'Construct a peak matrix in addition to the bin matrix');
    $("#id_snapSubset").attr('title', ' Use this number to construct a subset that is used to construct the distance matrix for SNAP. The lower it is, the lesser is the resolution. After 10-15K cells, the memory might become an issue');
    $("#id_doChromVar").attr('title', ' Perform chromVAR analysis');
    $("#id_readInPeak").attr('title', 'Should be inbetween 0 and 1. QC metric used to filter cells with low ratio of reads in peak');
    $("#id_tssPerCell").attr('title', 'QC metric used to filter cells with low TSS');
    $("#id_minReadPerCell").attr('title', 'QC metric used to filter cells with low number of aligned fragments');
    $("#id_snapBinSize").attr('title', 'Should be a list of whole numbers separated by a single space. Determines the bin sizes used to perform SNAP clustering.');
    $("#id_snapNDims").attr('title', 'Default is 25 if blank. Should be a list of whole numbers separated by a single space. Determines the number of dimensions to use to perform SNAP clustering.');
    $("#id_genome").attr('title', 'Note: If experiment is of type 10xATAC, the ref genome will then the same as the one ran with the 10x pipeline');
    /* makse sure value is not negative
    $("").change(function (e) {
        if ()
    });
    */
});
