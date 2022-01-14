$(document).ready(function () {

    $('.sidebar-menu').tree();

    loadCurrentQueue();

    $('button').on('click', function (e){
       //console.log('click');
       //alert($(this).attr('code'));
       if($(this).attr('code') === 'pickup'){
            pickup_id = $('.pickup-id').text().trim();
            trans_id = $('#trans_id').val();
            if (trans_id == ""){
                pickupQueue(pickup_id);
            }else{
                alert('Cannot pickup new queue, Please finish current queue');
            }
       }
       if($(this).attr('code') === 'recall'){
            trans_id = $('#trans_id').val();
            recallQueue(trans_id)
       }
       if($(this).attr('code') === 'skip'){
            trans_id = $('#trans_id').val();
            skipQueue(trans_id)
        }

       if($(this).attr('code') === 'finish'){
            trans_id = $('#trans_id').val();
            finishQueue(trans_id)
       }
    });

    function loadCurrentQueue(){
        pickup_id = $('.pickup-id').text().trim();
        $.getJSON('/queue/pickup/current/' + pickup_id + '/', function (data) {
        })
        .done(function(resp){
            console.log(resp);
            console.log(resp.counter_name)
            $('#trans_id').val(resp.id);
            $('#counter_name').text(resp.counter_name);
            $('#counter_trans').text(resp.counter_trans);
            $('.widget-user-header').removeClass().addClass('widget-user-header ' + resp.counter_bg);
            $('.badge').removeClass().addClass('badge ' + resp.counter_bg);

        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    }

    function pickupQueue(id){
        console.log("pickup");
        console.log(id);
        $.getJSON('/queue/pickup/' + id + '/', function (data) {
        })
        .done(function(resp){
            console.log(resp);
            console.log(resp.counter_name)
            $('#trans_id').val(resp.id);
            $('#counter_name').text(resp.counter_name);
            $('#counter_trans').text(resp.counter_trans);
            $('.widget-user-header').removeClass().addClass('widget-user-header ' + resp.counter_bg);
            $('.badge').removeClass().addClass('badge ' + resp.counter_bg);

        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    }

    function recallQueue(id){
        console.log("Finish");
        console.log(id);
        $.getJSON('/queue/recall/' + id + '/', function (data) {

        })
        .done(function(resp){
            console.log(resp);
        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    }

    function skipQueue(id){
        console.log("Finish");
        console.log(id);
        $.getJSON('/queue/skip/' + id + '/', function (data) {
        })
        .done(function(resp){
            $('#trans_id').val('');
            $('#counter_name').text('Not Available');
            $('#counter_trans').text('---');
            $('.widget-user-header').removeClass().addClass('widget-user-header');
            $('.badge').removeClass().addClass('badge');
        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    }

    function finishQueue(id){
        console.log("Finish");
        console.log(id);
        $.getJSON('/queue/finish/' + id + '/', function (data) {
        })
        .done(function(resp){
            $('#trans_id').val('');
            $('#counter_name').text('Not Available');
            $('#counter_trans').text('---');
            $('.widget-user-header').removeClass().addClass('widget-user-header');
            $('.badge').removeClass().addClass('badge');
        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    }

});