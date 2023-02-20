$(document).ready(function () {
  tfe = $('.returnTFE')
  $('.redirect').on('click', function(){
    filters = $(this).attr('data-filters');

    if(tfe.length == 1){
      urlTFE = tfe.attr('data-href') + filters;
      window.open(urlTFE);
    }else{
      urlTFE = []
      $.each(tfe, function(){
        urlTFE.push($(this).attr('data-href') + filters);
      });
      $('#dialogTFE').dialog({modal: true});

      $('.returnTFE').on('click', function(){
        urlTFE = $(this).attr('data-href') + filters;
        $("#dialogTFE").dialog('close');
        window.open(urlTFE);
      });
    }
  });
});
