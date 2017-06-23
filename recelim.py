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

def reachableSymbols(g):
    """ Return dictionary of reachable symbols:
        { 's1': [reachable-list], 's2': [reachable-list], ...}
    """
    reachable_syms = {}
    for r in g.rules:
        reachable_syms[r.name] = []
        for s in r.seqs:
            for sym in s:
                if isinstance(sym,CFG.Non_Term_Ref) and not (sym in reachable_syms[r.name]):
                    reachable_syms[r.name].append(sym.name)
    # transitive clausure
    changes = True
    while changes:
        changes = False
        for sym in reachable_syms.keys():
            for s in reachable_syms[sym]:
                for rs in reachable_syms[s]:
                    if not (rs in reachable_syms[sym]):
                        reachable_syms[sym].append(rs)
                        changes = True
    return reachable_syms

def unrools(symbolIndex,n):
    for sym in symbolIndex.keys():
        if symbolIndex[sym] < n:
            return False
    return True

def genNonRecGrammar(g,n):
    """
    Return an non recursive grammar with n unrolls
    """
    # step 1: generate rules from 0..n-1 unrools
    rs = reachableSymbols(g)
    print "Reachablity relation:"
    print rs
    symbolIndex = {} # dictionary non-term -> last-index
    # put recursive symbols in symbolIndex dictionary
    for sym in rs.keys():
        if sym in rs[sym]:
            symbolIndex[sym] = 0
    # invariant: symbolIndex[sym] == next index to generate
    print "\nRecursive rules:"
    print symbolIndex
    print "\nGenerating non recursive grammar:"
    rules = []
    generated = []
    while not unrools(symbolIndex,n):
        for r in g.rules:
            if r.name in rs[r.name]:
                # the rule is recursive
                i = symbolIndex[r.name]
                newrule = CFG.Rule(r.name + str(i),[])
                symbolIndex[r.name] = i + 1
                for seq in r.seqs:
                    newseq = [];
                    for sym in seq:
                        if isinstance(sym,CFG.Non_Term_Ref) and sym.name in symbolIndex.keys():
                            # sym is recursive: generate indexed symbol
                            j = symbolIndex[sym.name]
                            newseq.append(CFG.Non_Term_Ref(sym.name + str(j)))
                        else:
                            # sym is not recursive: generate original symbol
                            newseq.append(sym)
                    newrule.seqs.append(newseq)
            else:
                # non recursive rule
                if r.name in generated:
                    continue
                newrule = CFG.Rule(r.name,[])
                for seq in r.seqs:
                    newseq = [];
                    for sym in seq:
                        if isinstance(sym,CFG.Non_Term_Ref) and sym.name in rs.keys():
                            name = sym.name + "0"
                            newseq.append(CFG.Non_Term_Ref(name))
                        else:
                            newseq.append(sym)
                    newrule.seqs.append(newseq)

            generated.append(newrule.name)
            rules.append(newrule)

    # step 2: generate indexed rules with only terminal sequences as rhs
    for name in symbolIndex.keys():
        newrule = CFG.Rule(name + str(symbolIndex[name]),[])
        for seq in g.get_rule(name).seqs:
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
