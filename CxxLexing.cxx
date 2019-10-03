#include <cstring>

int addSymbol(const char* text, int length)
{
    int returnValue = findSymbol(text);
    if (returnValue == -1)
    {
        char* symbol = new char[length];
        strcpy(symbol, text);
        returnValue = symbols.size();
        symbols.push_back(symbol);
    }
    return returnValue;
}

int findSymbol(const char* text)
{
    int i = 0;
    for (auto symbol : symbols)
    {
        if (strcmp(symbol, text) == 0) return i;
        i++;
    }
    return -1;
}

void cleanSymbols()
{
    for (auto symbol : symbols)
    {
        delete [] symbol;
    }
    symbols.clear();
}

char* escapeSymbol(const char* symbol)
{
    int noEscapeChars = 0;
    int symbolLength = 0;
    int i = 0, j = 0;
    while (symbol[i])
    {
        if (symbol[i] == '"' || symbol[i] == '\\')
        {
            noEscapeChars++;
        }
        symbolLength++;
        i++;
    }
    char* newSymbol = new char[symbolLength + noEscapeChars + 1];
    i = 0;
    while (symbol[i])
    {
        if (symbol[i] == '"' || symbol[i] == '\\')
        {
            newSymbol[j++] = '\\';
        }
        newSymbol[j] = symbol[i];
        j++;
        i++;
    }
    newSymbol[j] = '\0';
    return newSymbol;
}

#include <iostream>

using std::cout;
using std::endl;

int main(void)
{
    int token;
    bool addComma = false;
    cout << "[";
    while ((token = yylex()) != 0)
    {
        if (addComma)
        {
            cout << ", ";
        }
        if (token == T_CHARACTER_LITERAL || token == T_STRING_LITERAL || token == T_NUMBER || token == T_ID || token == T_ESCAPED)
        {
            char* value = escapeSymbol(symbols[yylval]);
            cout << "{\"token\":\"" << token << "\", \"has_value\": true, \"value\": \"" << value << "\"}";
            delete [] value;
        }
        else cout << "{\"token\":\"" << token << "\", \"has_value\": false}";
        addComma = true;
    }
    cout << "]" << endl;
    return 0;
}