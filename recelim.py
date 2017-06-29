#!/usr/bin/python

import sys, Lexer, CFG

print sys.argv[1], sys.argv[2]

# reachable symbols dictionary (s0:[s1,s2,...,sn])
rs = {}

def nonrec(seq):
    """
    Check if sequence (rhs) do not use recursive symbols
    """
    for sym in seq:
        if isinstance(sym,CFG.Non_Term_Ref) and rs.has_key(sym.name):
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
    global rs
    rs = reachableSymbols(g)
    print "Reachablity relation:"
    print rs
    nextSymbolIndex = {}    # dictionary non-term -> last-index
    lastGenSymbolIndex = {} # last index of generated rule
    # put recursive symbols in symbolIndex dictionary
    for sym in rs.keys():
        if sym in rs[sym]:
            nextSymbolIndex[sym] = 0
            lastGenSymbolIndex[sym] = 0
    # invariant: symbolIndex[sym] == next index to generate
    print "\nRecursive rules:"
    print nextSymbolIndex
    print "\nGenerating non recursive grammar:"
    rules = []
    generated = set()
    while not unrools(nextSymbolIndex,n):
        for r in g.rules:
            if r.name in rs[r.name]:
                # the rule is recursive
                i = nextSymbolIndex[r.name]
                newrule = CFG.Rule(r.name + str(i),[])
                nextSymbolIndex[r.name] = i + 1
                for seq in r.seqs:
                    newseq = [];
                    for sym in seq:
                        if isinstance(sym,CFG.Non_Term_Ref) and sym.name in nextSymbolIndex.keys():
                            # sym is recursive: generate indexed symbol
                            j = nextSymbolIndex[sym.name]
                            lastGenSymbolIndex[sym.name] = j
                            newseq.append(CFG.Non_Term_Ref(sym.name + str(j)))
                        else:
                            # sym is not recursive: generate original symbol
                            newseq.append(sym)
                    newrule.seqs.append(newseq)
            else:
                if r.name in generated:
                    continue
                newrule = CFG.Rule(r.name,[])
                for seq in r.seqs:
                    newseq = []
                    for sym in seq:
                        if isinstance(sym,CFG.Non_Term_Ref) and sym.name in rs.keys():
                            name = sym.name + "0"
                            newseq.append(CFG.Non_Term_Ref(name))
                        else:
                            newseq.append(sym)
                    newrule.seqs.append(newseq)

            generated.add(newrule.name)
            rules.append(newrule)

    # step 2: generate indexed rules with only terminal sequences as rhs

    # step 2.1: Generate only s : rhs width rhs containing only non-rec symbols
    for name in lastGenSymbolIndex.keys():
        if lastGenSymbolIndex[name] == nextSymbolIndex[name]:
            r = g.get_rule(name)
            newrule = CFG.Rule(name + str(lastGenSymbolIndex[name]),[])
            nextSymbolIndex[name] = nextSymbolIndex[name] + 1
            for seq in r.seqs:
                if nonrec(seq):
                    newrule.seqs.append(seq)
                    rules.append(newrule)

    # step 2.2: Generate not yet generated rules
    for name in lastGenSymbolIndex.keys():
        if lastGenSymbolIndex[name] == nextSymbolIndex[name]:
            r = g.get_rule(name)
            newrule = CFG.Rule(name + str(lastGenSymbolIndex[name]),[])
            for seq in r.seqs:
                newseq = []
                for sym in seq:
                    if isinstance(sym,CFG.Non_Term_Ref) and sym.name in rs.keys():
                        name = sym.name + lastGenSymbolIndex[name]
                        newseq.append(CFG.Non_Term_Ref(name))
                    else:
                        newseq.append(sym)
                rules.append(newrule)
            generated.add(newrule.name)

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
