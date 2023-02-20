var normalize = (function() {

  var from = "ÃÀÁÄÂÈÉËÊÌÍÏÎÒÓÖÔÙÚÜÛãàáäâèéëêìíïîòóöôùúüûÑñÇç",
      to   = "AAAAAEEEEIIIIOOOOUUUUaaaaaeeeeiiiioooouuuunncc",
      mapping = {};

  for(var i = 0, j = from.length; i < j; i++ )
      mapping[ from.charAt( i ) ] = to.charAt( i );

  return function( str ) {
      var ret = [];
      for( var i = 0, j = str.length; i < j; i++ ) {
          var c = str.charAt( i );
          if( mapping.hasOwnProperty( str.charAt( i ) ) )
              ret.push( mapping[ c ] );
          else
              ret.push( c );
      }
      return ret.join( '' );
  }

})();

$.urlParam = function(name) {
  var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
  return results ? results[1] : false;
}

$('#offer').on('change', function(){
  $.ajax({
    type: 'POST',
    data: {'UID': $('#offer').val()},
    url: 'getInfoRenameOffer',
    success: function(data){
      result = $.parseJSON(data);
      if(result != null){
        $("#newTitle").val(result['title']);
        $("#newShortname").val(result['shortname']);
      }
    }
  });

  $("#confirm").prop("checked", false);
});

$(document).ready(function() {
  $('#offer').select2({
    placeholder: "",
    allowClear: true,
    theme: 'bootstrap-5'
  });

  var offer = $.urlParam('offer');
  if (offer) {
    $('#offer').select2("val", offer);
    $('#offer option[value=' + offer + ']').prop('selected', true);
    $('#offer').change();
  }

  $('#newTitle').keyup(function(){
    $("#newShortname").val(normalize($(this).val()).replace(/  +/g, ' ').replace(/[\ .\/]/g, "-").replace(/[^a-zA-Z0-9-_]/g, '').toLowerCase());
  });
});
