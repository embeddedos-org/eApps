package com.eos.eapps.apps.echess

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

enum class PieceType { KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN }
enum class PieceColor { WHITE, BLACK }

data class ChessPiece(val type: PieceType, val color: PieceColor) {
    val symbol: String get() = when (type) {
        PieceType.KING -> if (color == PieceColor.WHITE) "♔" else "♚"
        PieceType.QUEEN -> if (color == PieceColor.WHITE) "♕" else "♛"
        PieceType.ROOK -> if (color == PieceColor.WHITE) "♖" else "♜"
        PieceType.BISHOP -> if (color == PieceColor.WHITE) "♗" else "♝"
        PieceType.KNIGHT -> if (color == PieceColor.WHITE) "♘" else "♞"
        PieceType.PAWN -> if (color == PieceColor.WHITE) "♙" else "♟"
    }
}

data class Position(val row: Int, val col: Int)

class ChessBoard {
    val board = Array(8) { arrayOfNulls<ChessPiece>(8) }
    var currentTurn = PieceColor.WHITE
    var gameOver = false
    var winner: PieceColor? = null

    init { reset() }

    fun reset() {
        currentTurn = PieceColor.WHITE
        gameOver = false
        winner = null
        for (r in 0..7) for (c in 0..7) board[r][c] = null
        val backRow = arrayOf(PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN, PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK)
        for (c in 0..7) {
            board[0][c] = ChessPiece(backRow[c], PieceColor.BLACK)
            board[1][c] = ChessPiece(PieceType.PAWN, PieceColor.BLACK)
            board[6][c] = ChessPiece(PieceType.PAWN, PieceColor.WHITE)
            board[7][c] = ChessPiece(backRow[c], PieceColor.WHITE)
        }
    }

    fun getPiece(pos: Position): ChessPiece? = board[pos.row][pos.col]

    fun isValidMove(from: Position, to: Position): Boolean {
        val piece = getPiece(from) ?: return false
        if (piece.color != currentTurn) return false
        val target = getPiece(to)
        if (target != null && target.color == piece.color) return false
        val dr = to.row - from.row
        val dc = to.col - from.col
        return when (piece.type) {
            PieceType.PAWN -> {
                val dir = if (piece.color == PieceColor.WHITE) -1 else 1
                val startRow = if (piece.color == PieceColor.WHITE) 6 else 1
                when {
                    dc == 0 && dr == dir && target == null -> true
                    dc == 0 && dr == 2 * dir && from.row == startRow && target == null && getPiece(Position(from.row + dir, from.col)) == null -> true
                    kotlin.math.abs(dc) == 1 && dr == dir && target != null -> true
                    else -> false
                }
            }
            PieceType.ROOK -> (dr == 0 || dc == 0) && isPathClear(from, to)
            PieceType.BISHOP -> kotlin.math.abs(dr) == kotlin.math.abs(dc) && isPathClear(from, to)
            PieceType.QUEEN -> (dr == 0 || dc == 0 || kotlin.math.abs(dr) == kotlin.math.abs(dc)) && isPathClear(from, to)
            PieceType.KNIGHT -> (kotlin.math.abs(dr) == 2 && kotlin.math.abs(dc) == 1) || (kotlin.math.abs(dr) == 1 && kotlin.math.abs(dc) == 2)
            PieceType.KING -> kotlin.math.abs(dr) <= 1 && kotlin.math.abs(dc) <= 1
        }
    }

    private fun isPathClear(from: Position, to: Position): Boolean {
        val dr = to.row.compareTo(from.row)
        val dc = to.col.compareTo(from.col)
        var r = from.row + dr; var c = from.col + dc
        while (r != to.row || c != to.col) {
            if (board[r][c] != null) return false
            r += dr; c += dc
        }
        return true
    }

    fun makeMove(from: Position, to: Position): Boolean {
        if (!isValidMove(from, to)) return false
        val captured = board[to.row][to.col]
        board[to.row][to.col] = board[from.row][from.col]
        board[from.row][from.col] = null
        if (captured?.type == PieceType.KING) {
            gameOver = true
            winner = currentTurn
        }
        currentTurn = if (currentTurn == PieceColor.WHITE) PieceColor.BLACK else PieceColor.WHITE
        return true
    }

    fun getValidMoves(pos: Position): List<Position> {
        val moves = mutableListOf<Position>()
        for (r in 0..7) for (c in 0..7) {
            val to = Position(r, c)
            if (isValidMove(pos, to)) moves.add(to)
        }
        return moves
    }
}

