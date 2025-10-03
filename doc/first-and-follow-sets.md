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

|                        | follow                                                                                 |
| ---------------------- | -------------------------------------------------------------------------------------- |
| PROGRAM                | $                                                                                      |
| DEFINITION-LIST        | $                                                                                      |
| DEFINITION             | "function", $                                                                          |
| PARAMETER-LIST         | ")"                                                                                    |
| FORMAL-PARAMETERS      | ")"                                                                                    |
| FORMAL-PARAMETERS-REST | ")"                                                                                    |
| ID-WITH-TYPE           | ",", ")"                                                                               |
| TYPE                   | "print", INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", IDENTIFIER, "if", "(", ",", ")" |
| BODY                   | "function", $                                                                          |
| PRINT-EXPRESSION       | "print", INTEGER-LITERAL, BOOLEAN-LITERAL, "not", "-", IDENTIFIER, "if", "("           |
| EXPRESSION             | ")", "then", "else", ",", "function", $                                                |
| EXPRESSION-REST        | ")", "then", "else", ",", "function", $                                                |
| SIMPLE-EXPRESSION      | "=", "<", ")", "then", "else", ",", "function", $                                      |
| SIMPLE-EXPRESSION-REST | "=", "<", ")", "then", "else", ",", "function", $                                      |
| TERM                   | "or", "+", "-", "=", "<", ")", "then", "else", ",", "function", $                      |
| TERM-REST              | "or", "+", "-", "=", "<", ")", "then", "ellse", ",", "function", $                     |
| FACTOR                 | "\*", "/", "and", "or", "+", "-", "=", "<", ")", "then", "else", ",", "function", $    |
| FACTOR-REST            | "\*", "/", "and", "or", "+", "-", "=", "<", ")", "then", "else", ",", "function", $    |
| ARGUMENT-LIST          | ")"                                                                                    |
| FORMAL-ARGUMENTS       | ")"                                                                                    |
| FORMAL-ARGUMENTS-REST  | ")"                                                                                    |
| LITERAL                | "\*", "/", "and", "or", "+", "-", "=", "<", ")", "then", "else", ",", "function", $    |
