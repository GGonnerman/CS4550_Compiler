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

|                        | follow                                                                                                                             |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| PROGRAM                | $                                                                                                                                  |
| DEFINITION-LIST        | follow(PROGRAM)                                                                                                                    |
| DEFINITION             | first(DEFINITION-LIST), follow(DEFINITION-LIST)                                                                                    |
| PARAMETER-LIST         | ")"                                                                                                                                |
| FORMAL-PARAMETERS      | follow(PARAMETER-LIST), follow(FORMAL-PARAMETER-REST)                                                                              |
| FORMAL-PARAMETERS-REST | follow(FORMAL-PARAMETERS)                                                                                                          |
| ID-WITH-TYPE           | first(FORMAL-PARAMETERS-REST), follow(FORMAL-PARAMETERS)                                                                           |
| TYPE                   | first(BODY), follow(ID-WITH-TYPE)                                                                                                  |
| BODY                   | follow(DEFINITION)                                                                                                                 |
| PRINT-EXPRESSION       | first(BODY)                                                                                                                        |
| EXPRESSION             | follow(BODY), ")", follow(EXPRESSION-REST), "then", "else", follow(FACTOR), first(FORMAL-ARGUMENTS-REST), follow(FORMAL-ARGUMENTS) |
| EXPRESSION-REST        | follow(EXPRESSION)                                                                                                                 |
| SIMPLE-EXPRESSION      | first(EXPRERSSION-REST), follow(EXPRESSION), follow(SIMPLE-EXPRESSION-REST)                                                        |
| SIMPLE-EXPRESSION-REST | follow(SIMPLE-EXPRESSION)                                                                                                          |
| TERM                   | first(SIMPLE-EXPRERSSION-REST), follow(SIMPLE-EXPRESSION)                                                                          |
| TERM-REST              | follow(TERM)                                                                                                                       |
| FACTOR                 | first(TERM-REST), follow(TERM), follow(TERM-REST)                                                                                  |
| FACTOR-REST            | follow(FACTOR)                                                                                                                     |
| ARGUMENT-LIST          | ")"                                                                                                                                |
| FORMAL-ARGUMENTS       | follow(ARGUMENT-LIST), follow(FORMAL-ARGUMENTS-REST)                                                                               |
| FORMAL-ARGUMENTS-REST  | follow(FORMAL-ARGUMENTS)                                                                                                           |
| LITERAL                | follow(FACTOR)                                                                                                                     |
