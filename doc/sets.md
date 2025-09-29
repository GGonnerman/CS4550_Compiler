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

|                        | follow                                                                                   |
| ---------------------- | ---------------------------------------------------------------------------------------- |
| PROGRAM                | $                                                                                        |
| DEFINITION-LIST        | $                                                                                        |
| DEFINITION             | "function", $                                                                            |
| PARAMETER-LIST         | ")"                                                                                      |
| FORMAL-PARAMETERS      | ")"                                                                                      |
| FORMAL-PARAMETERS-REST | ")"                                                                                      |
| ID-WITH-TYPE           | ",", ")"                                                                                 |
| TYPE                   | "print", INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", IDENTIFIER, "if", "(", ",", ")"   |
| BODY                   | "function", $                                                                            |
| PRINT-EXPRESSION       | "print", INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", IDENTIFIER, "if", "("             |
| EXPRESSION             | "function", $, "then", "else", "\*", "/", "and", "or", "+", "-", "=", "<", ",", ")"      |
| EXPRESSION-REST        | "function", $, "then", "else", "\*", "/", "and", "or", "+", "-", "=", "<", ",", ")"      |
| SIMPLE-EXPRESSION      | "function", $, "then", "else", "\*", "/", "and", "or", "+", "-", "=", "<", ",", ")"      |
| SIMPLE-EXPRESSION-REST | "function", $, "then", "else", "\*", "/", "and", "or", "+", "-", "=", "<", ",", ")"      |
| TERM                   | "function", $, "then", "else", "\*", "/", "and", "or", "+", "-", "=", "<", ",", ")"      |
| TERM-REST              | "function", $, "then", "else", "\*", "/", "and", "or", "+", "-", "=", "<", ",", ")"      |
| FACTOR                 | "function", $, "then", "else", "\*", "/", "and", "or", "+", "-", "=", "<", ",", ")"      |
| FACTOR-REST            | "function", $, "then", "else", "\*", "/", "and", "or", "+", "-", "=", "<", ",", ")"      |
| ARGUMENT-LIST          | ")"                                                                                      |
| FORMAL-ARGUMENTS       | ")"                                                                                      |
| FORMAL-ARGUMENTS-REST  | ")"                                                                                      |
| LITERAL                | "function", $, ")", "then", "else", "\*", "/", "and", "or", "+", "-", "=", "<", ",", ")" |
