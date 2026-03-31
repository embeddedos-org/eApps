package com.eos.eappsuite.core.common.utils

object ExpressionParser {
    fun evaluate(expression: String): Double {
        val tokens = tokenize(expression.trim())
        val result = parseExpression(tokens.iterator() as MutableIterator<Token>)
        return result
    }

    private sealed class Token {
        data class Number(val value: Double) : Token()
        data class Op(val op: Char) : Token()
        data class Func(val name: String) : Token()
        data object LParen : Token()
        data object RParen : Token()
    }

    private fun tokenize(expr: String): List<Token> {
        val tokens = mutableListOf<Token>()
        var i = 0
        while (i < expr.length) {
            val c = expr[i]
            when {
                c.isWhitespace() -> i++
                c.isDigit() || c == '.' -> {
                    val start = i
                    while (i < expr.length && (expr[i].isDigit() || expr[i] == '.')) i++
                    tokens.add(Token.Number(expr.substring(start, i).toDouble()))
                }
                c.isLetter() -> {
                    val start = i
                    while (i < expr.length && expr[i].isLetterOrDigit()) i++
                    val name = expr.substring(start, i).lowercase()
                    when (name) {
                        "pi" -> tokens.add(Token.Number(kotlin.math.PI))
                        "e" -> tokens.add(Token.Number(kotlin.math.E))
                        else -> tokens.add(Token.Func(name))
                    }
                }
                c == '(' -> { tokens.add(Token.LParen); i++ }
                c == ')' -> { tokens.add(Token.RParen); i++ }
                c in "+-*/%^" -> { tokens.add(Token.Op(c)); i++ }
                else -> i++
            }
        }
        return tokens
    }

    private fun parseExpression(tokens: MutableIterator<Token>): Double {
        var left = parseTerm(tokens)
        while (tokens.hasNext()) {
            val next = tokens.next()
            when (next) {
                is Token.Op -> when (next.op) {
                    '+' -> left += parseTerm(tokens)
                    '-' -> left -= parseTerm(tokens)
                    else -> break
                }
                else -> break
            }
        }
        return left
    }

    private fun parseTerm(tokens: MutableIterator<Token>): Double {
        var left = parseFactor(tokens)
        while (tokens.hasNext()) {
            val next = tokens.next()
            when (next) {
                is Token.Op -> when (next.op) {
                    '*' -> left *= parseFactor(tokens)
                    '/' -> { val d = parseFactor(tokens); left = if (d != 0.0) left / d else Double.NaN }
                    '%' -> left %= parseFactor(tokens)
                    '^' -> left = kotlin.math.pow(left, parseFactor(tokens))
                    else -> break
                }
                else -> break
            }
        }
        return left
    }

    private fun parseFactor(tokens: MutableIterator<Token>): Double {
        if (!tokens.hasNext()) return 0.0
        return when (val token = tokens.next()) {
            is Token.Number -> token.value
            is Token.Op -> if (token.op == '-') -parseFactor(tokens) else parseFactor(tokens)
            is Token.LParen -> {
                val v = parseExpression(tokens)
                v
            }
            is Token.Func -> {
                val arg = parseFactor(tokens)
                applyFunction(token.name, arg)
            }
            else -> 0.0
        }
    }

    private fun applyFunction(name: String, arg: Double): Double = when (name) {
        "sin" -> kotlin.math.sin(arg)
        "cos" -> kotlin.math.cos(arg)
        "tan" -> kotlin.math.tan(arg)
        "asin" -> kotlin.math.asin(arg)
        "acos" -> kotlin.math.acos(arg)
        "atan" -> kotlin.math.atan(arg)
        "sqrt" -> kotlin.math.sqrt(arg)
        "log" -> kotlin.math.ln(arg)
        "log10" -> kotlin.math.log10(arg)
        "log2" -> kotlin.math.log2(arg)
        "abs" -> kotlin.math.abs(arg)
        "ceil" -> kotlin.math.ceil(arg)
        "floor" -> kotlin.math.floor(arg)
        "round" -> kotlin.math.round(arg).toDouble()
        "exp" -> kotlin.math.exp(arg)
        else -> arg
    }
}
