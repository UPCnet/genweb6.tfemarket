$.urlParam = function(name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    return results ? results[1] : false;
}

function setCookie(key, value, expiry) {
    var expires = new Date();
    expires.setTime(expires.getTime() + (expiry * 24 * 60 * 60 * 1000));
    document.cookie = key + '=' + value + ';path=/' + ';expires=' + expires.toUTCString();
}

function updateURLParameter(url, param, paramVal){
    var newAdditionalURL = "";
    var tempArray = url.split("?");
    var baseURL = tempArray[0];
    var additionalURL = tempArray[1];
    var temp = "";
    if (additionalURL) {
        tempArray = additionalURL.split("&");
        for (var i=0; i<tempArray.length; i++){
            if(tempArray[i].split('=')[0] != param){
                newAdditionalURL += temp + tempArray[i];
                temp = "&";
            }
        }
    }

    var rows_txt = temp + "" + param + "=" + paramVal;
    return baseURL + "?" + newAdditionalURL + rows_txt;
}

function changeLangAndReload(lang){
    setCookie('MERCAT_TFE_LANG', lang);
    var versionUpdate = (new Date()).getTime();
    if (window.location.href.indexOf("?") > -1) {
        if (window.location.href.indexOf("searchOffer") == -1 && (window.location.href.indexOf("&search") > -1 || window.location.href.indexOf("?search")) > -1) {
            $('#formSearchOffers').submit();
        }else{
            if (window.location.href.indexOf("&ts") > -1 || window.location.href.indexOf("?ts") > -1) {
                window.location = updateURLParameter(window.location.href, 'ts', versionUpdate);
            }else{
                window.location = window.location.href + '&ts=' + versionUpdate;
            }
        }
    }else{
        window.location = window.location.href + '?ts=' + versionUpdate;
    }
}

function uncollapseAll(){
    $("#collapseAll.collapsed").click(function() {
        $("#accordionOfertes .accordion-button.collapsed").trigger('click').removeClass('collapsed').attr('aria-expanded', 'true');
        $(this).removeClass('collapsed').attr('aria-expanded', 'true');
        collapseAll();
    });
}

function collapseAll(){
    $("#collapseAll:not(.collapsed)").click(function() {
        $("#accordionOfertes .accordion-button:not(.collapsed)").trigger('click').addClass('collapsed').attr('aria-expanded', 'false');
        $(this).addClass('collapsed').attr('aria-expanded', 'false');
        uncollapseAll();
    });
}

$(function() {
    $('.buscador-mercat .btn').on('click', function() {
        $('.spinner-mercat').fadeIn(500);
    });

    $('.setLangCA').click(function() {
        changeLangAndReload('ca');
    });

    $('.setLangEN').click(function() {
        changeLangAndReload('en');
    });

    $('.setLangES').click(function() {
        changeLangAndReload('es');
    });

    $('input[name="language"]').click(function() {
        if ($('input[name="language"]:checked').length == 0) {
            $(this).prop('checked', true);
        }
    });

    if ($('#formSearchOffers').attr('data-saved') == 1) {
        $('input[name="language"]').prop('checked', true);
    }

    var offer = $.urlParam('offer');
    if (offer) {
        if($("#heading-" + offer).length > 0){
            $(".alert[role='alert']:not(.alert-mercat)").appendTo("#" + offer + "-info");
            $('html, body').animate({
                scrollTop: $("#heading-" + offer).offset().top - 100
            }, 1000);
            if ($.urlParam('open')) {
                setTimeout(function() {
                    $("#heading-" + offer + " .accordion-button").trigger('click');
                }, 500);
            }
        }
    }

    uncollapseAll();
});
