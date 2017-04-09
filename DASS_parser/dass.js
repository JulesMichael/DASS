class Dass{
	construcor(){
		
	}
	m(selector,att,value){
		this.selector = selector;
		var alpha = "abcdefghijklmnopqrstuvwxyz";
		for (var i = 0; i < alpha.length; i++) {att.replace("-"+alpha[i], alpha[i].toUpperCase()) ;}
		document.querySelector(this.selector).style[att] = value;
	}
	get(selector,att){
		this.selector = selector;
		return document.querySelector(this.selector).style[att]
	}
	onmouseover(selector,func){
		this.selector = selector;
		document.querySelector(this.selector).onmouseover = func;
	}

}
$ = new Dass();