|                        | first                                                                       |
| ---------------------- | --------------------------------------------------------------------------- |
| PROGRAM                | "function", ε                                                               |
| DEFINITION-LIST        | "function", ε                                                               |
| DEFINITION             | "function"                                                                  |
| PARAMETER-LIST         | ε, IDENTIFIER                                                               |
| FORMAL-PARAMETERS      | IDENTIFIER                                                                  |
| FORMAL-PARAMETERS-REST | "," ε                                                                       |
| ID-WITH-TYPE           | IDENTIFIER                                                                  |
| TYPE                   | "integer", "boolean"                                                        |
| BODY                   | "print" INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", IDENTIFIER, "if", "(" |
| PRINT-EXPRESSION       | "print"                                                                     |
| EXPRESSION             | INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", IDENTIFIER, "if", "("         |
| EXPRESSION-REST        | "=", "<", ε                                                                 |
| SIMPLE-EXPRESSION      | INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", IDENTIFIER, "if", "("         |
| SIMPLE-EXPRESSION-REST | "or", "+", "-", ε                                                           |
| TERM                   | INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", IDENTIFIER, "if", "("         |
| TERM-REST              | "\*", "/", "and", ε                                                         |
| FACTOR                 | INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", IDENTIFIER, "if", "("         |
| FACTOR-REST            | "(", ε                                                                      |
| ARGUMENT-LIST          | ε, INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", IDENTIFIER, "if", "("      |
| FORMAL-ARGUMENTS       | INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", IDENTIFIER, "if", "("         |
| FORMAL-ARGUMENTS-REST  | ",", ε                                                                      |
| LITERAL                | INTEGER-LITERAL, BOOLEAN-LITERAL                                            |

|                        | follow                                                                                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROGRAM                | $                                                                                                                                                            |
| DEFINITION-LIST        | $                                                                                                                                                            |
| DEFINITION             | first(DEFINITION-LIST), $                                                                                                                                    |
| PARAMETER-LIST         | ")"                                                                                                                                                          |
| FORMAL-PARAMETERS      | ")"                                                                                                                                                          |
| FORMAL-PARAMETERS-REST | ")"                                                                                                                                                          |
| ID-WITH-TYPE           | first(FORMAL-PARAMETERS-REST), ")"                                                                                                                           |
| TYPE                   | first(BODY), follow(ID-WITH-TYPE)                                                                                                                            |
| BODY                   | first(DEFINITION-LIST), $                                                                                                                                    |
| PRINT-EXPRESSION       | first(BODY)                                                                                                                                                  |
| EXPRESSION             | first(DEFINITION-LIST), $, ")", "then", "else", first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), first(FORMAL-ARGUMENTS-REST), ")" |
| EXPRESSION-REST        | first(DEFINITION-LIST), $, ")", "then", "else", first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), first(FORMAL-ARGUMENTS-REST), ")" |
| SIMPLE-EXPRESSION      | first(DEFINITION-LIST), $, ")", "then", "else", first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), first(FORMAL-ARGUMENTS-REST), ")" |
| SIMPLE-EXPRESSION-REST | first(DEFINITION-LIST), $, ")", "then", "else", first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), first(FORMAL-ARGUMENTS-REST), ")" |
| TERM                   | first(DEFINITION-LIST), $, ")", "then", "else", first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), first(FORMAL-ARGUMENTS-REST), ")" |
| TERM-REST              | first(DEFINITION-LIST), $, ")", "then", "else", first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), first(FORMAL-ARGUMENTS-REST), ")" |
| FACTOR                 | first(DEFINITION-LIST), $, ")", "then", "else", first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), first(FORMAL-ARGUMENTS-REST), ")" |
| FACTOR-REST            | first(DEFINITION-LIST), $, ")", "then", "else", first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), first(FORMAL-ARGUMENTS-REST), ")" |
| ARGUMENT-LIST          | ")"                                                                                                                                                          |
| FORMAL-ARGUMENTS       | ")"                                                                                                                                                          |
| FORMAL-ARGUMENTS-REST  | ")"                                                                                                                                                          |
| LITERAL                | first(DEFINITION-LIST), $, ")", "then", "else", first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), first(FORMAL-ARGUMENTS-REST), ")" |
