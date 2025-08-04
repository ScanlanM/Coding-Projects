window.onload = (event) => {
    sizeInputBox()
}

function retainInput() {
    var calculatorDisplayValue = document.getElementById("inputBox").textContent
}

function buttonClick(key){

    usrInput = document.getElementById('inputBox').textContent;

    if (key=="C"){
        /* Clear button to nbsp (\u00A0) to retain input box formatting*/
        document.getElementById("inputBox").textContent = "\u00A0";

    } else if (key=="="){

        try {
            stringtoEval = parenHandler(document.getElementById("inputBox").textContent)
            /*eval() is in use here, but shouldn't be used in a production environment for safety/security reasons*/
            results = eval(stringtoEval)
            document.getElementById("inputBox").textContent = results
            document.getElementById("errorOutput").innerHTML = "";
        }
        catch(err) {
            document.getElementById("errorOutput").innerHTML = err.message;
        }
        
    } else {
        content = usrInput.concat("",key);
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
function sizeInputBox(){
    calcBody = document.getElementById("calcBody")
    inputBox = document.getElementById('inputBox')

    width = window.getComputedStyle(calcBody).getPropertyValue('width');
    inputBox.style.width = width
}