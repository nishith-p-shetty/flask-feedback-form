const slider = $("#myRange");
const output = $("#starno");

slider.on("input", function() {
    let no = "";
    let i = 0;
    for (i = 0; i < this.value; i++) {
        no += "⭐️";
    }
    output.text("Rating: " + slider.val() + " " + no);
});

const forms = $(".form");
const name = forms[1].value;
console.log(forms);

let no = 0;
let rateAr = [];
for (var i = 2; i < forms.length - 1; i++) {
    rateAr[i - 2] = [];
    for (let j = 0; j < 5; j++) {
        rateAr[i - 2][j] = no++;
    }
}
console.log(rateAr);

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

