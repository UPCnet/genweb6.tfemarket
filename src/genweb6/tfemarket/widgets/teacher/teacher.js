var hideElementsTeacher = function(){
  $("#form-widgets-teacher_manager-error").removeClass("viewError");
  $("#form-widgets-teacher_manager-warn").removeClass("viewWarn");
  $("#form-widgets-teacher_manager-hint > tbody").html("<tr><td/><td/><td/><td/><td/></tr>");
}

var addTeacher = function(teacher){
  parent = $(teacher).parent().parent();
  $("#form-widgets-teacher_manager").val($(parent).children('.teacher').html());
  $("#form-widgets-teacher_fullname").val($(parent).children('.fullname').html());
  $("#form-widgets-teacher_email").val($(parent).children('.email').html());
  $("#form-widgets-dept").val($(parent).children('.dept').html());
  $('#form-widgets-teacher_manager-modal').modal('toggle');
}

$("#form-widgets-teacher_manager-btn").on("click", function(){
  hideElementsTeacher();
  var regexTeacher = new RegExp('^[a-zA-ZñÑçÇ]{1,}\\.[a-zA-Z0-9-.ñÑçÇ]{1,}$');
  var teacherUser = $("#form-widgets-teacher_manager-input").val();
  if(regexTeacher.test(teacherUser)){
    $.ajax({
      type: 'POST',
      data: { "teacher" : $("#form-widgets-teacher_manager-input").val() },
      url: 'getTeacher',
      success: function(data){
        results = $.parseJSON(data);
        if(results != null && results.length > 0){
          $("#form-widgets-teacher_manager-hint > tbody").html("");
          $.each( results, function( key, value ){
            $("#form-widgets-teacher_manager-hint").show();
            field = "<tr>";
            field += "<td class='align-middle teacher'>" + value['user'] + "</td>";
            field += "<td class='align-middle fullname'>" + value['fullname'] + "</td>";
            field += "<td class='align-middle email'>" + value['email'] + "</td>";
            field += "<td class='align-middle dept'>" + value['dept'] + "</td>";
            field += "<td scope='align-middle row' class='actions'>";
            field += "<a class='btn btn-sm btn-outline-secondary label add' alt='add' onclick='addTeacher(this)'>";
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
  }else{
    $("#form-widgets-teacher_manager-error").addClass("viewError");
  }
});
