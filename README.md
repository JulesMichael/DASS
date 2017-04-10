# DASS
Dynamically Awesome StyleSheets


Dass is a SCSS-like and SASS-like project. The goal of the project is to make a dynamic css-like langage. For exemple the langage can be used to make dashboard or web app simply. The langage be parsed by the server. In future we may make the parser with the web browser via Pepper. 


#Why DASS and not just CSS and JS ?

DASS was designed to create webapp and interactive dashboard. DASS wasn't mode for all your projects.

# Components:

All elements are bound to change.

## Variables 

```
$variable = "This is my var";
```

## Comments:
```
// My comment
```

## Conditions:

```
if my_condition :
    ...

elif my_condition :
    ...

else :
    ...

```

## Functions:

```
function function_name (arg):
    color: arg;
```

## CSS rules:

## Simple:

```
h1 :
    color : #FFF;
    background-color: #000;

```

## With events:

```
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

```
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

![screenshot](https://raw.githubusercontent.com/JulesMichael/DASS/master/screen.png)
![screenshot](https://raw.githubusercontent.com/JulesMichael/DASS/master/screen-2.png)