# coding=utf-8
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, Field, field
from enum import auto, Enum
from pathlib import Path
from typing import NamedTuple, Optional, TextIO, TYPE_CHECKING

import typing_extensions

from . import sentence

sf = sentence.sf


def prefixSentenceParser(string, symbols=None):
    """
    Parses a sentence from its prefix form

    @param string - A string representation of a sentence
    @param symbols - A dict of symbols to use.  Valid keys are: 'variable', 'wff',
    'openParen', 'closeParen', 'seperator'

    @return - A sentence parsed from the string
    """

    if symbols is None:
        symbols = {}

    if "variable" not in symbols:
        symbols["variable"] = "?"

    if "wff" not in symbols:
        symbols["wff"] = "@"

    if "openParen" not in symbols:
        symbols["openParen"] = "("

    if "closeParen" not in symbols:
        symbols["closeParen"] = ")"

    if "openOpParen" not in symbols:
        symbols["openOpParen"] = "["

    if "closeOpParen" not in symbols:
        symbols["closeOpParen"] = "]"

    if "seperator" not in symbols:
        symbols["seperator"] = ","

    if "newVar" not in symbols:
        symbols["newVar"] = "$"

    def init(string):
        # ForAll[?x](...)
        # if symbols['openOpParen'] in string and symbols['openParen'] != symbols[
        # 'openOpParen']:
        # newSymbols = dict(symbols)
        # newSymbols['openParen'] = symbols['openOpParen']
        # newSymbols['closeParen'] = symbols['closeOpParen']
        # newSymbols['openOpParen'] = symbols['openParen']
        # newSymbols['closeOpParen'] = symbols['closeParen']
        # return prefixSentenceParser(string, newSymbols)

        # If the operator starts with the variableSymbol then make it a generic operator
        # @P
        if string.startswith(symbols["wff"]):
            return sf.generateWff(string[len(symbols["wff"]) :], symbols["wff"])

        # ?x
        if string.startswith(symbols["variable"]):
            return sf.generateVariable(
                string[len(symbols["variable"]) :], symbols["variable"]
            )
        else:
            # Otherwise make it a literal
            return sf.generateLiteral(string)

    def findMatch(string, pos, endSymbol, direction=1):
        depth = 1
        startSymbol = string[pos]
        while depth > 0:
            pos += direction
            if string[pos] == startSymbol:
                depth += 1
            elif string[pos] == endSymbol:
                depth -= 1
        return pos

    def splitArgs(string, symbols):
        # A                     -> ['A']
        # (A)                   -> ['A']
        # (not(A))              -> ['not', 'A']
        # not(A)                -> ['not', 'A']
        # and(A, B)             -> ['and', 'A', 'B']
        # and(not(A), B)        -> ['and', 'not(A)', 'B']
        # and(not(A), or(B, C)) -> ['and', 'not(A)', 'or(B, C)']
        # P[x]                  -> ['P', 'x']
        # P[s(x)]               -> ['P', 's(x)']
        # P[s(x, y)]            -> ['P', 's(x, y)']
        # ForAll(x, P(x))
        # ForAll(x, P(s(x)))
        # ForAll(x, P[x])
        # ForAll(x, P[s(x)])
        # ForAll(x, P(x, a))
        # ForAll(x, P(x, A(a)))
        # ForAll(x, P(x, A(a, b)))

        # Remove whitespace
        string = "".join(string.split())

        # Find the first paren
        firstP = string.find(symbols["openParen"])
        firstOpP = string.find(symbols["openOpParen"])

        # Find the matching paren
        try:
            otherP = findMatch(string, firstP, symbols["closeParen"])
        except IndexError:
            otherP = -1

        try:
            otherOpP = findMatch(string, firstOpP, symbols["closeOpParen"])
        except IndexError:
            otherOpP = -1

        result = []
        oper = False

        if firstOpP < 0 or (firstP < firstOpP and firstP >= 0):
            # A                     -> ['A']
            # (A)                   -> ['A']
            # (not(A))              -> ['not', 'A']
            # not(A)                -> ['not', 'A']
            # and(A, B)             -> ['and', 'A', 'B']
            # and(not(A), B)        -> ['and', 'not(A)', 'B']
            # and(not(A), or(B, C)) -> ['and', 'not(A)', 'or(B, C)']
            # |-(@P[?a], @P[s(?a)])
            # ForAll(x, P(x))
            # ForAll(x, P(s(x)))
            # ForAll(x, P[x])
            # ForAll(x, P[s(x)])
            # ForAll(x, P(x, a))
            # ForAll(x, P(x, A(a)))
            # ForAll(x, P(x, A(a, b)))

            if firstP < 0:
                # A                     -> ['A']
                return string, [], "", oper

            elif firstP == 0:
                # (A)                   -> ['A']
                # (not(A))              -> ['not', 'A']

                return splitArgs(string[1:-1], symbols)
            else:
                # not(A)                -> ['not', 'A']
                # and(A, B)             -> ['and', 'A', 'B']
                # and(not(A), B)        -> ['and', 'not(A)', 'B']
                # and(not(A), or(B, C)) -> ['and', 'not(A)', 'or(B, C)']
                # ForAll(x, P(x))       -> ['ForAll', 'x', 'P(x)']
                # ForAll(x, P(s(x)))
                # ForAll(x, P[x])
                # ForAll(x, P[s(x)])
                # ForAll(x, P(x, a))
                # ForAll(x, P(x, A(a)))
                # ForAll(x, P(x, A(a, b)))
                # |-(@P[?a], @P[s(?a)])

                # take the operator and its parens out of the string, anything after
                # the last paren is extra
                opStr, string, extra = (
                    string[:firstP],
                    string[firstP + 1 : otherP],
                    string[otherP + 1 :],
                )
        else:
            # P[x]                  -> ['P', 'x']
            # P[s(x)]               -> ['P', 's(x)']
            # P[s(x, y)]            -> ['P', 's(x, y)']

            # if otherOpP < firstP:
            # ForAll(x, P(x))       -> ['ForAll', 'P(x)']
            # ForAll(x, P(s(x)))
            # ForAll(x, P[x])
            # ForAll(x, P[s(x)])
            # ForAll(x, P(x, a))
            # ForAll(x, P(x, A(a)))
            # ForAll(x, P(x, A(a, b)))
            # ForAll[x](P(x, A(a, b)))
            #    opStr, string, extra = string[:firstP], string[firstP + 1:otherP],
            #    string[otherP + 1:]

            # else:
            # P[x]                  -> ['P', 'x']
            # P[Q[x]]               -> ['P', 'Q[x]']
            # P[s(x)]               -> ['P', 's(x)']
            # P[s(x, y)]            -> ['P', 's(x, y)']
            opStr, string, extra = (
                string[:firstOpP],
                string[firstOpP + 1 : otherOpP],
                string[otherOpP + 1 :],
            )
            oper = True

        curStr = ""
        for tok in string.split(","):
            curStr += tok
            parenCount = (
                curStr.count(symbols["openParen"])
                - curStr.count(symbols["closeParen"])
                + curStr.count(symbols["openOpParen"])
                - curStr.count(symbols["closeOpParen"])
            )

            if parenCount == 0:
                result.append(curStr)
                curStr = ""
            else:
                curStr += ","

        return opStr, result, extra, oper

    # Remove all the whitespace in the string
    string = "".join(string.split())

    # Count the difference in the number of open and close parenthesis
    parenCount = string.count(symbols["openParen"]) - string.count(
        symbols["closeParen"]
    )
    parenOpCount = string.count(symbols["openOpParen"]) - string.count(
        symbols["closeOpParen"]
    )

    # raise error if they are unequal
    if parenCount > 0:
        raise sentence.InvalidSentenceError(
            "Unmatched Close Parenthesis" + symbols["closeParen"]
        )
    elif parenCount < 0:
        raise sentence.InvalidSentenceError(
            symbols["openParen"] + "Unmatched Open Parenthesis"
        )
    elif parenOpCount > 0:
        raise sentence.InvalidSentenceError(
            "Unmatched Close Parenthesis" + symbols["closeOpParen"]
        )
    elif parenOpCount < 0:
        raise sentence.InvalidSentenceError(
            symbols["openOpParen"] + "Unmatched Open Parenthesis"
        )

    opStr, argStr, extra, oper = splitArgs(string, symbols)

    data = dict(symbols)
    data["extra"] = {}

    if extra.startswith(symbols["newVar"]):
        data["extra"]["newVars"] = [
            prefixSentenceParser(s) for s in extra.split(symbols["newVar"])[1:]
        ]

    if oper:

        data["openParen"] = symbols["openOpParen"]
        data["closeParen"] = symbols["closeOpParen"]

        op = prefixSentenceParser(opStr, data)
        args = [prefixSentenceParser(arg, symbols) for arg in argStr]
        return sf.generateOperator(op, args, data)

    if len(argStr) == 0:
        return init(opStr)

    op = prefixSentenceParser(opStr, data)
    try:
        op = sf.generateSentence(op[0], op[1:])
    except IndexError:
        pass
    args = [prefixSentenceParser(arg, symbols) for arg in argStr]
    return sf.generateSentence(op, args, data)


