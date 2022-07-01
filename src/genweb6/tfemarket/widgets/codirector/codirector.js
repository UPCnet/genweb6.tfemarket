var hideElementsCodirector = function(){
  $("#form-widgets-codirector-error").removeClass("viewError");
  $("#form-widgets-codirector-warn").removeClass("viewWarn");
  $("#form-widgets-codirector-hint > tbody").html("<tr><td/><td/><td/><td/><td/></tr>");
}

var addCodirector = function(codirector){
  parent = $(codirector).parent().parent();
  $("#form-widgets-codirector").val($(parent).children('.fullname').html());
  $("#form-widgets-codirector_id").val($(parent).children('.codirector').html());
  $("#form-widgets-codirector_email").val($(parent).children('.email').html());
  $("#form-widgets-codirector_dept").val($(parent).children('.dept').html());
  $('#form-widgets-codirector-modal').modal('toggle');
}

var changeDisplaysCodirector = function(value){
  switch(value){
    case 'UPC':
      $("#form-widgets-codirector").attr('readonly', 'readonly');
      $("#formfield-form-widgets-codirector").css('display', 'block');
      $("#formfield-form-widgets-codirector_id").css('display', 'block');
      $("#formfield-form-widgets-codirector_email").css('display', 'block');
      $("#formfield-form-widgets-codirector_dept").css('display', 'block');
      $("#form-widgets-codirector-btn-modal").css('display', 'inline-block');
      break;
    case 'External':
      $("#form-widgets-codirector").removeAttr('readonly');
      $("#formfield-form-widgets-codirector").css('display', 'block');
      $("#formfield-form-widgets-codirector_id").css('display', 'none');
      $("#formfield-form-widgets-codirector_email").css('display', 'none');
      $("#formfield-form-widgets-codirector_dept").css('display', 'none');
      $("#form-widgets-codirector-btn-modal").css('display', 'none');
      break;
    default:
      $("#formfield-form-widgets-codirector").css('display', 'none');
      $("#formfield-form-widgets-codirector_id").css('display', 'none');
      $("#formfield-form-widgets-codirector_email").css('display', 'none');
      $("#formfield-form-widgets-codirector_dept").css('display', 'none');
      $("#form-widgets-codirector-btn-modal").css('display', 'none');
      break;
  }
}

$("#form-widgets-type_codirector").on("change", function(){
  changeDisplaysCodirector(this.value);
  $("#form-widgets-codirector").val('');
  $("#form-widgets-codirector_id").val('');
  $("#form-widgets-codirector_email").val('');
  $("#form-widgets-codirector_dept").val('');
});

$("#form-widgets-codirector-btn").on("click", function(){
  hideElementsCodirector();
  var regexCodirector = new RegExp('^[a-zA-ZñÑçÇ]{1,}\\.[a-zA-Z0-9-.ñÑçÇ]{1,}$');
  var codirectorUser = $("#form-widgets-codirector-input").val();
  if(regexCodirector.test(codirectorUser)){
    $.ajax({
      type: 'POST',
      data: { "teacher" : $("#form-widgets-codirector-input").val() },
      url: 'getTeacher',
      success: function(data){
        results = $.parseJSON(data);
        if(results != null && results.length > 0){
          $("#form-widgets-codirector-hint > tbody").html("");
          $.each( results, function( key, value ){
            $("#form-widgets-codirector-hint").show();
            field = "<tr>";
            field += "<td class='codirector'>" + value['user'] + "</td>";
            field += "<td class='fullname'>" + value['fullname'] + "</td>";
            field += "<td class='email'>" + value['email'] + "</td>";
            field += "<td class='dept'>" + value['dept'] + "</td>";
            field += "<td scope='row' class='actions'>";
            field += "<a class='label add' alt='add' onclick='addCodirector(this)'>";
            field += "<i class='bi bi-plus'></i>";
            field += "</a>";
            field += "</td>";
            field += "</tr>";
            $("#form-widgets-codirector-hint").append(field);
          });
        }else{
          $("#form-widgets-codirector-warn").addClass("viewWarn");
        }
      }
    });
  }else{
    $("#form-widgets-codirector-error").addClass("viewError");
  }
});

$(document).ready(function(){
  changeDisplaysCodirector($("#form-widgets-type_codirector").val());
});
