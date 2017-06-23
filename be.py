import CFG, lexer

def be(g,sym,n):
    """
    
    """
    if n == 0:
        return set()
    result = set()
    for seq in g.rule(sym.name).seqs:
        genrhs = []
        for s in seq:
            if isinstance(s,CFG.Non_Term_Ref):
                genrhs.append(be(g,s,n-1))
            if isInstance(s,CFG.Sym_Term):
                list.append(set(s.tok))
            if isInstance(s,CFG.Term):
                list.append(set(s.tok))
