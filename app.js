$(document).ready(function() {
    // loop through each slider input
    $('.slider').each(function() {
      // get the id of the corresponding div to update
      var id = $(this).attr('id').replace('myRange', 'starno');
      // set the initial value of the div
      $('#' + id).text('Result: ' + $(this).val() + ' ⭐️');
      // update the div when the slider value is changed
      $(this).on('input', function() {
        $('#' + id).text('Result: ' + $(this).val() + ' ' + '⭐️'.repeat($(this).val()));
      });
    });
  });