$(document).ready(function () {
  // loop through each slider input
  $(".slider").each(function () {
    // get the id of the corresponding div to update
    var id = $(this).attr("id").replace("team_id", "starno");
    // set the initial value of the div
    $("#" + id).text("Rating: " + $(this).val() + " ⭐️");
    // update the div when the slider value is changed
    $(this).on("input", function () {
      $("#" + id).text(
        "Rating: " + $(this).val() + " " + "⭐️".repeat($(this).val()),
      );
    });
  });
});

$(document).ready(function () {
  $('input').keydown(function (event) {
    if (event.keyCode == 13) {
      event.preventDefault();
      var nextInput = $('input').eq($('input').index(this) + 1);
      if (nextInput.length) {
        nextInput.focus();
      }
      return false;
    }
  });
});