if($("#form-widgets-title").val() == ""){
  $.ajax({
    type: 'POST',
    url: 'getInfoCreateApplication',
    success: function(data){
      result = $.parseJSON(data);
      if(result != null){
        $("#form-widgets-offer_id").val(result['offer_id']);
        $("#form-widgets-offer_title").val(result['offer_title']);
        $("#form-widgets-title").val(result['fullname']);
        $("#form-widgets-dni").val(result['dni']);
        $('#form-widgets-email').val(result['email']);
        $('#form-widgets-prisma_id').val(result['idPrisma']);
        $('#form-widgets-codi_expedient').val(result['codi_expedient'])
        if(result['phone']){
          $('#form-widgets-telephone').val(result['phone']);
        }
      }
    }
  });
}