def defaultInferenceParser(string, sentenceParser=None):
    """
    Parses an inference into an Inference object

    @param string - A string representation of an inference rule
    @param sentenceParser - A function that parses the sentences in the inference
    rule (Defaults to prefixSentenceParser)

    @return - An inference parsed from the string
    """

    if sentenceParser is None:
        sentenceParser = prefixSentenceParser

    from .inference import Inference

    # Split the sting into lines
    lines = string.split("\n")

    # Strip all the lines
    lines = map(lambda a: a.strip(), lines)

    # Remove all blank lines
    lines = list(filter(lambda a: not len(a) == 0, lines))

    # The name is the first line
    name = lines.pop(0)

    # The conclusion is the last line
    conclusion = sentenceParser(lines.pop())

    # Each other line is a sentence of the premises
    premises = [sentenceParser(i) for i in lines]

    return Inference(name, conclusion, premises)


if TYPE_CHECKING:
    from .proof import Proof
    from .inference import Inference
    from .line import Line


class FSM_state(Enum):
    DEFAULT = auto()
    INFERENCE = auto()
    PROOF = auto()


@dataclass
class FsmData:
    queue: deque[tuple[str, int, Optional[Path]]] = field(default_factory=deque)
    proofs: dict[str, 'Proof'] = field(default_factory=dict)
    infs: 'dict[str, Inference | Proof]' = field(
        default_factory=lambda: {"Assumption": defaultInferenceParser("Assumption\n@A")}
    )
    state: FSM_state = FSM_state.DEFAULT
    include: str = "include"
    assign: str = "set"
    split: str = "\t"
    subSplit: str = ","
    path: Optional[Path] = None
    imported: set[Path] = field(default_factory=set)
    proofDone: str = "done"
    infDone: str = "done"
    proofSplit: str = "\t"
    supportSplit: str = ","
    comment: str = "#"
    range: str = "-"
    curInf: Optional[str] = None
    curProof: Optional[str] = None
    curLines: 'dict[str, Line]' = field(default_factory=dict)


