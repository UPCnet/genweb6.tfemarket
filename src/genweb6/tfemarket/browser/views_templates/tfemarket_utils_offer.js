$(document).ready(function() {
  $('#offer').select2({
    placeholder: "",
    allowClear: true,
    theme: 'bootstrap-5'
  });

  $('#offer').on('change', function(){
    $("#confirm").prop("checked", false);
  });
});
