function show_fields_modality_offer(){
  $("#formfield-form-widgets-company").show();
}

function hide_fields_modality_offer(){
  $("#formfield-form-widgets-company").hide();
}

function update_modality_offer(selected_option) {
  switch(selected_option) {
    case 'Empresa':
      show_fields_modality_offer();
      break;
    case 'Universitat':
    default:
      hide_fields_modality_offer();
  }
}

$(document).ready(function(){
  $("#form-widgets-modality").change(function(){
    update_modality_offer($(this).val());
  });

  update_modality_offer($("#form-widgets-modality").val());
});
