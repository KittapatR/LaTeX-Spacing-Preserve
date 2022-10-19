import argparse
import re
import os
import glob

parser = argparse.ArgumentParser(description='Doing some LaTeX file to have a natural spacing')
parser.add_argument(
    "--filename", "-f", metavar = "-f", type = str,
    help = "put .tex file to generate spacing"
)
parser.add_argument(
    "--xelatex", "-x", help = "change mode of compilation, default: pdfLaTeX", action = "store_true"
)

args = parser.parse_args()
stack = []

def composing_text(pattern, leading, trailing):
    finalLine = leading[0] + pattern + trailing[0]\
                if leading else pattern + trailing[0]\
                if trailing else pattern
    return finalLine

with open(args.filename, encoding = "utf-8") as f:
    text = f.readlines()
    newLinesToWrite = []
    for no in range(len(text)):
        # capture keywords in the certain line by such expressions
        line = text[no]
        begin = re.finditer(r"\\begin\{([^\}]+)\}", line)
        end = re.finditer(r"\\end\{([^\}]+)\}", line)

        # collect keywords in the certain line
        check = {}
        for itemBegin in begin:
            check[itemBegin.start()] = itemBegin.group(1) + "_begin"
        for itemEnd in end:
            check[itemEnd.start()] = itemEnd.group(1) + "_end"

        # Sanity check
        indicesCheck = sorted(check)
        for index in indicesCheck:
            name, status = check[index].split("_")
            if status == "begin": stack.append(name)
            elif status == "end":
                if stack != []:
                    if name == stack[-1]: stack = stack[:-1]
                else:
                    print(f"Invalid syntax: {args.filename}")
                    print(f"Line {no}: {line}")
                    exit(1)
        
        # fill to have actual space
        leadingSpace = re.findall("^\s+", line)
        trailingSpace = re.findall("\s+$", line)
        newLine = re.sub("\s$", "", line).strip()
        if newLine == "":
            newLinesToWrite += [leadingSpace[0]]
        else:
            verb = re.finditer(r"\\verb\|[^\|]+\||\\begin{verbatim}[^\\]+\\end{verbatim}", newLine)
            fragmentedText = []
            verb = list(verb)
            for verbNo in range(len(verb)):
                fragmentedText.append(newLine[verb[verbNo - 1].end() if verbNo != 0 else 0:verb[verbNo].start()])
                fragmentedText.append(newLine[verb[verbNo].start(): verb[verbNo].end()])
            if (fragmentedText == []):
                if stack != [] and ("verbatim" in stack[-1]):
                    newLinesToWrite.append(line)
                else:
                    pattern = re.sub("\s", "\\ ", newLine) 
                    newLinesToWrite.append(composing_text(pattern, leadingSpace, trailingSpace))
            else:
                even = True
                finalFragmentedText = []
                for textFragment in fragmentedText:
                    finalFragmentedText.append(re.sub("\s", "\\ ", textFragment) if even else textFragment)
                    even = not(even)
                pattern = "".join(finalFragmentedText)
                newLinesToWrite.append(composing_text(pattern, leadingSpace, trailingSpace))
            
    with open(args.filename[:-4] + "_natural.tex", "w") as f:
        f.writelines(newLinesToWrite)

dir_name = "\\".join(args.filename.split("/")[:-1])
os.chdir(dir_name)
file_name = args.filename.split("/")[-1][:-4]

if args.xelatex:
    os.system(f"xelatex {file_name + '_natural.tex'}")
else:
    os.system(f"pdflatex {file_name + '_natural.tex'}")

os.remove(f"{file_name}_natural.tex")
os.remove(f"{file_name}_natural.aux")
os.remove(f"{file_name}_natural.log")

print("Normal termination!")