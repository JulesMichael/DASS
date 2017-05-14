import re
import ast
import urllib.parse
import os
from hamlpy.hamlpy import Compiler
import shutil


#
# BLOCKS
#

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class block(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def size(self, value: str):
        self.type = "variable"
        self.str = '"{value}"'.format(value=value)
        sizeRegex = re.match("(?P<number>[0-9]*)(?P<unit>.*)", value)
        self.int = int(sizeRegex.group("number"))
        self.unit = sizeRegex.group("unit")
        return self

    def regle(self, value: str):
        self.type = "variable"
        simpleRegleRegex = r"^\[{0}(?P<property>[A-Za-z-]*)\s?:\s?(?P<value>.*)\]{0}$"
        multipleRegleRegex = r"^\[(?P<reglesList>.*)\]$"
        simpleRegle = re.match(simpleRegleRegex, value)
        multipleRegle = re.match(multipleRegleRegex, value)
        if simpleRegle:
            self.str = '"{value}"'.format(value=value)
        elif multipleRegle:
            reglesList = multipleRegle.group("reglesList").split(";")
            self.str = str(reglesList)
        return self


class js():
    def style(selector: str, property: str, value: str):
        style = """style("{selector}","{property}","{value}");"""
        style = style.format(selector=selector, property=property, value=value)
        return style

    def function(name: str, content: str, args: list = list()):
        function = "function " + name + \
            "(" + ",".join(args) + \
            "){" + blockToJS(content) + "}"
        return function

#
# Regex
#


def lineMatchWith(strToTest: str):
    # "variable": re.escape("$") + r"^(?P<type>\w*)\s(?P<name>[A-Za-z0-9_-]*)\s?=\s?(?P<value>.*);$"
    regexs = {
        "commentaire": r"^//\s?(?P<comment>.*)$",
        "conditionIf": r"^if (.*):$",
        "conditionElse": r"^else\s?:$",
        "conditionElif": r"^elif (.*):$",
        "variable": r"^(?P<type>\w*)\s(?P<name>[A-Za-z0-9_-]*)\s?=\s?(?P<value>.*);$",
        "function": r"^function (?P<name>.*)\s?\((?P<args>.*)\)()?:$",
        "regle": r"^(?P<property>[\w-]*)\s?:\s?(?P<value>.*);$",
        "selector": r"^(//){0}(?P<selector>[\w \.#,]+):$"
    }
    for regexName, regex in regexs.items():
        attempt = re.match(regex, strToTest)
        if attempt:
            return (regexName, attempt)
    return False


class Parser():

    def __init__(self, text, mode: str = "lax", min: bool=True):
        # Vars
        self.text = text
        self.__str__ = ""
        self.mode = mode
        self.vars = {}
        self.selector = {}
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
        self.blocks = ast.literal_eval(self.blocks)

    def __toClass(self):
        """
        Fird part of parsing. Transform text into class.
        """
        def parse(subject):
            for i in range(len(subject)):
                if type(subject[i]) == str:
                    line = urllib.parse.unquote_plus(subject[i]).strip()
                    isMatched = lineMatchWith(line)
                    if isMatched:
                        matchedRegex = isMatched[0]
                        matchedGroups = isMatched[1]
                        blockType = matchedRegex
                        if matchedRegex == "commentaire":
                            subject[i] = block(
                                value=matchedGroups.group("comment")
                            )
                        elif matchedRegex == "conditionIf":
                            subject[i] = block(
                                condition=matchedGroups.group(1),
                                content=parse(subject[i + 1])
                            )

                        elif matchedRegex == "conditionElse":
                            subject[i] = block(
                                content=parse(subject[i + 1])
                            )
                        elif matchedRegex == "conditionElif":
                            subject[i] = block(
                                condition=matchedGroups.group(1),
                                content=parse(subject[i + 1])
                            )
                        elif matchedRegex == "variable":
                            name = matchedGroups.group("name")
                            try:
                                value = getattr(
                                    block(),
                                    matchedGroups.group("type")
                                )(
                                    matchedGroups.group("value")
                                )
                            except AttributeError:
                                value = matchedGroups.group("value")

                            subject[i] = block(
                                name=name,
                                value=value
                            )
                            self.vars[name] = value
                        elif matchedRegex == "function":
                            subject[i] = block(
                                name=matchedGroups.group("name") or "",
                                args=matchedGroups.group("args").split(","),
                                content=parse(subject[i + 1])
                            )
                        elif matchedRegex == "regle":
                            subject[i] = block(
                                property=matchedGroups.group("property"),
                                value=matchedGroups.group("value")
                            )
                        elif matchedRegex == "selector":
                            subject[i] = block(
                                selector=matchedGroups.group("selector"),
                                content=parse(subject[i + 1])
                            )
                    else:
                        blockType = "unknown"
                        content = ""
                        if (i + 1) < len(subject):
                            if type(subject[i + 1]) == list:
                                content = parse(subject[i + 1])
                        subject[i] = block(
                            value=line,
                            content=content
                        )
                    if subject[i].__dict__.get("content", "") != "":
                        subject[i + 1] = None
                    subject[i].type = blockType

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
                            if type(i.value) == block:
                                value = i.value.str
                            else:
                                value = i.value
                            toReturn += "var " + i.name + " = " + value + ";"
                        elif i.type == "function":
                            toReturn += js.function(
                                i.name,
                                blockToJS(i.content),
                                args=i.args
                            )
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
                                        selector=newSelector
                                    )
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
                                toReturn += ("".join(
                                    list(
                                        map(
                                            lambda i: blockToJS(i),
                                             i.content)
                                    )
                                )
                                )

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
        # template = Template('Hello {{ name }}!')
        # template.render(name='John Doe')

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
