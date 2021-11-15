$(document).ready(function (e){
    console.log("Start Print");
    setTimeout(function () { window.print(); }, 500);
    console.log("On Focus");
    window.onfocus = function () { setTimeout(function () { window.close(); }, 500); }
});