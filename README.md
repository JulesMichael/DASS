# DASS
Dynamically Awesome StyleSheets


Dass is a SCSS-like and SASS-like project. The goal of the project is to make a dynamic css-like langage. For exemple the langage can be used to make dashboard or web app simply. The langage be parsed by the server. In future we may make the parser with the web browser via Pepper. 

# Components:

All elements are bound to change.

## Variables :

```css
§variable = "This is my var";
```

## Comments
```css
// My comment
```

## Conditions :

```css
if my_condition :
    ...

elif my_condition :
    ...

else :
    ...

```

## Functions

```css
function function_name (arg):
    color: arg;
```

## CSS rules

## Simple

```css
h1 :
    color : #FFF;
    background-color: #000;

```

## With events:

```css
.card:
    background-color: #fff;
    padding: 10px;
    border-radius: 3px;

&:hover :
    background-color: red;
    .content :
        color: #fff;
```

## In DASS you can execute JS:

```css
.card:
    background-color: #fff;
    padding: 10px;
    border-radius: 3px;

&:hover :
    background-color: red;
    .content :
        color: #fff;
    console.log("I'm a javascript line");
```

# Made with DASS:

![screenshot](https://raw.githubusercontent.com/JulesMichael/DASS/master/screenshot.png)