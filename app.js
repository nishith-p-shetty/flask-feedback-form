const slider = $('#myRange');
const output = $('#starno');

slider.on('input', function () {
    let no = "";
    for (var i = 0; i < this.value; i++) {
        no += '⭐️';
    }
    output.text("Rating: " + slider.val() + " " + no);
});


const forms = $('.form');
const name = forms[1].value;
console.log(forms);

for (var i = 2 ; i <= forms.length ; i++)
{
    console.log(i);
}




/*$('#sendFeedbackbtn').click(function () {
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
});*/