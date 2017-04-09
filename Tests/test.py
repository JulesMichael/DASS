from DASS_parser import Parser

file = "test.dass"
p = Parser(open(file,"r").read())
open(file+".js","w").write(p.__str__)