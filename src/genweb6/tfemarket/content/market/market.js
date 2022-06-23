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

$(function() {
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

    $('input[name="modality"]').click(function() {
        if ($('input[name="modality"]:checked').length == 0) {
            $(this).prop('checked', true);
        }
    });

    $('.expand').click(function() {
        $(this).hide();
        $(this).parent().find('.notexpand').show();
        $(this).parent().parent().parent().find('.offerData').slideDown();
    });

    $('.notexpand').click(function() {
        $(this).hide();
        $(this).parent().find('.expand').show();
        $(this).parent().parent().parent().find('.offerData').slideUp();
    });

    $("#buttonsSearch").click(function() {
        if ($("#collapseSearch").is(":visible")) {
            $("#formSearchOffers").slideUp();
            $("#expandSearch").show();
            $("#collapseSearch").hide();
        } else {
            $("#formSearchOffers").slideDown();
            $("#expandSearch").hide();
            $("#collapseSearch").show();
        }
    });

    $("#expandAll").click(function() {
        $(".expand").parent().parent().parent().slideDown();
        $(".expand").hide();
        $(".notexpand").show();
        $(".expand").parent().parent().parent().find('.offerData').slideDown();
        $("#expandAll").hide();
        $("#collapseAll").show();
    });

    $("#collapseAll").click(function() {
        $(".notexpand").slideUp();
        $(".notexpand").hide();
        $(".expand").show();
        $(".expand").parent().parent().parent().find('.offerData').slideUp();
        $("#expandAll").show();
        $("#collapseAll").hide();
    });

    if ($('#formSearchOffers').attr('data-saved') == 1) {
        $('input[name="language"]').prop('checked', true);
        $('input[name="modality"]').prop('checked', true);
    }

    var offer = $.urlParam('offer');
    if (offer) {
        if($("#" + offer).length > 0){
            $(".alert[role='alert']:not(.offerInfo)").appendTo("#" + offer + "-info");
            $('html, body').animate({
                scrollTop: $("#" + offer).offset().top - 50
            }, 1000);
            $("#" + offer).trigger('click');
            if ($.urlParam('open')) {
                setTimeout(function() {
                    $("#" + offer + "-applications").trigger('click');
                }, 500);
            }
        }
    }

    $('.showMoreInfo').click(function() {
        offerInfo = $(this).parent().parent().parent().find('.moreInfo');
        if (offerInfo.hasClass('hide')) {
            $(this).find('i.fa').removeClass('fa-chevron-down').addClass('fa-chevron-up');
            offerInfo.slideDown().removeClass('hide');
        } else {
            $(this).find('i.fa').removeClass('fa-chevron-up').addClass('fa-chevron-down');
            offerInfo.slideUp().addClass('hide');
        }
    });

    $('.showApplications').click(function() {
        applications = $(this).parent().parent().parent().find('.applications');
        if (applications.hasClass('hide')) {
            $(this).find('.showApplicationsLit').hide();
            $(this).find('.hideApplicationsLit').show();
            applications.slideDown().removeClass('hide');
        } else {
            $(applications).find('i.fa').removeClass('fa-chevron-up').addClass('fa-chevron-down')
            $(this).find('.hideApplicationsLit').hide();
            $(this).find('.showApplicationsLit').show();
            applications.slideUp().addClass('hide');
        }
    });

    $('#formSearchOffers .keyword').click(function() {
        input = $(this).find('input[name="key"]');
        if ($(input).prop('checked')) {
            $(this).removeClass('checked');
            $(input).prop('checked', false);
        } else {
            $(this).addClass('checked');
            $(input).prop('checked', true);
        }
    });
});

$(function() {
    $('#market #offersFilter').on('click', function() {
        $('#formSearchOffers').submit();
        $('#market .loaderContainer').fadeIn(500);
    });

    $('#market a[href="?allOffers"]').on('click', function() {
        $('#market .loaderContainer').fadeIn(500);
    });

    $('#market .dropdown-menu a').on('click', function() {
        $('#market .loaderContainer').fadeIn(500);
    });
});
