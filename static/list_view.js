var $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};


$("[data-list-id=*]").click(function(){
    $.getJSON($SCRIPT_ROOT + '/')
    $(this).attr('data-list-id')
})


  $(function() {
    $('a#calculate').bind('click', function() {
      $.getJSON($SCRIPT_ROOT + '/_add_numbers', {
        a: $('input[name="a"]').val(),
        b: $('input[name="b"]').val()
      }, function(data) {
        $("#result").text(data.result);
      });
      return false;
    });
  });
