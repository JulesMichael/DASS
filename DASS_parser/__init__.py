import re
import ast
import urllib.parse
import os
from hamlpy.hamlpy import Compiler
import shutil


#
# TEMPLATE FOR BLOCKS
#


class block(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


#
# DASS PARSER
#

class js():
    def style(selector, property, value):
        s = """style("{selector}","{property}","{value}");"""
        s = s.format(selector=selector, property=property, value=value)
        return s


class Parser():

    def __init__(self, text, mode="lax", min=True):
        # Vars
        self.text = text
        self.__str__ = ""
        self.mode = mode
        self.vars = {}
        self.min = min
        # Processing
        try:
            self.__creatIndentation()
            self.__creatBlocks()
            self.__toClass()
            self.__toStr()
        except Exception as e:
            print("[ERROR]: File can't be parsed.")
            print(e)
            exit()

    def __creatIndentation(self):
        """
        First part of parsing. Find indentation for all lines.
        """
        self.indentationList = []
        self.lines = []
        for line in self.text.split("\n"):
            if len(line) > 0:
                if line[0] == " ":
                    newLine = line.lstrip(" ")
                    lineIndentation = len(line) - len(line.lstrip(" "))
                elif line[0] == "\t":
                    newLine = line.lstrip("\t")
                    lineIndentation = len(line) - len(line.lstrip("\t"))
                else:
                    newLine = line
                    lineIndentation = 0

                self.lines.append(newLine.strip())
                self.indentationList.append(lineIndentation)

    def __creatBlocks(self):
        """
        Second part of parsing. Find blocks and creat a list.
        """
        w = list(zip(self.lines, self.indentationList))
        self.blocks, indentation, level = "[", 0, 0
        for i in w:
            if i[1] > indentation:
                level = level + 1
                self.blocks += ",[" + '"' + urllib.parse.quote_plus(i[0]) + '"'
            elif i[1] == 0:
                if len(self.blocks) > 1:
                    self.blocks += "]" * (level) + ','
                self.blocks += '"' + urllib.parse.quote_plus(i[0]) + '"'
                level = 0
            elif i[1] < indentation:
                if w.index(i) != len(w):
                    self.blocks += "]" + "," + '"' + \
                        urllib.parse.quote_plus(i[0]) + '"'
                    level += -1
            elif i[1] == indentation:
                self.blocks += "," + '"' + urllib.parse.quote_plus(i[0]) + '"'
            indentation = i[1]
        self.blocks += "]" * (level + 1)
        try:
            self.blocks = ast.literal_eval(self.blocks)
        except Exception as e:
            print("[ERROR]: File can't be parsed.")
            print(e)
            exit()

    def __toClass(self):
        """
        Fird part of parsing. Transform text into class.
        """
        def parse(subject):
            for i in range(len(subject)):
                if type(subject[i]) == str:
                    theStr = urllib.parse.unquote_plus(subject[i])
                    commentaireRegex = re.match(r"//( )?(.*)", theStr)
                    conditionIfRegex = re.match(r"if (.*):", theStr)
                    conditionElseRegex = re.match(r"else( )?:", theStr)
                    conditionElifRegex = re.match(r"elif (.*):", theStr)
                    varriableRegex = re.match(
                        re.escape("$") + r"([A-Za-z0-9_-]*)( )?=( )?(.*)", theStr)
                    functionRegex = re.match(
                        r"^function (.*)( )?\((.*)\)()?:", theStr)
                    regleRegex = re.match(r"^(.*)( )?:( )?(.*);", theStr)
                    selectorRegex = re.match(r"^(.*)( )?:$", theStr)
                    if commentaireRegex:
                        subject[i] = block(
                            type="commentaire", value=commentaireRegex.group(2))
                    elif conditionIfRegex:
                        subject[i] = block(type="conditionIf", condition=conditionIfRegex.group(
                            1), content=parse(subject[i + 1]))
                        subject[i + 1] = None
                    elif conditionElseRegex:
                        subject[i] = block(
                            type="conditionElse", content=parse(subject[i + 1]))
                        subject[i + 1] = None
                    elif conditionElifRegex:
                        subject[i] = block(type="conditionElif", condition=conditionElifRegex.group(
                            1), content=parse(subject[i + 1]))
                        subject[i + 1] = None
                    elif varriableRegex:
                        subject[i] = block(type="variable", name=varriableRegex.group(
                            1), value=varriableRegex.group(4))
                        self.vars[varriableRegex.group(
                            1)] = varriableRegex.group(4)
                    elif functionRegex:
                        subject[i] = block(type="function", name=functionRegex.group(
                            1) or "", args=functionRegex.group(3).split(","), content=parse(subject[i + 1]))
                        subject[i + 1] = None
                    elif regleRegex:
                        subject[i] = block(type="regle", property=regleRegex.group(
                            1), value=regleRegex.group(4))
                    elif selectorRegex:
                        subject[i] = block(type="selector", selector=selectorRegex.group(
                            1), content=parse(subject[i + 1]))
                        subject[i + 1] = None
                    else:
                        content = ""
                        if (i + 1) < len(subject):
                            if type(subject[i + 1]) == list:
                                content = parse(subject[i + 1])
                                subject[i + 1] = None
                        subject[i] = block(type="unknown", value=theStr, content = content)
                elif type(subject[i]) == list:
                    subject[i] = parse(subject[i])
            while None in subject:
                subject.remove(None)
            return subject
        self.blocks = parse(self.blocks)

    def __toStr(self):
        """
        Fourth part of parsing. Transform class to JS text.
        """
        dassJs = open("dass.js", "r").read()
        if self.min:
            dassJs = dassJs.split("\n")
            dassJs = list(map(lambda line: line.strip(" "), dassJs))
            dassJs = list(map(lambda line: line.strip("\t"), dassJs))
            dassJs = "".join(dassJs)

        def blockToJS(subject):
            toReturn = ""
            if type(subject) == list:
                for i in subject:
                    if type(i) == block:
                        if i.type == "conditionIf":
                            toReturn += "if (" + i.condition + \
                                ") {" + blockToJS(i.content) + "}"
                        elif i.type == "conditionElse":
                            toReturn += "else {" + blockToJS(i.content) + "}"
                        elif i.type == "conditionElif":
                            toReturn += "if (" + i.condition + \
                                ") {" + blockToJS(i.content) + "}"
                        elif i.type == "variable":
                            toReturn += "var " + i.name + " = " + i.value + ";"
                        elif i.type == "function":
                            toReturn += "function " + i.name + \
                                "(" + ",".join(i.args) + \
                                "){" + blockToJS(i.content) + "}"
                        elif i.type == "selector":
                            if i.selector.strip(" ")[0] != "&":
                                for item in i.content:
                                    if item.type == "regle":
                                        selector = i.selector.strip(" ")
                                        property = item.property.strip(" ")
                                        value = item.value
                                        toReturn += js.style(selector,
                                                             property, value)
                                    else:
                                        toReturn += blockToJS([item])
                            else:
                                newSelector = subject[
                                    subject.index(i) - 1].selector
                                if i.selector.strip(" ")[1:] == ":hover":
                                    toReturn += """onmouseover("{selector}",function (){{""".format(
                                        selector=newSelector)
                                    for item in i.content:
                                        if item.type == "regle":
                                            selector = newSelector
                                            property = item.property.strip(" ")
                                            value = item.value
                                            toReturn += js.style(selector,
                                                                 property, value)
                                        else:
                                            toReturn += blockToJS([item])
                                    toReturn += "});"
                                elif i.selector.strip(" ")[1:] == ":unhover":
                                    toReturn += """onmouseout("{selector}",function (){{""".format(
                                        selector=newSelector)
                                    for item in i.content:
                                        if item.type == "regle":
                                            selector = newSelector
                                            property = item.property.strip(" ")
                                            value = item.value
                                            toReturn += js.style(selector,
                                                                 property, value)
                                        else:
                                            toReturn += blockToJS([item])
                                    toReturn += "});"

                            if i.selector.strip(" ")[1:] in [":hover", ":unhover"]:
                                i.selector = newSelector
                        elif i.type == "unknown":
                            if self.mode == "lax":

                                toReturn += i.value
                                toReturn += ("".join(list(map(lambda i: blockToJS(i),i.content))))

                            elif self.mode == "strict":
                                print("[ERROR]: \"" + i.value +
                                      "\" can't be parsed")
                            else:
                                print("[ERROR]: \"" + self.mode +
                                      "\" mode doesn't exist.")
                    elif type(subject) == list:
                        toReturn += blockToJS(i)
            elif type(subject) == block:
                toReturn += blockToJS([subject])
            return toReturn
        self.__str__ = dassJs + blockToJS(self.blocks)
        return self.__str__

#
# Compile a project
#


def parseHaml(raw_text):
    c = Compiler()
    return c.process(raw_text)


def parseDass(raw_text, min):
    return Parser(raw_text, min=min).__str__


def compileProject(baseDir, destination=None, min=True):

    if os.path.exists(os.path.join(baseDir, "datas.json")):
        pass
        # TO DO => JINJA2 => TEMPLATE RENDER
        ## template = Template('Hello {{ name }}!')
        ## template.render(name='John Doe')

    # Check if dir exists and make it
    if not destination:
        destination = os.path.dirname(baseDir) if os.path.dirname(
            baseDir) != "" else baseDir + "_output"
    if os.path.exists(destination):
        shutil.rmtree(destination)
    os.mkdir(destination)
    # Create lists of files

    files = list()
    # folder = list() => TODO
    dassFiles = list()
    otherFiles = list()
    hamlFiles = list()
    for entry in os.walk(baseDir):
        for i in entry[2]:
            files.append(os.path.join(entry[0], i))
    for path in files:
        b = os.path.splitext(path)
        extension = b[1]
        if extension in [".dass", ".DASS"]:
            dassFiles.append(path)
        elif extension in [".haml", ".HAML", ".PHP", ".php"]:
            hamlFiles.append(path)
        else:
            otherFiles.append(path)

    # Parse files and create new files

    for file in otherFiles:
        shutil.copyfile(file, file.replace(baseDir, destination))

    for file in dassFiles:
        d = file.replace(baseDir, destination)
        fileContent = parseDass(open(file, "r").read(), min)
        open(d.replace(os.path.splitext(d)[1], ".js"), "w").write(
            fileContent)

    for file in hamlFiles:
        d = file.replace(baseDir, destination)
        fileContent = parseHaml(open(file, "r").read())
        open(d.replace(os.path.splitext(d)[1], ".html" if os.path.splitext(d)[1] in [".haml", ".HAML"] else os.path.splitext(d)[1].lower()), "w").write(
            fileContent)
