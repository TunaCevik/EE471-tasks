let currentInput = '0';
let previousInput = '';
let operation = undefined;
let shouldResetScreen = false;

const display = document.getElementById('display');

function updateDisplay() {
    display.innerText = currentInput;
}

function formatNumber(num) {
    if (isNaN(num)) return "Error";
    // Avoid floating point inaccuracies up to 10 decimal digits
    return (Math.round(num * 10000000000) / 10000000000).toString();
}

function appendNumber(number) {
    if (currentInput === '0' && number !== '.') {
        currentInput = number;
    } else if (shouldResetScreen) {
        currentInput = number;
        shouldResetScreen = false;
    } else {
        if (number === '.' && currentInput.includes('.')) return;
        currentInput += number;
    }
    updateDisplay();
}

function chooseOperation(op) {
    if (currentInput === '' && previousInput === '') return;
    
    // If we click an operator after just getting a result, we continue with that result
    if (previousInput !== '' && !shouldResetScreen) {
        compute();
    }
    
    operation = op;
    previousInput = currentInput;
    shouldResetScreen = true;
}

function compute() {
    let computation;
    const prev = parseFloat(previousInput);
    const current = parseFloat(currentInput);
    
    if (isNaN(prev) || isNaN(current)) return;

    switch (operation) {
        case '+':
            computation = prev + current;
            break;
        case '-':
            computation = prev - current;
            break;
        case 'x':
            computation = prev * current;
            break;
        case '÷':
            if (current === 0) {
                alert("Cannot divide by zero");
                clear();
                return;
            }
            computation = prev / current;
            break;
        case '^':
            computation = Math.pow(prev, current);
            break;
        default:
            return;
    }

    currentInput = formatNumber(computation);
    operation = undefined;
    previousInput = '';
    shouldResetScreen = true;
    updateDisplay();
}

function computeSingleTarget(func) {
    if (currentInput === '') return;
    const current = parseFloat(currentInput);
    if (isNaN(current)) return;

    let computation;
    switch (func) {
        case 'sin':
            // Assume input is in degrees for user convenience
            computation = Math.sin(current * (Math.PI / 180));
            break;
        case 'cos':
            computation = Math.cos(current * (Math.PI / 180));
            break;
        case 'tan':
            computation = Math.tan(current * (Math.PI / 180));
            break;
        case 'log':
            if (current <= 0) {
                alert("Invalid input for log");
                return;
            }
            computation = Math.log10(current);
            break;
        case 'ln':
            if (current <= 0) {
                alert("Invalid input for ln");
                return;
            }
            computation = Math.log(current);
            break;
        case 'sqrt':
            if (current < 0) {
                alert("Invalid input for square root");
                return;
            }
            computation = Math.sqrt(current);
            break;
        default:
            return;
    }

    currentInput = formatNumber(computation);
    shouldResetScreen = true;
    updateDisplay();
}

function appendConstant(constant) {
    if (constant === 'π') {
        currentInput = formatNumber(Math.PI);
    } else if (constant === 'e') {
        currentInput = formatNumber(Math.E);
    }
    shouldResetScreen = true;
    updateDisplay();
}

function clear() {
    currentInput = '0';
    previousInput = '';
    operation = undefined;
    updateDisplay();
}

// Keyboard functionality for an enhanced user experience
window.addEventListener('keydown', (e) => {
    if (e.key >= 0 && e.key <= 9) appendNumber(e.key);
    if (e.key === '.') appendNumber(e.key);
    if (e.key === '=' || e.key === 'Enter') {
        e.preventDefault(); // prevent triggering buttons
        compute();
    }
    if (e.key === 'Escape') clear();
    if (e.key === '+') chooseOperation('+');
    if (e.key === '-') chooseOperation('-');
    if (e.key === '*') chooseOperation('x');
    if (e.key === '/') chooseOperation('÷');
    if (e.key === '^') chooseOperation('^');
    if (e.key === 'Backspace') {
        if (shouldResetScreen) return;
        currentInput = currentInput.slice(0, -1);
        if (currentInput === '') currentInput = '0';
        updateDisplay();
    }
});
