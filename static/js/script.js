/*----Materialize JS initialization---*/
$(document).ready(function(){
    $('.sidenav').sidenav({edge:"right"});
    $(".dropdown-trigger").dropdown();
    $('.parallax').parallax();
    $('.tooltipped').tooltip();
    $('select').formSelect();
    $('.modal').modal();
    $('.datepicker').datepicker({
        format: "dd/mm/yyyy",
        yearRange: 3,
        showClearBtn: true,
        i18n: {
            done: "Select"
        }
    });

    $('.timepicker').timepicker({
        showClearBtn: true,
        twelveHour: false,
        i18n: {
            done: "Select",
            clear: "Clear",
            cancel: "Cancel"
        }
    });  

    /*----price free icon on/off---*/
    $( "#price_free" ).click(function(){
        $("#price_amount").toggle();
      });
      
    /*----fixes bug with Materialize select elements not working with iOS, https://stackoverflow.com/a/52851046---*/
    $(document).click(function () {
        "use strict";
        $('li[id^="select-options"]').on('touchend', function (e) {
            e.stopPropagation();
        });
    });


    /*----validate select/div in forms - adapted from source Code Institute "Materialize Form Validation" lesson---*/
    validateMaterializeSelect();
    function validateMaterializeSelect() {
        let classValid = { "border-bottom": "1px solid #880e4f", "box-shadow": "0 1px 0 0 #880e4f" };
        let classInvalid = { "border-bottom": "1px solid #f44336", "box-shadow": "0 1px 0 0 #f44336" };
        if ($("select.validate").prop("required")) {
            $("select.validate").css({ "display": "block", "height": "0", "padding": "0", "width": "0", "position": "absolute" });
        }
        $(".select-wrapper input.select-dropdown").on("focusin", function () {
            $(this).parent(".select-wrapper").on("change", function () {
                if ($(this).children("ul").children("li.selected:not(.disabled)").on("click", function () { })) {
                    $(this).children("input").css(classValid);
                }
            });
        }).on("click", function () {
            if ($(this).parent(".select-wrapper").children("ul").children("li.selected:not(.disabled)").css("background-color") === "rgba(0, 0, 0, 0.03)") {
                $(this).parent(".select-wrapper").children("input").css(classValid);
            } else {
                $(".select-wrapper input.select-dropdown").on("focusout", function () {
                    if ($(this).parent(".select-wrapper").children("select").prop("required")) {
                        if ($(this).css("border-bottom") != "1px solid rgb(136, 14, 79)") {
                            $(this).parent(".select-wrapper").children("input").css(classInvalid);
                        }
                    }
                });
            }
        });
    }
  
  });