@Composable
fun AppContent() {
    val game = remember { ChessBoard() }
    var selectedPos by remember { mutableStateOf<Position?>(null) }
    var validMoves by remember { mutableStateOf(emptyList<Position>()) }
    var boardVersion by remember { mutableStateOf(0) }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("♟️ eChess", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(4.dp))
        val _ = boardVersion
        Text(
            if (game.gameOver) "${game.winner?.name} wins!" else "${game.currentTurn.name}'s turn",
            style = MaterialTheme.typography.bodyLarge,
        )
        Spacer(Modifier.height(8.dp))

        Box(modifier = Modifier.aspectRatio(1f).fillMaxWidth(0.9f)) {
            LazyVerticalGrid(
                columns = GridCells.Fixed(8),
                modifier = Modifier.fillMaxSize(),
                userScrollEnabled = false,
            ) {
                items(64) { index ->
                    val row = index / 8
                    val col = index % 8
                    val pos = Position(row, col)
                    val piece = game.getPiece(pos)
                    val isLight = (row + col) % 2 == 0
                    val isSelected = selectedPos == pos
                    val isValidTarget = pos in validMoves

                    Box(
                        modifier = Modifier
                            .aspectRatio(1f)
                            .background(
                                when {
                                    isSelected -> Color(0xFF6495ED)
                                    isValidTarget -> Color(0xFF90EE90)
                                    isLight -> Color(0xFFF0D9B5)
                                    else -> Color(0xFFB58863)
                                },
                            )
                            .then(if (isSelected) Modifier.border(2.dp, Color.Blue) else Modifier)
                            .clickable {
                                if (game.gameOver) return@clickable
                                if (selectedPos != null && isValidTarget) {
                                    game.makeMove(selectedPos!!, pos)
                                    selectedPos = null
                                    validMoves = emptyList()
                                    boardVersion++
                                } else if (piece != null && piece.color == game.currentTurn) {
                                    selectedPos = pos
                                    validMoves = game.getValidMoves(pos)
                                } else {
                                    selectedPos = null
                                    validMoves = emptyList()
                                }
                            },
                        contentAlignment = Alignment.Center,
                    ) {
                        if (piece != null) {
                            Text(piece.symbol, fontSize = 28.sp, textAlign = TextAlign.Center)
                        }
                    }
                }
            }
        }

        Spacer(Modifier.height(12.dp))
        Button(onClick = { game.reset(); selectedPos = null; validMoves = emptyList(); boardVersion++ }) {
            Text("New Game")
        }
    }
}
package com.eos.eapps.apps.echess

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.eos.eapps.core.ui.canvas.GameCanvas
import com.eos.eapps.core.ui.theme.AppTheme

private enum class Screen { HOME, GAME }
private enum class PieceType { KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN }
private enum class PieceColor { WHITE, BLACK }

private data class ChessPiece(val type: PieceType, val color: PieceColor)

private data class ChessState(
    val board: List<List<ChessPiece?>> = initialBoard(),
    val selectedCell: Pair<Int, Int>? = null,
    val validMoves: List<Pair<Int, Int>> = emptyList(),
    val turn: PieceColor = PieceColor.WHITE,
    val capturedWhite: List<ChessPiece> = emptyList(),
    val capturedBlack: List<ChessPiece> = emptyList(),
    val gameOver: Boolean = false
)

private fun initialBoard(): List<List<ChessPiece?>> {
    val board = MutableList<MutableList<ChessPiece?>>(8) { MutableList(8) { null } }
    val backRow = listOf(PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
        PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK)
    for (c in 0..7) {
        board[0][c] = ChessPiece(backRow[c], PieceColor.BLACK)
        board[1][c] = ChessPiece(PieceType.PAWN, PieceColor.BLACK)
        board[6][c] = ChessPiece(PieceType.PAWN, PieceColor.WHITE)
        board[7][c] = ChessPiece(backRow[c], PieceColor.WHITE)
    }
    return board
}

