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

|                        | follow                                                                                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| PROGRAM                | $                                                                                                                      |
| DEFINITION-LIST        | $                                                                                                                      |
| DEFINITION             | first(DEFINITION-LIST), $                                                                                              |
| PARAMETER-LIST         | ")"                                                                                                                    |
| FORMAL-PARAMETERS      | ")"                                                                                                                    |
| FORMAL-PARAMETERS-REST | ")"                                                                                                                    |
| ID-WITH-TYPE           | first(FORMAL-PARAMETERS-REST), ")"                                                                                     |
| TYPE                   | first(BODY), follow(ID-WITH-TYPE)                                                                                      |
| BODY                   | first(DEFINITION-LIST), $                                                                                              |
| PRINT-EXPRESSION       | first(BODY)                                                                                                            |
| EXPRESSION             | first(DEFINITION-LIST), $, ")", "then", "else", follow(FACTOR), first(FORMAL-ARGUMENTS-REST), follow(FORMAL-ARGUMENTS) |
| EXPRESSION-REST        | follow(EXPRESSION)                                                                                                     |
| SIMPLE-EXPRESSION      | first(EXPRERSSION-REST), follow(EXPRESSION)                                                                            |
| SIMPLE-EXPRESSION-REST | first(EXPRERSSION-REST), follow(EXPRESSION)                                                                            |
| TERM                   | first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), follow(EXPRESSION)                                            |
| TERM-REST              | first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), follow(EXPRESSION)                                            |
| FACTOR                 | first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), follow(EXPRESSION)                          |
| FACTOR-REST            | first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), follow(EXPRESSION)                          |
| ARGUMENT-LIST          | ")"                                                                                                                    |
| FORMAL-ARGUMENTS       | ")"                                                                                                                    |
| FORMAL-ARGUMENTS-REST  | ")"                                                                                                                    |
| LITERAL                | first(TERM-REST), first(SIMPLE-EXPRERSSION-REST), first(EXPRERSSION-REST), follow(EXPRESSION)                          |
