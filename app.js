const slider = $('#myRange');
const output = $('#starno');

slider.on('input', function () {
    let no = "";
    for (var i = 0; i < this.value; i++) {
        no += '⭐️';
    }
    output.text(slider.val() + " " + no);
});
$('#sendFeedbackbtn').click(function () {
    const msg = document.getElementById("msg").value;
    const srtno = $('#myRange').val();
    const name = $('#name').val();
    var compldReq = { "name": name, "stars": srtno, "fedbakmsg": msg };
    console.log(compldReq);
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(compldReq),
        dataType: 'json',
        url: 'https://feedback.bhuvansa.ml/submit'
    });
    document.body.classList.add("sent");
});