private fun getValidMoves(board: List<List<ChessPiece?>>, row: Int, col: Int): List<Pair<Int, Int>> {
    val piece = board[row][col] ?: return emptyList()
    val moves = mutableListOf<Pair<Int, Int>>()

    fun addIfValid(r: Int, c: Int): Boolean {
        if (r !in 0..7 || c !in 0..7) return false
        val target = board[r][c]
        if (target == null) { moves.add(r to c); return true }
        if (target.color != piece.color) { moves.add(r to c) }
        return false
    }

    fun addLine(dr: Int, dc: Int) {
        var r = row + dr; var c = col + dc
        while (r in 0..7 && c in 0..7) {
            if (!addIfValid(r, c) || board[r][c] != null) break
            r += dr; c += dc
        }
    }

    when (piece.type) {
        PieceType.PAWN -> {
            val dir = if (piece.color == PieceColor.WHITE) -1 else 1
            val startRow = if (piece.color == PieceColor.WHITE) 6 else 1
            if (row + dir in 0..7 && board[row + dir][col] == null) {
                moves.add((row + dir) to col)
                if (row == startRow && board[row + 2 * dir][col] == null) moves.add((row + 2 * dir) to col)
            }
            for (dc in listOf(-1, 1)) {
                val nr = row + dir; val nc = col + dc
                if (nr in 0..7 && nc in 0..7 && board[nr][nc]?.color != null && board[nr][nc]?.color != piece.color)
                    moves.add(nr to nc)
            }
        }
        PieceType.KNIGHT -> {
            for ((dr, dc) in listOf(-2 to -1, -2 to 1, -1 to -2, -1 to 2, 1 to -2, 1 to 2, 2 to -1, 2 to 1))
                addIfValid(row + dr, col + dc)
        }
        PieceType.BISHOP -> { addLine(-1, -1); addLine(-1, 1); addLine(1, -1); addLine(1, 1) }
        PieceType.ROOK -> { addLine(-1, 0); addLine(1, 0); addLine(0, -1); addLine(0, 1) }
        PieceType.QUEEN -> {
            addLine(-1, -1); addLine(-1, 1); addLine(1, -1); addLine(1, 1)
            addLine(-1, 0); addLine(1, 0); addLine(0, -1); addLine(0, 1)
        }
        PieceType.KING -> {
            for (dr in -1..1) for (dc in -1..1) if (dr != 0 || dc != 0) addIfValid(row + dr, col + dc)
        }
    }
    return moves
}

@Composable
fun App() {
    AppTheme {
        var screen by remember { mutableStateOf(Screen.HOME) }
        when (screen) {
            Screen.HOME -> HomeScreen { screen = Screen.GAME }
            Screen.GAME -> GameScreen { screen = Screen.HOME }
        }
    }
}

@Composable
private fun HomeScreen(onPlay: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().background(Color(0xFF3E2723)).padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("\u265A eChess", fontSize = 48.sp, color = Color.White)
        Spacer(Modifier.height(16.dp))
        Text("Classic Chess", fontSize = 18.sp, color = Color(0xFFBCAAA4))
        Spacer(Modifier.height(32.dp))
        Button(
            onClick = onPlay,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF795548)),
            modifier = Modifier.width(200.dp).height(56.dp)
        ) { Text("Play", fontSize = 20.sp) }
    }
}

