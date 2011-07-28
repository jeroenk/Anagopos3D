# -*- coding: utf-8 -*-
# Anagopos 3D: A Reduction Graph Visualizer for Term Rewriting and λ-Calculus
#
# Copyright (C) 2011 Jeroen Ketema
#
# Reduction Visualizer. A tool for visualization of reduction graphs.
# Copyright (C) 2010 Niels Bjoern Bugge Grathwohl and Jens Duelund Pallesen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import xml.parsers.expat

from TRSTermClass import TRSFunctionSymbol, TRSFun, TRSVar, TRSRule

class TRSParseException(Exception):
    pass

parser = xml.parsers.expat.ParserCreate()

# Enumerated types and global variables to keep track of where we are during
# the parsing.
top_level, lower_level = range(2)
level = top_level

trs_level, strategy_level, start_level, status_level, metainfo_level = range(5)
sublevel = None

rules_level, sig_level, ho_sig_level, comment_level, condition_level = range(5)
trslevel = None

func_level = range(1)
siglevel = None

name_level, arity_level, theory_level, repl_level = range(4)
funclevel = None

rule_level, relrules_level = range(2)
ruleslevel = None

lhs_level, rhs_level, conditions_level = range(3)
rulelevel = None

fun_level, fun_name_level, fun_arg_level, var_level, \
    lambda_level, app_level = range(6)
termlevel = []

# For parsing signatures:
signature   = {}
func_symbol = None
arity       = None

# For parsing rules:
rules = []
lhs   = None
rhs   = None

# For parsing terms:
symbolstack   = []
subterms      = []
subterm_count = []
term          = None

def reset_global():
    global parser, level, sublevel, trslevel, siglevel, funclevel, ruleslevel, \
        rulelevel, termlevel, signature, func_symbol, arity, rules, lhs, rhs, \
        symbolstack, subterms, subter,_count, term

    parser = xml.parsers.expat.ParserCreate()

    level      = top_level
    sublevel   = None
    trslevel   = None
    siglevel   = None
    funclevel  = None
    ruleslevel = None
    rulelevel  = None

    termlevel = []

    signature   = {}
    func_symbol = None
    arity       = None

    rules = []
    lhs   = None
    rhs   = None

    symbolstack   = []
    subterms      = []
    subterm_count = []
    term          = None

def start_problem(name, attrs):
    global level

    # We ignore whether we are dealing with a "termination" or "complexity"
    # problem. In both cases we are dealing with a TRS after all.
    level = lower_level

def start_term(name, attrs):
    global termlevel, subterm_count

    length = len(termlevel)

    if length == 0 or termlevel[length - 1] == fun_arg_level:
        if name == "funapp":
            termlevel.append(fun_level)
            subterm_count.append(0)
        elif name == "var":
            termlevel.append(var_level)
        elif name == "lambda" or name == "application":
            raise TRSParseException("Higher-order rewrite systems unsupported")
        else:
            raise TRSParseException("Unexpected element " + name)
    elif termlevel[length - 1] == fun_level:
        if name == "name":
            termlevel.append(fun_name_level)
        elif name == "arg":
            termlevel.append(fun_arg_level)
            count = subterm_count.pop() + 1
            subterm_count.append(count)
        else:
            raise TRSParseException("Unexpected element " + name)
    else:
        raise TRSParseException("Unexpected element " + name)

def start_rule(name, attrs):
    global rulelevel

    if rulelevel == None:
        if name == "lhs":
            rulelevel = lhs_level
        elif name == "rhs":
            rulelevel = rhs_level
        elif name == "conditions":
            raise TRSParseException("Conditional rewrite systems unsupported")
        else:
            raise TRSParseException("Unexpected element " + name)
    elif rulelevel == lhs_level or rulelevel == rhs_level:
        start_term(name, attrs)

