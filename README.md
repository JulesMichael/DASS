# DASS
Dynamically Awesome StyleSheets


Dass is a SCSS-like and SASS-like project. The goal of the project is to make a dynamic css-like langage. For exemple the langage can be used to make dashboard or web app simply. The langage be parsed by the server. In future we may make the parser with the web browser via Pepper. 

# Components:

All elements are bound to change.

## Variables :

```
§variable = "This is my var";
```

## Conditions :

```
if my_condition :
	...

elif my_condition :
	...

else :
	...

```

## Functions

```
function function_name (arg):
	console.log(§arg);
	color: §arg;
```

## CSS rules

```
h1 :
	color : #FFF;
	background-color: #000;

```

<!---
	```
	§size = 500px
	§f_size = 20px if §html.width > §size else 10px;
	
	§animation = {
	  transition: 0.5s;
	}
	
	h1 {
	  if §html.width > §size{
	    this.add(§animation);
	  }
	  font-size: §f_size;
	}
	```
-->
