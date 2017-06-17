%{
#include "yygrammar.h"
%}
%%
"P"     { return 'P'; }
"S"     { return 'S'; }
"Z"     { return 'Z'; }
"WKLJ"     { return TK_WKLJ; }
"ZT"     { return TK_ZT; }
"TCN"     { return TK_TCN; }
"WIP"     { return TK_WIP; }
"JX"     { return TK_JX; }
"AU"     { return TK_AU; }
"SM"     { return TK_SM; }
" "    { /* skip blank */ }
\n     { yypos++; /* adjust linenumber and skip newline */ }
\r     { yypos++; /* adjust linenumber and skip newline */ }
.      { yyerror("illegal token"); }
