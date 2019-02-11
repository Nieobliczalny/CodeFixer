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
            cout << "{\"token\":\"" << token << "\", \"has_value\": true, \"value\": \"" << symbols[yylval] << "\"}";
        }
        else cout << "{\"token\":\"" << token << "\", \"has_value\": false}";
        addComma = true;
    }
    cout << "]" << endl;
    return 0;
}