# Klein to TM Compiler

Produced by the **Compile Squad**

- Jett Nehls
- Gaston Gonnerman
- Will Gasaway
- Matthew Costello

This project contains the source code for a Klein to TM Compiler. The project is implemented in python. The project is largely split into 4 sections based on the generalized structure of a compiler: scanning, parsing, semantic analysis, and optimization/code generation. This document serves as the primary documentation with supplementary material appearing in the doc directory, which is further broken down by section.

## Table of Contents:

- [Quickstart Guide](#quickstart-guide)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Optimizations Implemented](#optimizations-implemented)
  - [Smart Register Selection](#smart-register-selection)
  - [Print Inlining](#print-inlining)
- [Known Bugs](#known-bugs)
  - [Scanner](#scanner)
  - [Parser](#parser)
  - [Code Generator](#code-generator)
- [More Running Instructions](#more-running-instructions)
- [Interested in Contributing? More Resources Below](#interested-in-contributing-more-resources-below)

## Quickstart Guide

### Prerequisites

- These instructions assume that you are running a UNIX enviornment with the following packages/program available and installed
  - python3
    - Running `python3` **has** to execute python with version 3.11
    - If this is not the case, in `Makefile` line 2, python3 can be changed to a different alias (e.g., `python3.11` or `python`)
  - make
  - git (optional)
  - graphviz (optional)

### Installation

- (Optional) Clone the [repository](https://github.com/GGonnerman/CS4550_Compiler)
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

> Important Note: It is **highly** recommended that the DMEM and IMEM address sizes within the TM virtual machine be increased from the default values (1024) to larger values (e.g., 1024000). Technically this is not required, but the number of programs that can be run without increasing these limits is relatively small.

- Ensure that the `kleinc` file in the project root is executable
  - If not, running `chmod +x kleinc` should make it
- From the root, you can now run `./kleinc path/to/source.kln`. The `.kln` extension is optional in this command and it will still detect the file without it being there.
- kleinc defaults to creating a file name `path/to/source.tm`, that is the source file location but with the extension changed from `kln` to `tm`. However, this behavior can be customized using the `--output` or `-o` flag
  - Running `./kleinc --output custom_name path/to/source.kln` will output the compiled klein program to the specified custom file name.
    - Note: kleinc is unopinionated and will not modify the extension (or add an extension) to the custom file name. Also note that the output flag _must_ come before the klein source file name

#### Running kleins/kleinf/kleinv on a klein source code file

- kleins will print all tokens within a source klein program
- kleinf will validate a source klein program
- kleinv will print the symbol table of a source klein program
- The following instructions are applicable to any of the kleins/kleinf/kleinv programs. For simplicity, I will refer to that as the `kleinX` file for this instruction set which can simply be substitued for your chosen bash file
- Ensure that the `kleinX` file in the project root is executable
  - If not, running `chmod +x kleinX` should make it
- From the root, you can now run `./kleinX path/to/source.kln`

#### Running kleinp on a klein source code file to print text or dot of the ast

- Ensure that the `kleinp` file in the project root is executable
  - If not, running `chmod +x kleinp` should make it
- From the root, you can now run `./kleinp path/to/source.kln`
- kleinp defaults to printing text, but it can be customized using the `--format` flag
  - Running `./kleinp --format text path/to/source.kln` will print the file as a 2-space indented text tree
  - Running `./kleinp --format dot path/to/source.kln` will print the file as a dot program
    - So, given proper graphviz/dot installation, one can for example run `./kleinp --format dot path/to/source.kln | dot -T png -o out.png` and then view open the out.png file in an external program.

#### Need more?

- More details about running the code as well as tests can be found in the [more running instructions](#more-running-instructions) section!

## Optimizations Implemented

### Smart Register Selection

- The compiler implements a smart register selection algorithm which utilizes next use data to determine which register is the best to "replace." This helps to minimize the number of stores and loads that our compiler makes, thus increasing speed of compiled programs.

### Print Inlining

- The compiler has a basic of inlining that specifically targets print statements. Due to their frequency and the cost of making function calls, this again helps to increase the speed of compiled programs. We _do_ still generate the source code for the print function in case it becomes necessary. However, it is unused at this time.

## Known Bugs

### Scanner

- If you do an identifier or integer over 1000 characters long it will crash (due to recursion depth)

### Parser

- Under unknown conditions, the carrot can be off by one when printing the source code of errors

### Code Generator

- When calling kleinc for a path that contains a period and relying on an implicit .kln extension, the outputted file is incorrectly named and placed in the wrong location

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

Before running tests (specifically for the compiler), ensure that you have a version of tm-cli-go compiled for your machine (ideally with increased imem and dmem). This file should be placed inside of the tests directory and named `tm_cli_go` to ensure test functionality.

##### Running All Tests

- From the root, run `make test_all`

##### Running a Specific Subset of Tests

- Activate the virtual enviornment
  - This can be done by (from the root) running `source ./.venv/bin/activate`
- From the root, execute `pytest tests/<chosen test suite>.py`
  - For example, to only run the tests for the scanner you could execute `pytest tests/test_scanner.py`

## Interested in Contributing? More Resources Below

- [Original language specifications](./doc/scanner/klein_specification.txt)
- [The Scanner's State Machines](./doc/scanner/finite_state_machines/)
- The [Refactored Grammer](./doc/parser/refactored_grammar.txt)
- [Chosen AST Nodes](./doc/parser/ast_nodes.txt)
- [First and Follow Sets](./doc/parser/first_and_follow_sets.md) and the [Parse Table](./doc/parser/parse_table.csv)
- All possible [semantic errors](./doc/semantic_checker/all_semantic_error_log.txt)
- Information about [Code Generation, TM, and Memory Management](./doc/code_generator/code_generator_memory_explained.md)
- A [Legacy/Outdated README](./doc/prerelease_README.md) still contains useful insights
