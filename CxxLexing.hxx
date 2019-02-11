#include <vector>

#define T_CHARACTER_LITERAL 256
#define T_STRING_LITERAL 257
#define T_ASM 258
#define T_AUTO 259
#define T_BOOL 260
#define T_BREAK 261
#define T_CASE 262
#define T_CATCH 263
#define T_CHAR 264
#define T_CLASS 265
#define T_CONST 266
#define T_CONST_CAST 267
#define T_CONTINUE 268
#define T_DEFAULT 269
#define T_DELETE 270
#define T_DO 271
#define T_DOUBLE 272
#define T_DYNAMIC_CAST 273
#define T_ELSE 274
#define T_ENUM 275
#define T_EXPLICIT 276
#define T_EXPORT 277
#define T_EXTERN 278
#define T_FALSE 279
#define T_FLOAT 280
#define T_FOR 281
#define T_FRIEND 282
#define T_GOTO 283
#define T_IF 284
#define T_INLINE 285
#define T_INT 286
#define T_LONG 287
#define T_MUTABLE 288
#define T_NAMESPACE 289
#define T_NEW 290
#define T_OPERATOR 291
#define T_PRIVATE 292
#define T_PROTECTED 293
#define T_PUBLIC 294
#define T_REGISTER 295
#define T_REINTERPRET_CAST 296
#define T_RETURN 297
#define T_SHORT 298
#define T_SIGNED 299
#define T_SIZEOF 300
#define T_STATIC 301
#define T_STATIC_CAST 302
#define T_STRUCT 303
#define T_SWITCH 304
#define T_TEMPLATE 305
#define T_THIS 306
#define T_THROW 307
#define T_TRUE 308
#define T_TRY 309
#define T_TYPEDEF 310
#define T_TYPEID 311
#define T_TYPENAME 312
#define T_UNION 313
#define T_UNSIGNED 314
#define T_USING 315
#define T_VIRTUAL 316
#define T_VOID 317
#define T_VOLATILE 318
#define T_WCHAR_T 319
#define T_WHILE 320
#define T_SCOPE 321
#define T_ELLIPSIS 322
#define T_SHL 323
#define T_SHR 324
#define T_EQ 325
#define T_NE 326
#define T_LE 327
#define T_GE 328
#define T_LOG_AND 329
#define T_LOG_OR 330
#define T_INC 331
#define T_DEC 332
#define T_ARROW_STAR 333
#define T_ARROW 334
#define T_DOT_STAR 335
#define T_ASS_ADD 336
#define T_ASS_SUB 337
#define T_ASS_MUL 338
#define T_ASS_DIV 339
#define T_ASS_MOD 340
#define T_ASS_XOR 341
#define T_ASS_AND 342
#define T_ASS_OR 343
#define T_ASS_SHR 344
#define T_ASS_SHL 345
#define T_NUMBER 346
#define T_ID 347
#define T_ESCAPED 348

int yylval;

std::vector<char*> symbols;

int addSymbol(const char* text, int length);
int findSymbol(const char* text);
void cleanSymbols();