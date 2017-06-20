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

def recursiveRules(g):
    """ Get recursive rules """
    reachable_syms = {}
    for r in g.rules:
        reachable_syms[r.name] = []
        for s in r.seqs:
            for sym in s:
                if isinstance(sym,CFG.Non_Term_Ref) and not (sym in reachable_syms[r.name]):
                    reachable_syms[r.name].append(sym.name)
    changes = True
    while changes:
        changes = False
        for sym in reachable_syms.keys():
            for s in reachable_syms[sym]:
                for rs in reachable_syms[s]:
                    if not (rs in reachable_syms[sym]):
                        reachable_syms[sym].append(rs)
                        changes = True
    print "Reachable symbols:"
    print reachable_syms
    result = []
    for sym in reachable_syms.keys():
        if sym in reachable_syms[sym]:
            result.append(sym)
    print "Recursive rules:"
    print result
    return result

def genNonRecGrammar(g,n):
    """
    Return an non recursive grammar with n unrolls
    """

    # step 1: generate rules from 0..n-1 unrools
    symbolIndex = {}
    rr = recursiveRules(g)
    rules = []
    generated = []
    i = 0;
    for unrolls in range(0,n):
        for r in g.rules:
            if r.name in rr:
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
                i = i + 1
            else:
                if r.name in generated:
                    continue
                newrule = CFG.Rule(r.name,[])
                for seq in r.seqs:
                    newseq = [];
                    for sym in seq:
                        if isinstance(sym,CFG.Non_Term_Ref) and sym.name in rr:
                            name = sym.name + "0"
                            newseq.append(CFG.Non_Term_Ref(name))
                        else:
                            newseq.append(sym)
                    newrule.seqs.append(newseq)

            generated.append(newrule.name)
            rules.append(newrule)

    # step 2: generate indexed rules with only terminal sequences as rhs
    for lhs in rr:
        newrule = CFG.Rule(lhs + str(symbolIndex[lhs]),[])
        for seq in g.get_rule(lhs).seqs:
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
        print recursiveRules(grammar)
        print genNonRecGrammar(grammar,n).__repr__()
