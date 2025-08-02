function retainInput() {
    var calculatorDisplayValue = document.getElementById("inputBox").textContent
}

function buttonClick(key){

    usrInput = document.getElementById('inputBox').textContent;

    if (key=="C"){
        document.getElementById("inputBox").textContent = ""

    } else if (key=="="){

        try {
            stringtoEval = parenHandler(document.getElementById("inputBox").textContent)
            results = eval(stringtoEval)
            document.getElementById("inputBox").textContent = results
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

function parenHandler(usrInput){
    /*need to handle d paren and paren d since eval doesn't recognize this as implied multiplication*/

    rexDParen = /(\d) \(/g;
    rexDParenReplacement = "$1*\("

    rexParenD = /\) (\d)/g;
    rexParenDReplacement = ")*$1"

    stringtoEval = usrInput;

    stringtoEval = stringtoEval.replaceAll(rexDParen,rexDParenReplacement);
    stringtoEval = stringtoEval.replaceAll(rexParenD,rexParenDReplacement);

    return stringtoEval

}