def start_rules(name, attrs):
    global ruleslevel

    if ruleslevel == None:
        if name == "rule":
            ruleslevel = rule_level
        elif name == "relrules":
            raise TRSParseException("Relative rules not supported")
        else:
            raise TRSParseException("Unexpected element " + name)
    elif ruleslevel == rule_level:
        start_rule(name, attrs)
    # We should not reach this point in case of relative rules.

def start_signature(name, attrs):
    global siglevel, funclevel

    if siglevel == None:
        if name == "funcsym":
            siglevel = func_level
        else:
            raise TRSParseException("Unexpected element " + name)
    elif siglevel == func_level:
        if funclevel == None:
            if name == "name":
                funclevel = name_level
            elif name == "arity":
                funclevel = arity_level
            elif name == "theory":
                raise TRSParseException("Rewriting modulo theories unsupported")
            elif name == "replacementmap":
                raise TRSParseException("Replacement maps unsupported")
            else:
                raise TRSParseException("Unexpected element " + name)
        else:
            raise TRSParseException("Unexpected element " + name)

def start_trs(name, attrs):
    global trslevel

    if trslevel == None:
        if name == "rules":
            trslevel = rules_level
        elif name == "signature":
            trslevel = sig_level
        elif name == "higherOrderSignature":
            raise TRSParseException("Higher-order rewrite systems unsupported")
        elif name == "comment":
            trslevel = comment_level
        elif name == "conditiontype":
            raise TRSParseException("Conditional rewrite systems unsupported")
        else:
            raise TRSParseException("Unexpected element " + name)
    elif trslevel == rules_level:
        start_rules(name, attrs)
    elif trslevel == sig_level:
        start_signature(name, attrs)
    # We ignore what is in the comment section. If we have a higher-order
    # or conditional system we should not have reached this point.

def start_lower(name, attrs):
    global sublevel

    if sublevel == None:
        if name == "trs":
            sublevel = trs_level
        elif name == "strategy":
            sublevel = strategy_level
        elif name == "startterm":
            sublevel = start_level
        elif name == "status":
            sublevel = status_level
        elif name == "metainformation":
            sublevel = metainfo_level
        else:
            raise TRSParseException("Unexpected element " + name)
    elif sublevel == trs_level:
        start_trs(name, attrs)
    # We ignore what is in the strategy, startterm, status, and metainfomation
    # sections, as we do not need the data from those sections. Note that we
    # do not even perform santity checks on these sections.

def start_element(name, attrs):
    if level == top_level:
        start_problem(name, attrs)
    else: # level == lower_level
        start_lower(name, attrs)

def end_term(name):
    global termlevel, symbolstack, subterms, term, subterm_count, signature

    level = termlevel.pop()

    if level == fun_level:
        if name == "funapp":
            count = subterm_count.pop()
            f = symbolstack.pop()
            f_symbol = TRSFunctionSymbol(f, count)
            f_subterms = []

            if f not in signature:
                signature[f] = count
            elif signature[f] != count:
                raise TRSParseException("Arity of \"" + f +"\" is " + \
                                            str(signature[f]) + ", not " + \
                                            str(count))

            for s in subterms[len(subterms) - count:]:
                f_subterms.append(s)

            subterms = subterms[:len(subterms) - count]

            term = TRSFun(f_symbol, f_subterms)
        else:
            raise TRSParseException("Unexpected element end " + name)
    elif level == fun_name_level:
        if name != "name":
            raise TRSParseException("Unexpected element end " + name)
    elif level == fun_arg_level:
        if name == "arg":
            subterms.append(term)
        else:
            raise TRSParseException("Unexpected element end " + name)
    elif level == var_level:
        term = TRSVar(symbolstack.pop())
    else:
        raise TRSParseException("Unexpected element end " + name)

def end_rule(name):
    global rulelevel, lhs, rhs

    if rulelevel == lhs_level:
        if name == "lhs":
            lhs = term
            rulelevel = None
        else:
            end_term(name)
    elif rulelevel == rhs_level:
        if name == "rhs":
            rhs = term
            rulelevel = None
        else:
            end_term(name)
    else:
        raise TRSParseException("Unexpected element end " + name)

