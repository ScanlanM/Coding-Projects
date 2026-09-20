window.onload = () => {
    sizeInputBox();
};

function buttonClick(key) {
    const inputBox = document.getElementById('inputBox');
    const errorOutput = document.getElementById('errorOutput');

    if (key === 'C') {
        // Clear button to nbsp (\u00A0) to retain input box formatting
        inputBox.textContent = '\u00A0';
        errorOutput.textContent = '';
        return;
    }

    if (key === '=') {
        try {
            const expression = parenHandler(inputBox.textContent);
            inputBox.textContent = evaluateExpression(expression);
            errorOutput.textContent = '';
        } catch (err) {
            errorOutput.textContent = err.message;
        }
        return;
    }

    inputBox.textContent = inputBox.textContent.concat(key);
}

function parenHandler(usrInput) {
    // Need to handle "digit (" and ") digit" since implied multiplication
    // isn't valid syntax on its own.
    const rexDParen = /(\d) \(/g;
    const rexParenD = /\) (\d)/g;

    return usrInput
        .replaceAll(rexDParen, '$1*(')
        .replaceAll(rexParenD, ')*$1');
}

/**
 * Evaluate a basic arithmetic expression (+, -, *, /, %, parentheses,
 * decimals, unary minus) without eval() or the Function() constructor,
 * so user input can never run as arbitrary JavaScript.
 */
function evaluateExpression(expression) {
    return evaluateRpn(toRpn(tokenize(expression)));
}

const BINARY_OPERATORS = ['+', '-', '*', '/', '%'];
const PRECEDENCE = { '+': 1, '-': 1, '*': 2, '/': 2, '%': 2, 'u-': 3 };
const RIGHT_ASSOCIATIVE = new Set(['u-']);

function isBinaryOperator(token) {
    return BINARY_OPERATORS.includes(token);
}

function isOperatorToken(token) {
    return isBinaryOperator(token) || token === 'u-';
}

function tokenize(expression) {
    const tokenPattern = /\d+\.?\d*|\.\d+|[+\-*/%()]/g;
    const rawTokens = expression.match(tokenPattern) || [];

    const cleanedInput = expression.replaceAll(/\s/g, '');
    if (rawTokens.join('') !== cleanedInput) {
        throw new Error('Invalid characters in expression');
    }

    // Normalize unary minus (e.g. "-5", "(-5", "3*-2") into a distinct
    // "u-" token so the parser below only ever deals with two-operand
    // operators plus this one explicit one-operand case.
    const tokens = [];
    for (const token of rawTokens) {
        const prev = tokens[tokens.length - 1];
        const isUnaryMinus = token === '-' && (prev === undefined || prev === '(' || isOperatorToken(prev));
        tokens.push(isUnaryMinus ? 'u-' : token);
    }

    return tokens;
}

function toRpn(tokens) {
    const output = [];
    const operators = [];

    for (const token of tokens) {
        if (!isNaN(token)) {
            output.push(token);
        } else if (token === '(') {
            operators.push(token);
        } else if (token === ')') {
            while (operators.length && operators[operators.length - 1] !== '(') {
                output.push(operators.pop());
            }
            if (!operators.length) {
                throw new Error('Mismatched parentheses');
            }
            operators.pop();
        } else if (isOperatorToken(token)) {
            while (
                operators.length &&
                isOperatorToken(operators[operators.length - 1]) &&
                (
                    (RIGHT_ASSOCIATIVE.has(token) && PRECEDENCE[operators[operators.length - 1]] > PRECEDENCE[token]) ||
                    (!RIGHT_ASSOCIATIVE.has(token) && PRECEDENCE[operators[operators.length - 1]] >= PRECEDENCE[token])
                )
            ) {
                output.push(operators.pop());
            }
            operators.push(token);
        } else {
            throw new Error(`Unexpected token: ${token}`);
        }
    }

    while (operators.length) {
        const op = operators.pop();
        if (op === '(') {
            throw new Error('Mismatched parentheses');
        }
        output.push(op);
    }

    return output;
}

function evaluateRpn(rpn) {
    const stack = [];

    for (const token of rpn) {
        if (!isNaN(token)) {
            stack.push(parseFloat(token));
            continue;
        }

        if (token === 'u-') {
            const a = stack.pop();
            if (a === undefined) {
                throw new Error('Malformed expression');
            }
            stack.push(-a);
            continue;
        }

        const b = stack.pop();
        const a = stack.pop();
        if (a === undefined || b === undefined) {
            throw new Error('Malformed expression');
        }

        switch (token) {
            case '+': stack.push(a + b); break;
            case '-': stack.push(a - b); break;
            case '*': stack.push(a * b); break;
            case '%': stack.push(a % b); break;
            case '/':
                if (b === 0) {
                    throw new Error('Division by zero');
                }
                stack.push(a / b);
                break;
            default:
                throw new Error(`Unknown operator: ${token}`);
        }
    }

    if (stack.length !== 1) {
        throw new Error('Malformed expression');
    }

    return stack[0];
}

function sizeInputBox() {
    const calcBody = document.getElementById('calcBody');
    const inputBox = document.getElementById('inputBox');
    const width = window.getComputedStyle(calcBody).getPropertyValue('width');
    inputBox.style.width = width;
}
