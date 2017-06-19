#!/usr/bin/python

import sys, Lexer, CFG

print sys.argv[1], sys.argv[2]

def onlyTokens(seq):
    """
    Check if sequence has only terminals or token references
    """
    for sym in seq:
        if isinstance(sym,CFG.Non_Term_Ref):
            return False
    return True

def genNonRecGrammar(g,n):
    """
    Return an non recursive grammar with n unrolls
    """

    # step 1: generate rules from 0..n-1 unrools
    symbolIndex = {}
    rules = []
    i = 0;
    for unrolls in range(0,n):
        for r in g.rules:
            if r == g.rules[0]:
                if unrolls == 0:
                    newrule = CFG.Rule(r.name,[])
                else:
                    continue # skip start rule
            else:
                newrule = CFG.Rule(r.name + str(i),[])
            for seq in r.seqs:
                newseq = [];
                for sym in seq:
                    if isinstance(sym,CFG.Non_Term_Ref):
                        name = sym.name + str(i+1)
                        newseq.append(CFG.Non_Term_Ref(name))
                        symbolIndex[sym.name] = i+1
                    else:
                        newseq.append(sym)
                newrule.seqs.append(newseq)
            rules.append(newrule)
            i = i + 1

    # step 2: generate indexed rules with only terminal sequences as rhs
    for r in g.rules:
        if r == g.rules[0]:
            continue;
        newrule = CFG.Rule(r.name + str(symbolIndex[r.name]),[])
        for seq in r.seqs:
            newseq = [];
            if onlyTokens(seq):
                for sym in seq:
                    newseq.append(sym)
                newrule.seqs.append(newseq)
        if newrule.seqs:
            rules.append(newrule)

    return CFG.CFG(g.tokens,rules)
#============= end function genNonRecGrammar ===============


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "Usage: " + sys.argv[0] + " grammar lex unrool-level"
    else:
        l = open(sys.argv[2], "r")
        g = open(sys.argv[1], "r")
        n = int(sys.argv[3])
        lex = Lexer.parse( l.read() )
        grammar = CFG.parse(lex, g.read())
        print genNonRecGrammar(grammar,n).__repr__()
