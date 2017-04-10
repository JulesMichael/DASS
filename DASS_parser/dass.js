function style(selector, property, value) {
    this.selector = selector;
    var alpha = "abcdefghijklmnopqrstuvwxyz";
    for (var i = 0; i < alpha.length; i++) {
        property.replace("-" + alpha[i], alpha[i].toUpperCase());
    }
    var l = document.querySelectorAll(this.selector);
    for (var i = 0; i < l.length; i++) {
        l[i].style[property] = value;
    }
}

function getProperty(selector, property) {
    return document.querySelector(selector).style[property];
}

function getElement(selector) {
    return document.querySelector(selector);
}

function onmouseover(selector, func) {
    document.querySelector(selector).onmouseover = func;
}

function onmouseout(selector, func) {
    document.querySelector(selector).onmouseout = func;
}