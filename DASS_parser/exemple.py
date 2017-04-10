from __init__ import Parser

fileContent = open("exemple_datas/test.dass","r").read()
fileOutput = "exemple_result/test.js"

output = Parser(fileContent).__str__
open(fileOutput,"w").write(output)
print(output)