def defaultProofParser(
    string: str | Path | TextIO, sentenceParser=None, inferenceParser=None
):
    """
    Takes a string or file and parses it into a proof

    @param string - The string to parse, file to use, or name of file to use
    @param sentenceParser - The parser to use to parse sentences.  Defaults to
    prefixSentenceParser
    @param inferenceParser - The parser to use to parse inferences.  Defaults to
    defaultInferenceParser
    @return - A dict of all the proofs parsed from the given input
    """
    import os

    # Path is used as the current working directory for imports
    path = Path(__file__)
    filename: Optional[Path] = None

    # Attempt to convert string into the data if it is a file or filename
    dataString: Optional[str] = None

    if isinstance(string, str):
        # Try to open the string as if it was a file
        filename = Path(string)
        if filename.exists() and filename.is_file():
            path = filename.parent
            with filename.open() as f:
                dataString = f.read()
        else:
            filename = None
            # string must be the data
            dataString = string

    elif isinstance(string, TextIO):
        # Try to read a file if it is a file
        dataString = string.read()
        filename = Path(string.name)
        path = filename.parent
    elif isinstance(string, Path):
        filename = string
        path = filename.parent
        with filename.open() as f:
            dataString = f.read()
    else:
        raise TypeError(f"Expected str or file, got {type(string)}.")

    # Set the default parsers
    if sentenceParser is None:
        sentenceParser = prefixSentenceParser
    if inferenceParser is None:
        inferenceParser = defaultInferenceParser

    def include(string: str, data: FsmData) -> None:
        toks = string.split(data.split)
        toks = list(filter(None, toks))

        keepLines = None
        if len(toks) > 2:
            keepLines = set([])
            subToks = [s.strip() for s in toks[2].split(data.subSplit)]
            for num in subToks:
                if data.range in num:
                    start, end = [int(s.strip()) for s in num.split(data.range)]
                    for i in range(start, end + 1):
                        keepLines.add(i)
                else:
                    keepLines.add(int(num))

        if len(toks) > 1:
            # Get the filename to include
            filename = Path(toks[1].strip())
        else:
            filename = Path(string[len(data.include) :].strip())

        # Check if it is a relative path, if it is get the absolute path
        if not filename.is_absolute():
            filename = data.path / filename

        # Check to see that we have not already included this file
        if filename not in data.imported or keepLines is not None:
            try:
                with open(filename) as f:
                    # Add all the new lines to the beginning of the queue
                    # e.g. q = [o1,o2,o3,o4] file = '1\n2\n3\n4\n5 -> [1,2,3,4,5,o1,
                    # o2,o3,o4]
                    lines = f.read().split("\n")
                    for n, line in enumerate(reversed(lines)):
                        lineNum = len(lines) - n
                        if keepLines is None or lineNum in keepLines:
                            data.queue.appendleft((line, lineNum, filename))

                # Add as an included file
                data.imported.add(filename)
            except IOError as e:
                raise LineError("%s %s" % (e.strerror, e.filename))

    # The function to use by default
    def init(string: str, data: FsmData) -> None:
        """
        @param string - The current line of the proof as a string
        @param data - The data of parsing the previous lines
        """
        # The initial state

        if string.startswith(data.assign):
            toks = string.split(data.split)
            toks = list(filter(None, toks))
            if len(toks) >= 3:
                setattr(data, toks[1], toks[2])

        else:
            # Set the state to the line
            match string.strip().lower():
                case '':
                    data.state = FSM_state.DEFAULT
                case 'proof':
                    data.state = FSM_state.PROOF
                case 'inference':
                    data.state = FSM_state.INFERENCE

    # The function to use while parsing an inference rule
    def inf(string: str, data: FsmData) -> None:
        """
        @param string - The current line of the proof as a string
        @param data - The data of parsing the previous lines
        """
        # We are in the inference parsing state

        # Check to see if we are done
        if string == data.infDone:
            # Use the data from the previous lines to parse the proof
            inf = inferenceParser(data.curInf, sentenceParser)

            # Add it to the data
            data.infs[inf.name] = inf

            # Reset 'curInf'
            data.curInf = None

            # Set state to default
            data.state = FSM_state.DEFAULT
            return

        # Check to see if we are in the middle of an inference rule
        if data.curInf is not None:
            # Add to the current rule
            data.curInf += "\n" + string
        else:
            # Start a new inference rule
            data.curInf = string

    # The function to use while parsing a proof
    def prf(string: str, data: FsmData) -> None:
        """
        @param string - The current line of the proof as a string
        @param data - The data of parsing the previous lines
        """
        from .proof import Proof

        # check if we are done
        if string == data.proofDone:
            # Set state to default
            data.state = FSM_state.DEFAULT

            # Reset the current proof
            data.curProof = None
            return

        # Check to see if we are in the middle of a proof
        if data.curProof is None:
            # Start a new proof
            # Name is the first line
            name = string.strip()

            # Set the current proof to name
            data.curProof = name

            # Create a new proof with this name
            data.proofs[name] = Proof(name)

            # Add it as an inference rule too
            data.infs[name] = data.proofs[name]

            # Clear the dict to store the lines
            data.curLines.clear()
            return

        # Retrieve the current proof
        curProof = data.proofs[data.curProof]

        # Retrieve the current lines
        lines = data.curLines

        # Split the line into tokens
        # Remove empty strings, this is used to allow multiple tabs between entries
        # Strip all the parts
        toks = [t.strip() for t in string.split(data.proofSplit) if t]

        # toks[0] = Line number, toks[1] = Sentence, toks[2] = Inference rule name,
        # toks[3] = support step
        if len(toks) < 2:
            # There should be at least two parts
            raise LineError("Each line should be at least two parts")

        # Parse the sentence
        curSen = sentenceParser(toks[1])

        # Add the sentence to the proof
        curProof += curSen

        # Adds the line to the dict using the line number as the key
        lines[toks[0]] = curProof[-1]

        if len(toks) == 2:
            # If there are exactly two parts, then this line is an assumption
            curProof[-1] += data.infs["Assumption"]
        if len(toks) >= 3:
            # If there are at least 3 parts then the third part is the name of the
            # inference rule to use
            try:
                curProof[-1] += data.infs[toks[2]]
            except KeyError as e:
                raise LineError(
                    "%s is not a defined inference rule or proof" % e.args[0]
                )
        if len(toks) >= 4:
            # If there are at least 4 parts then the fourth part is a list of
            # supporting lines
            try:
                for i in toks[3].split(data.supportSplit):
                    # Add each support as supporting steps
                    curProof[-1] += lines[i.strip()]
            except KeyError as e:
                raise LineError("%s is not a line" % e.args[0])

    # Finite state machine states
    fsm: dict[FSM_state, Callable[[str, FsmData], None]] = {
        FSM_state.DEFAULT: init,
        FSM_state.INFERENCE: inf,
        FSM_state.PROOF: prf,
    }

    # Create the data, used to keep track of the state of the fsm
    data = FsmData(path=path)

    # Add all of the lines from the given input
    for n, line in enumerate(dataString.split("\n")):
        data.queue.append((line, n, filename))

    while len(data.queue) > 0:
        # Grab the next line off of the queue
        line, n, filename = data.queue.popleft()

        # Retrieve the current path
        data.path = path if filename is None else filename.parent

        try:
            # Ignore everything after the comment symbol for commenting
            line = line.split(data.comment)[0].strip()

            # Ignore the line if it is blank
            if len(line) != 0:
                # Check to see if this is an 'include' statement
                if line.startswith(data.include):
                    include(line, data)
                else:
                    # Run the function corresponding to the state of the FSM
                    fsm[data.state](line, data)

        except (sentence.InvalidSentenceError, LineError) as e:
            # Raise an error to tell the user that there is a parsing error
            raise LineError(
                'Error in "%s", line %d:\t%s' % (filename, n + 1, e.args[0])
            )

    # Return all the proofs parsed
    return data.proofs


