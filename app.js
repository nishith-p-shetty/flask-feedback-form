function addClass() {
    var msg = document.getElementById("msg").value;
    var srtno = document.getElementById("myRange").value;
    var name = document.getElementById("name").value;
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
}

sendFeedbackbtn.addEventListener("click", addClass);

var slider = document.getElementById("myRange");
var output = document.getElementById("starno");
output.innerHTML = slider.value + " ⭐️"; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function () {
    let no = "";
    for (var i = 0; i < this.value; i++) {
        no += '⭐️';
    }
    output.innerHTML = this.value + " " + no;
}
