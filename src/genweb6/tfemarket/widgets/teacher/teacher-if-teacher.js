if($("#form-widgets-teacher_manager").val() == ""){
  $.ajax({
    type: 'POST',
    url: 'getExactTeacher',
    success: function(data){
      result = $.parseJSON(data);
      if(result != null){
        $("#form-widgets-teacher_manager").val(result['user']);
        $("#form-widgets-teacher_fullname").val(result['fullname']);
        $("#form-widgets-teacher_email").val(result['email']);
        $("#form-widgets-dept").val(result['dept']);
      }
    }
  });
}

$.ajax({
  type: 'POST',
  data: { "teacher" : $("#form-widgets-teacher_manager-modal").data("user") },
  url: 'getTeacher',
  success: function(data){
    results = $.parseJSON(data);
    if(results != null && results.length > 0){
      $("#form-widgets-teacher_manager-hint > tbody").html("");
      $.each( results, function( key, value ){
        $("#form-widgets-teacher_manager-hint").show();
        field = "<tr>";
        field += "<td class='teacher'>" + value['user'] + "</td>";
        field += "<td class='fullname'>" + value['fullname'] + "</td>";
        field += "<td class='email'>" + value['email'] + "</td>";
        field += "<td class='dept'>" + value['dept'] + "</td>";
        field += "<td scope='row' class='actions'>";
        field += "<a class='label add' alt='add' onclick='addTeacher(this)'>";
        field += "<i class='bi bi-plus'></i>";
        field += "</a>";
        field += "</td>";
        field += "</tr>";
        $("#form-widgets-teacher_manager-hint").append(field);
      });
    }else{
      $("#form-widgets-teacher_manager-warn").addClass("viewWarn");
    }
  }
});
