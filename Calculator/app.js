    function retainInput() {
        var calculatorDisplayValue = document.getElementById("inputBox").textContent
    }

    function buttonClick(key){

        usrInput = document.getElementById('inputBox').textContent;

        if (key=="C"){
            document.getElementById("inputBox").textContent = ""
            
        } else if (key=="="){

            try {
                content = eval(document.getElementById("inputBox").textContent)
                document.getElementById("inputBox").textContent = content;
            }
            catch(err) {
                document.getElementById("errorOutput").innerHTML = err.message;
            }
            
        } else {
            console.log(key,usrInput);
            let content = usrInput.concat("",key);
            document.getElementById("inputBox").textContent = content;
        }
    }