class LineError(Exception):
    """
    An Exception on a specific line while parsing the proof
    """

    pass


def main():

    formatStr = "%-40sExpected:  %s"

    sen1 = prefixSentenceParser("A")
    sen2a = prefixSentenceParser("?B")
    sen2b = prefixSentenceParser("@C")

    print(formatStr % (sen1, "A"))
    print(formatStr % (sen2a, "?B"))
    print(formatStr % (sen2b, "@C"))

    print(formatStr % (sen1.mapInto(sen2a), "[]"))
    print(formatStr % (sen1.mapInto(sen2b), "[]"))
    print(formatStr % (sen2a.mapInto(sen1), "[{?B:A}]"))
    print(formatStr % (sen2a.mapInto(sen2b), "[]"))
    print(formatStr % (sen2b.mapInto(sen1), "[{@C:A}]"))
    print(formatStr % (sen2b.mapInto(sen2a), "[{@C:?B}]"))

    sen3 = prefixSentenceParser("not(@A)")
    sen4 = prefixSentenceParser("not(or(A,not(A)))")

    print(formatStr % (sen3, "not(@A)"))
    print(formatStr % (sen4, "not(or(A,not(A)))"))
    print(formatStr % (sen4.generalize(), "not(or(@A,not(@A)))"))

    print(formatStr % (sen3.mapInto(sen4), "[{not: not, @A: or(A,not(A))}]"))
    print(formatStr % (sen4.mapInto(sen3), "[]"))

    sen5 = prefixSentenceParser("not(not(@A))")

    print(formatStr % (sen5, "not(not(@A))"))

    sen6 = prefixSentenceParser("=(+(?x, ?y), ?x)")

    sen7 = prefixSentenceParser("=(+(?a, ?b), ?a)")

    print(sen6 < sen7, sen6 <= sen7, sen6 == sen7, sen6 >= sen7, sen6 > sen7)
    print(sen7 < sen6, sen7 <= sen6, sen7 == sen6, sen7 >= sen6, sen7 > sen6)

    def normalize(sen, data):
        if "index" not in data:
            data["index"] = 0
            data["map"] = {}

        if isinstance(sen, sentence.Variable) and not isinstance(sen, sentence.Literal):
            if sen not in data["map"]:
                newSen = sf.generateVariable(chr(data["index"] + ord("a")))
                data["index"] += 1
                data["map"][sen] = newSen
            return data["map"][sen]

        return sen

    print(sen6.applyFunction(normalize))

    def subsitute(sen, data):
        if sen in data:
            return data[sen]
        return sen

    print(
        sen7.applyFunction(
            subsitute, {prefixSentenceParser("?a"): prefixSentenceParser("*(2,3)")}
        )
    )

    emptySen = prefixSentenceParser("")

    print(emptySen, emptySen.op(), emptySen.arity())

    emptyArg = prefixSentenceParser("|-(,A)")

    print("'%r', '%r', '%r'" % (emptyArg, emptyArg[0], emptyArg[1]))

    sen8 = prefixSentenceParser("ForAll[?x](?P[?x])")

    sen9 = prefixSentenceParser("ForAll[x](if(A(x),B(x)))")

    print(sen8, prefixSentenceParser("?x") in sen8)
    print(sen8[1].subsitute({prefixSentenceParser("?x"): prefixSentenceParser("a")}))

    print(sen8 < sen9)

    def cornner(sen, data):
        data["str"] += "<" + str(sen) + ">"
        return sen

    data = {"str": ""}
    sen8.applyFunction(cornner, data)
    print(data["str"])

    sen10 = prefixSentenceParser("@P[s(@x)]")

    print(sen10)


if __name__ == "__main__":
    main()