def end_rules(name):
    global ruleslevel, rules, lhs, rhs

    if ruleslevel == rule_level:
        if name == "rule":
            if lhs != None and rhs != None:
                rules.append((lhs, rhs))
            else:
                raise TRSParseException("Rule not completely defined")
            lhs = None
            rhs = None
            ruleslevel = None
        else:
            end_rule(name)
    else:
        raise TRSParseException("Unexpected element end " + name)

def end_signature(name):
    global siglevel, funclevel, func_symbol, arity, signature

    if siglevel == func_level:
        if name == "funcsym":
            if func_symbol != None and arity != None:
                if func_symbol not in signature:
                    signature[func_symbol] = arity
                elif signature[func_symbol] != arity:
                    raise TRSParseException("Arity of \"" + f +"\" is " + \
                                                str(signature[func_symbol]) + \
                                                ", not " + str(arity))
            else:
                raise TRSParseException("Function symbol without name or arity")
            func_symbol = None
            arity = None
            siglevel = None
        else:
            if funclevel == name_level:
                if name == "name":
                    funclevel = None
                else:
                    raise TRSParseException("Unexpected element end " + name)
            elif funclevel == arity_level:
                if name == "arity":
                    funclevel = None
                else:
                    raise TRSParseException("Unexpected element end " + name)
            else:
                raise TRSParseException("Unexpected element end " + name)
    else:
        raise TRSParseException("Unexpected element end " + name)

def end_trs(name):
    global trslevel

    if trslevel == rules_level:
        if name == "rules":
            trslevel = None
        else:
            end_rules(name)
    elif trslevel == sig_level:
        if name == "signature":
            trslevel = None
        else:
            end_signature(name)
    elif trslevel == comment_level:
        if name == "comment":
            trslevel = None
        # Ignore any subsections
    else:
        raise TRSParseException("Unexpected element end " + name)

def end_lower(name):
    global level, sublevel

    if sublevel == None:
        if name == "problem":
            level = top_level
        else:
            raise TRSParseException("Unexpected element end " + name)
    elif sublevel == trs_level:
        if name == "trs":
            sublevel = None
        else:
            end_trs(name)
    elif sublevel == strategy_level:
        if name == "strategy":
            sublevel = None
        # Ignore any subsections
    elif sublevel == start_level:
        if name == "startterm":
            sublevel = None
        # Ignore any subsections
    elif sublevel == status_level:
        if name == "status":
            sublevel = None
        # Ignore any subsections
    elif sublevel == metainfo_level:
        if name == "metoinformation":
            sublevel = None
        # Ignore any subsections
    else:
        raise TRSParseError("Unexpected element end " + name)

def end_element(name):
    if level == lower_level:
        end_lower(name)
    else:
        raise TRSParseException("Unexpected element " + name)

def char_data(data):
    global func_symbol, arity

    length = len(termlevel)

    if funclevel == name_level:
        if func_symbol == None:
            func_symbol = data
        else:
            raise TRSParseException("Function symbol has multiple names")
    elif funclevel == arity_level:
        if arity == None:
            arity = int(data)

            if str(arity) != data:
                raise TRSParseException("Invalid arity " + data)
    elif length > 0 and termlevel[length - 1] == fun_name_level:
        symbolstack.append(data)
    elif length > 0 and termlevel[length - 1] == var_level:
        symbolstack.append(data)

def TRSParseRules(file_name):
    reset_global()

    parser.StartElementHandler  = start_element
    parser.EndElementHandler    = end_element
    parser.CharacterDataHandler = char_data

    f = open(file_name, 'r')

    try:
        parser.ParseFile(f)
    except xml.parsers.expat.ExpatError as exception:
        raise TRSParseException("Parse error: " + str(exception))
    finally:
        f.close()

    rule_set = []

    for (lhs, rhs) in rules:
        if lhs.isVar():
            raise TRSParseException("LHS of a rule cannot be a variable!")

        rule_set.append(TRSRule(lhs, rhs))

    return (rule_set, signature)
