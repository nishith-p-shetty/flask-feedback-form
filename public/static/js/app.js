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