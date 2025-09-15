from enum import IntEnum, auto


class TokenType(IntEnum):
    TERMINATOR = auto()
    PUNCTUATION = auto()
    OPERATOR = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    KEYWORD = auto()
    BOOLEAN = auto()
    PRIMITIVE_IDENTIFIER = auto()


class Token:
    def __init__(self, token_type: TokenType, token_value: int | None = None):
        self.token_type: TokenType = token_type
        self.token_value: int | None = token_value

    def isTerminator(self):
        return self.token_type == TokenType.terminator

    def isInteger(self):
        return self.token_type == TokenType.int_token

    def isIdentifier(self):
        return self.token_type == TokenType.identifier

    def isKeyword(self):
        return self.token_type == TokenType.keyword

    def isBoolean(self):
        return self.token_type == TokenType.boolean

    def isPrimitiveIdentifier(self):
        return self.token_type == TokenType.primitive_identifier

    def isPunctuation(self):
        return self.token_type == TokenType.punctuation

    def isOperator(self):
        return self.token_type == TokenType.operator

    def isEOF(self):
        return self.token_type == TokenType.eof

    def value(self):
        return self.token_value

    def __repr__(self):
        if self.isTerminator():
            return 'terminator'
        elif self.isInteger():
            return f'integer = {self.token_value}'
        elif self.isIdentifier():
            return f'identifier = {self.token_value}'
        elif self.isKeyword():
            return f'keyword = {self.token_value}'
        elif self.isBoolean():
            return f'boolean = {self.token_value}'
        elif self.isPrimitiveIdentifier():
            return f'primitive = {self.token_value}'
        elif self.isPunctuation():
            return f'punctuation = {self.token_value}'
        elif self.isOperator():
            return f'operator = {self.token_value}'
        else:  
            return 'EOF'

