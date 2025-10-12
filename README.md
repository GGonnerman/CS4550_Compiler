# Klein to TM Compiler (WIP)

Produced by the **Compile Squad**

- Jett Nehls
- Gaston Gonnerman,
- Will Gasaway
- Matthew Costello

## Explanation of Files

#### Primary Source Code

- `src/compiler`: The home for all of the python source code
- `scanner.py`: Scans through the program and seperates each character of string of characters into tokens
- `position.py`: Custom position class to track the location in the program
- `token.py`: Custom token class with a number of TokenTypes
- `token_lister.py`: Takes in a program and prints its token in an easily readable format
- `klein_errors.py`: Custom errors classes related to different stages of compiling
- `__init__.py`: These files are empty, but are required through to let python know that the current folder is a module.
- `__main__.py`: This file provides some scripts which are accessible to the user after installation
- `requirements.txt`: a list of all 3d party dependencies which get automatically installed when running make setup
- `parser.py`: Parses a program via a passed scanner and optionally the file name of the parse table to use
- `parse_table.py`: Parses a file into a usable parse table
- `validator.py`: Takes in the name of a file and prints whether it is a valid klein program or what issues arose when parsing
- `parse-table.csv`: A parse table made by hand in [Google Sheets](https://docs.google.com/spreadsheets/d/1-ugst1Gmi6EBQGiQIIBZfSfw-93SWWUm1b03G6lsCB4/edit?usp=sharing). Each value corresponds to an enum (either TokenType or NonTerminal).

#### Documentation Files

- `doc/finite-state-machines/*.jff`; Finite state machine files (which can be opened in JFLAP)
- `doc/klein-specification.txt`: Categorization of klein features with regular expressions and link to FSM files. Additionally contains a few notes on implementation
- `doc/refactored-grammer.txt`: The klein grammar with specific refactoring to make generating first/follow sets easier. All changes are described with comments
- `doc/first-and-follow-sets.md`: A listing of all first and follow sets displayed in seperate markdown tables
- `doc/ast-nodes.txt`: A listing of all ast nodes created for the klein language

#### Project Files

- `.gitignore`: ignores specific files/folders which should not be stored in version control
- `LICENSE`: the project is tenatively licensed under the MIT license
- `pyproject.toml`: Specific configuration to support building the project and exporting specific app scripts
- `Makefile`: easily provides functionality to users related to installing and running the compiler
- `kleins`: a bash script to allow scanning any klein program
- `kleinf`: a bash script to allow validating any klein program
- `CS4550_Compiler.code-workspace` and `.vscode`: We all use vscode, so these files help our configurations to stay in sync.
- `.ruff.toml`: configurations for ruff (python linter and formatter) to help standardize code
- `programs/`: a variety of programs (some functional and some intentionally non-functional) written in the klein language

#### Test Files

- `tests/test_scanner.py`: contains a large number of tests to help validate and ensure functionality of the klein scanner
- `tests/test_position.py`: contains a few tests for the position tracker
- `tests/test_parser.py`: contains a number of tests for the parser
- `tests/programs/`: contains professor provided klein programs (used in testing)

## Known Bugs

### Scanner:

- If you do an identifier or integer over 1000 characters long it will crash (due to recursion depth)

## Getting Started

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
- Thats it! Now your path depends on what you want to do

#### Running kleins/kleinf on a klein source code file

- The following instructions are applicable to any of the kleins/kleinf programs. For simplicity, I will refer to that as the `kleins` file for this instruction set which can simply be substitued for your chosen bash file.
- Ensure that the `kleins` file in the project root is executable
  - If not, running `chmod +x kleins` should make it
- From the root, you can now run `./kleins path/to/source.kln`

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
    - Now you can run the token lister against programs like `python src/compiler/token_lister.py $'hello, world\n123'` and see the tokens used!
    - You can run any file, not just the token_lister - however, that file has the most interesting behavior.

#### Running the program validator

- Activate the virtual environment
  - This can be done by (from the root) running `source ./.venv/bin/activate`
- Two options:
  - 1 As a script:
    - You can now run `klein_parse_program $'function hi(): integer 1'` and see if the program is valid
  - 2 As a file:
    - Now you can run the program validator against programs like `python src/compiler/token_lister.py $'function hi(): integer 1'` and see if it is valid!

#### Running Tests

##### Running All Tests

- From the root, run `make test_all`

##### Running a Specific Subset of Tests

- Activate the virtual enviornment
  - This can be done by (from the root) running `source ./.venv/bin/activate`
- From the root, execute `pytest tests/<chosen test suite>.py`
  - For example, to only run the tests for the scanner you could execute `pytest tests/test_scanner.py`