@Composable
private fun GameScreen(onBack: () -> Unit) {
    var state by remember { mutableStateOf(ChessState()) }
    var canvasW by remember { mutableStateOf(1f) }
    var canvasH by remember { mutableStateOf(1f) }

    Column(modifier = Modifier.fillMaxSize().background(Color(0xFF3E2723))) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextButton(onClick = onBack) { Text("\u2190 Back", color = Color.White) }
            Text(
                if (state.gameOver) "Game Over" else "${if (state.turn == PieceColor.WHITE) "White" else "Black"}'s Turn",
                color = Color.White, fontSize = 18.sp
            )
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("Captured: ${state.capturedBlack.size}", color = Color.White, fontSize = 12.sp)
            Text("Captured: ${state.capturedWhite.size}", color = Color.White, fontSize = 12.sp)
        }

        Box(modifier = Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
            GameCanvas(
                modifier = Modifier.fillMaxSize().padding(8.dp),
                onTap = { offset ->
                    if (state.gameOver) return@GameCanvas
                    val cellSize = minOf(canvasW, canvasH) / 8f
                    val offX = (canvasW - cellSize * 8) / 2f
                    val offY = (canvasH - cellSize * 8) / 2f
                    val col = ((offset.x - offX) / cellSize).toInt()
                    val row = ((offset.y - offY) / cellSize).toInt()
                    if (row !in 0..7 || col !in 0..7) return@GameCanvas

                    val s = state
                    if (s.selectedCell != null && (row to col) in s.validMoves) {
                        val (sr, sc) = s.selectedCell
                        val newBoard = s.board.map { it.toMutableList() }.toMutableList()
                        val movingPiece = newBoard[sr][sc]
                        val captured = newBoard[row][col]
                        newBoard[row][col] = movingPiece
                        newBoard[sr][sc] = null
                        val newTurn = if (s.turn == PieceColor.WHITE) PieceColor.BLACK else PieceColor.WHITE
                        val cw = if (captured?.color == PieceColor.WHITE) s.capturedWhite + captured else s.capturedWhite
                        val cb = if (captured?.color == PieceColor.BLACK) s.capturedBlack + captured else s.capturedBlack
                        val kingCaptured = captured?.type == PieceType.KING
                        state = s.copy(
                            board = newBoard, selectedCell = null, validMoves = emptyList(),
                            turn = newTurn, capturedWhite = cw, capturedBlack = cb, gameOver = kingCaptured
                        )
                    } else {
                        val piece = s.board[row][col]
                        if (piece != null && piece.color == s.turn) {
                            val moves = getValidMoves(s.board, row, col)
                            state = s.copy(selectedCell = row to col, validMoves = moves)
                        } else {
                            state = s.copy(selectedCell = null, validMoves = emptyList())
                        }
                    }
                },
                onDraw = {
                    canvasW = size.width; canvasH = size.height
                    val cellSize = minOf(size.width, size.height) / 8f
                    val offX = (size.width - cellSize * 8) / 2f
                    val offY = (size.height - cellSize * 8) / 2f

                    for (r in 0..7) for (c in 0..7) {
                        val light = (r + c) % 2 == 0
                        val x = offX + c * cellSize; val y = offY + r * cellSize
                        val isSelected = state.selectedCell == (r to c)
                        val isValid = (r to c) in state.validMoves
                        val color = when {
                            isSelected -> Color(0xFF66BB6A)
                            isValid -> Color(0xFFFFEB3B).copy(alpha = 0.5f)
                            light -> Color(0xFFF0D9B5)
                            else -> Color(0xFFB58863)
                        }
                        drawRect(color, Offset(x, y), Size(cellSize, cellSize))

                        if (isValid) {
                            drawCircle(Color(0x6666BB6A), cellSize * 0.15f, Offset(x + cellSize / 2, y + cellSize / 2))
                        }

                        val piece = state.board[r][c] ?: continue
                        drawPiece(piece, x, y, cellSize)
                    }
                }
            )
        }

        Button(
            onClick = { state = ChessState() },
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF795548))
        ) { Text("New Game") }
    }
}

private fun DrawScope.drawPiece(piece: ChessPiece, x: Float, y: Float, cellSize: Float) {
    val cx = x + cellSize / 2; val cy = y + cellSize / 2
    val r = cellSize * 0.35f
    val fillColor = if (piece.color == PieceColor.WHITE) Color.White else Color(0xFF333333)
    val outlineColor = if (piece.color == PieceColor.WHITE) Color(0xFF666666) else Color.White

    drawCircle(fillColor, r, Offset(cx, cy))
    drawCircle(outlineColor, r, Offset(cx, cy), style = androidx.compose.ui.graphics.drawscope.Stroke(2f))

    when (piece.type) {
        PieceType.KING -> {
            drawRect(outlineColor, Offset(cx - 2, cy - r * 0.6f), Size(4f, r * 0.5f))
            drawRect(outlineColor, Offset(cx - r * 0.25f, cy - r * 0.4f), Size(r * 0.5f, 3f))
        }
        PieceType.QUEEN -> {
            for (i in 0..2) {
                val dx = (i - 1) * r * 0.3f
                drawCircle(outlineColor, r * 0.08f, Offset(cx + dx, cy - r * 0.6f))
            }
        }
        PieceType.ROOK -> {
            drawRect(outlineColor, Offset(cx - r * 0.3f, cy - r * 0.5f), Size(r * 0.6f, r * 0.3f))
        }
        PieceType.BISHOP -> {
            drawCircle(outlineColor, r * 0.12f, Offset(cx, cy - r * 0.5f))
        }
        PieceType.KNIGHT -> {
            drawRect(outlineColor, Offset(cx - r * 0.1f, cy - r * 0.6f), Size(r * 0.3f, r * 0.6f))
        }
        PieceType.PAWN -> { /* circle only */ }
    }
}
