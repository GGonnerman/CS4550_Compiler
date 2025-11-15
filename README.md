# Klein to TM Compiler (WIP)

Produced by the **Compile Squad**

- Jett Nehls
- Gaston Gonnerman,
- Will Gasaway
- Matthew Costello

## Quickstart Guide

### Prerequisites

- These instructions assume that you are running a UNIX enviornment with the following packages/program available and installed
  - python3
    - Running `python3` **has** to execute python with version 3.11
    - If this is not the case, in `Makefile` line 2, python3 can be changed to a different alias (e.g., `python3.11` or `python`)
  - make
  - git (optional)

### Installation

- (Optional) Clone the [repository](https://github.com/GGonnerman/CS4550_Compiler) and checkout the feature/scanner branch
- Open a terminal in the root of the project
- Run `make setup`
  - This will create a virtual environment (assuming one does not already exist) using venv
  - Then, it will install all required dependencies
  - NOTE: If this fails complaining about wrong python version, you must
    1. Delete the generated .venv folder (otherwise it will remain there and cause future issues)
    2. Either modify the Makefile or change your python3 path to meet required version
    3. Retry `make setup`
- Thats it! Now your path depends on what you want to do

#### Running kleinc on a klein source code file to compile it

- Ensure that the `kleinc` file in the project root is executable
  - If not, running `chmod +x kleinc` should make it
- From the root, you can now run `./kleinc path/to/source.kln`. The `.kln` extension is optional in this command and it will still detect the file without it being there.
- kleinc defaults to creating a file name `path/to/source.tm`, that is the source file location but with the extension changed from `kln` to `tm`. However, this behavior can be customized using the `--output` or `-o` flag
  - Running `./kleinc --output custom_name path/to/source.kln` will output the compiled klein program to the specified custom file name.
    - Note: kleinc is unopinionated and will not modify the extension (or add an extension) to the custom file name. Also note that the output flag _must_ come before the klein source file name

#### Running kleins/kleinf/kleinv on a klein source code file

- The following instructions are applicable to any of the kleins/kleinf/kleinv programs. For simplicity, I will refer to that as the `kleins` file for this instruction set which can simply be substitued for your chosen bash file.
- Ensure that the `kleins` file in the project root is executable
  - If not, running `chmod +x kleins` should make it
- From the root, you can now run `./kleins path/to/source.kln`

#### Running kleinp on a klein source code file to print text or dot

- Ensure that the `kleinp` file in the project root is executable
  - If not, running `chmod +x kleinp` should make it
- From the root, you can now run `./kleinp path/to/source.kln`
- kleinp defaults to printing text, but it can be customized using the `--format` flag
  - Running `./kleinp --format text path/to/source.kln` will print the file as a 2-space indented text tree
  - Running `./kleinp --format dot path/to/source.kln` will print the file as a dot program
    - So, given proper dot installation, one can for example run `./kleinp --format dot path/to/source.kln | dot -T png -o out.png` and then view open the out.png file in an external program.

#### Need more?

- More details about running the code as well as tests can be found in the [more running instructions](#more-running-instruction) section!

## Explanation of Files

#### Primary Source Code

- `src/compiler`: The home for all of the python source code
  - `scanner.py`: Scans through the program and seperates each character of string of characters into tokens
  - `position.py`: Custom position class to track the location in the program
  - `token.py`: Custom token class with a number of TokenTypes
  - `klein_errors.py`: Custom errors classes related to different stages of compiling
  - `__init__.py`: These files are empty, but are required through to let python know that the current folder is a module.
  - `__main__.py`: This file provides some scripts which are accessible to the user after installation
  - `requirements.txt`: a list of all 3d party dependencies which get automatically installed when running make setup
  - `parser.py`: Parses a program via a passed scanner and optionally the file name of the parse table to use
  - `parse_table.py`: Parses a file into a usable parse table
  - `parse-table.csv`: A parse table made by hand in [Google Sheets](https://docs.google.com/spreadsheets/d/1-ugst1Gmi6EBQGiQIIBZfSfw-93SWWUm1b03G6lsCB4/edit?usp=sharing). Each value corresponds to an enum (either TokenType or NonTerminal).
  - `ast_nodes.py`: All ast nodes and utilities to display
  - `symbol_table.py`: The symbol table and associated symbol code
  - `semantic_analyzer.py`: Takes in a program and generates a symbol table and detects any semantic errors
  - `tm.py`: A collection of classes to easily build lines of TM code or comments
  - `code_generator.py`: Generates TM code from an AST and a symbol table
- `src/compiler/programs`: The home for all user-facing program source code
  - `token_lister.py`: Takes in a program and prints its token in an easily readable format
  - `validator.py`: Takes in a program and prints whether it is a valid klein program or what issues arose when parsing
  - `ast_lister.py`: Takes in a program and prints its ast as text
  - `ast_lister_dot.py`: Takes in a program and prints its ast as a dot program
  - `compile.py`: Takes in a program and prints its tm representation

#### Documentation Files

- `doc/finite-state-machines/*.jff`; Finite state machine files (which can be opened in JFLAP)
- `doc/klein-specification.txt`: Categorization of klein features with regular expressions and link to FSM files. Additionally contains a few notes on implementation
- `doc/refactored-grammer.txt`: The klein grammar with specific refactoring to make generating first/follow sets easier. All changes are described with comments
- `doc/first-and-follow-sets.md`: A listing of all first and follow sets displayed in seperate markdown tables
- `doc/ast-nodes.txt`: A listing of all ast nodes created for the klein language
- `doc/all-semantic-error-log.txt`: The output of running the semantic error checker against the semantic-error.kln program
- `doc/code-generator-memory-explained.md`: An explanation of how memory is allocated, used, and addressing within/across stack frames
- `doc/memory-diagrams/*`: A set of diagrams used within the code generation explanation page

#### Project Files

- `.gitignore`: ignores specific files/folders which should not be stored in version control
- `LICENSE`: the project is tenatively licensed under the MIT license
- `pyproject.toml`: Specific configuration to support building the project and exporting specific app scripts
- `Makefile`: easily provides functionality to users related to installing and running the compiler
- `kleins`: a bash script to allow scanning any klein program
- `kleinf`: a bash script to allow validating any klein program
- `kleinp`: a bash script to allow printing the ast of any klein program
- `kleinv`: a bash script to print the symbol table or any semantic errors
- `kleinc`: a bash script to allow compiling a klein program into tm code
- `CS4550_Compiler.code-workspace` and `.vscode`: We all use vscode, so these files help our configurations to stay in sync.
- `.ruff.toml`: configurations for ruff (python linter and formatter) to help standardize code

#### Programs

- `programs/`: a variety of programs (some functional and some intentionally non-functional) written in the klein language
- `programs/EveryNode.kln`: Generates every node type (No module association)
- `programs/MissingBody.kln`: Small Error: Has no definition body but has a print followed by a long comment (No module association)
- `programs/BMI.kln`: Calculates BMI (Module 1)
- `programs/CommaErr.kln`: Small Error: Has a trailing comma in parameter list (Module 2)
- `programs/If_ThenErr.kln`: Small Error: If is missing then (Module 2)
- `programs/PrintErr.kln`: Small Error: Missing return value in body (Module 2)
- `programs/PrintErr2.kln`: Small Error: Print inside of an expression (Module 2)
- `programs/TypeErr.kln`: Small Error: No type in formal parameter (Module 2)
- `programs/FractionAdd.kln`: Adds 2 fractions and prints out result (Module 3)
- `programs/semantic-errors.kln`: A program with every possible semantic error (Module 4)
- `programs/fixed-semantic-errors.kln`: The above program with all semantic errors fixed (Module 4)
- `programs/print-one.kln`: A simple program used for testing code generation (Module 5)

#### Test Files

- `tests/test_scanner.py`: contains a large number of tests to help validate and ensure functionality of the klein scanner
- `tests/test_position.py`: contains a few tests for the position tracker
- `tests/test_parser.py`: contains a number of tests for the parser
- `tests/test_semantic_analyzer.py`: contains a number of tests for the semantic analyzer
- `tests/programs/`: contains professor provided klein programs (used in testing)

## Interested in Code Generation, TM, and Memory Management?

- Documentation for these topics can be found [here](./doc/code-generator-memory-explained.md)!

## Known Bugs

### Scanner:

- If you do an identifier or integer over 1000 characters long it will crash (due to recursion depth)

### Parser:

- Under unknown conditions, the carrot can be off by one when printing source code of errors

### Code Generator:

- Passing many arguments to the tm cli program could cause incorrect internal state when returning to the main function.
- Currently only works for limited printing integer literals and returning a value from main

## More Running Instructions

- Make sure that you have checked out the [quickstart guide](#quickstart-guide) first, and come here for more detailed instructions

#### Running any python file

- Activate the virtual environment
  - This can be done by (from the root) running `source ./.venv/bin/activate`
  - Now you can run any python program simply with `python src/compiler/my_filename.py`

#### Running the token lister

- Activate the virtual environment
  - This can be done by (from the root) running `source ./.venv/bin/activate`
- Two options:
  - 1 As a script:
    - You can now run `klein_list_tokens $'hello, world\n123'` and see the tokens used!
  - 2 As a file:
    - Now you can run the token lister against programs like `python src/compiler/programs/token_lister.py $'hello, world\n123'` and see the tokens used!
    - You can run any file, not just the token_lister - however, that file has the most interesting behavior.

#### Running the program validator

- Activate the virtual environment
  - This can be done by (from the root) running `source ./.venv/bin/activate`
- Two options:
  - 1 As a script:
    - You can now run `klein_parse_program $'function hi(): integer 1'` and see if the program is valid
  - 2 As a file:
    - Now you can run the program validator against programs like `python src/compiler/programs/token_lister.py $'function hi(): integer 1'` and see if it is valid!

#### Running the ast printer

- Activate the virtual environment
  - This can be done by (from the root) running `source ./.venv/bin/activate`
- Two options:
  - 1 As a script:
    - You can now run `klein_ast_to_text $'function hi(): integer 1'` and see your programs ast as text
    - You can now run `klein_ast_to_dot $'function hi(): integer 1'` and see your programs ast as a dot program
  - 2 As a file:
    - Now you can run the ast printer like `python src/compiler/programs/ast_lister.py $'function hi(): integer 1'` and see the ast in text
    - Now you can run the ast dot printer like `python src/compiler/programs/ast_lister_dot.py $'function hi(): integer 1'` and see the ast as a dot program

#### Running the symbol table printer

- Activate the virtual environment
  - This can be done by (from the root) running `source ./.venv/bin/activate`
- Two options:
  - 1 As a script:
    - You can now run `klein_display_symbol_table $'function main(): integer 1'` and see the symbol table or any semantic errors
  - 2 As a file:
    - Now you can run the program validator against programs like `python src/compiler/programs/display_symbol_table.py $'function main(): integer 1'` and see the symbol table or any semantic errors

#### Running the compiler

- Activate the virtual environment
  - This can be done by (from the root) running `source ./.venv/bin/activate`
- Two options:
  - 1 As a script:
    - You can now run `klein_compile $'function main(): integer 1'` and see the generated tm code
  - 2 As a file:
    - Now you can run the program validator against programs like `python src/compiler/programs/compile.py $'function main(): integer 1'` and see the generated tm code

#### Running Tests

##### Running All Tests

- From the root, run `make test_all`

##### Running a Specific Subset of Tests

- Activate the virtual enviornment
  - This can be done by (from the root) running `source ./.venv/bin/activate`
- From the root, execute `pytest tests/<chosen test suite>.py`
  - For example, to only run the tests for the scanner you could execute `pytest tests/test_scanner.py`
