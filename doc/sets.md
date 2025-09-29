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

|                        | follow                                                                                                    |
| ---------------------- | --------------------------------------------------------------------------------------------------------- |
| PROGRAM                | $                                                                                                         |
| DEFINITION-LIST        | $                                                                                                         |
| DEFINITION             | "function", $                                                                                             |
| PARAMETER-LIST         | ")"                                                                                                       |
| FORMAL-PARAMETERS      | ")"                                                                                                       |
| FORMAL-PARAMETERS-REST | ")"                                                                                                       |
| ID-WITH-TYPE           | ",", ")"                                                                                                  |
| TYPE                   | INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", <IDENTIFIER>, "if", "(", follow(id-with-type)               |
| BODY                   | "function", $, follow(body)                                                                               |
| PRINT-EXPRESSION       | INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", <IDENTIFIER>, "if", "("                                     |
| EXPRESSION             | follow(body), ")", follow(expression-rest), "then", "else", follow(factor), ",", follow(formal-arguments) |
| EXPRESSION-REST        | follow(expression)                                                                                        |
| SIMPLE-EXPRESSION      | "=", "<", follow(expression), follow(simple-expresion-rest)                                               |
| SIMPLE-EXPRESSION-REST | follow(simple-expression)                                                                                 |
| TERM                   | "or", "+", "-", follow(simple-expression)                                                                 |
| TERM-REST              | follow(term)                                                                                              |
| FACTOR                 | "\*", "/", "and", follow(term), follow(term-rest), follow(factor)                                         |
| FACTOR-REST            | follow(factor)                                                                                            |
| ARGUMENT-LIST          | ")"                                                                                                       |
| FORMAL-ARGUMENTS       | follow(argument-list), follow(formal-arguments-rest)                                                      |
| FORMAL-ARGUMENTS-REST  | follow(formal-arguments)                                                                                  |
| LITERAL                | follow(factor)                                                                                            |
