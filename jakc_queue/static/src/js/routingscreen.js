$(document).ready( function(){
    //Loading Counter
    setInterval(loadCounter, 1000);
    //Loading Queuing

    function loadCounter(){
        $.ajax({
            url         : "/jakc_queue/counter/load",
            type        : "POST",
            data        : {
            },
            dataType    : "json",
            success     : function(resp) {
                console.log(resp);
            },
            error        : function(xhr, status, error){
                console.log(xhr);
            }
        });
    }
})