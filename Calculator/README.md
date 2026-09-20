# Calculator

A small browser calculator. Open `index.html` in a browser, no build
step or server required.

Expressions are evaluated with a hand-written tokenizer and a
shunting-yard parser in `app.js`, not `eval()`, so user input can never
run as arbitrary JavaScript.
