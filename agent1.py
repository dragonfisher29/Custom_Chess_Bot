import random
from extension.board_utils import list_legal_moves_for, copy_piece_move
from extension.board_rules import get_result

# Constants
SEARCH_DEPTH = 3
PIECE_VALUES = {
    'king': 1000,
    'queen': 9,
    'right': 5,
    'bishop': 3,
    'knight': 3,
    'pawn': 1
}
WIN_SCORE = 10000
MOBILITY_WEIGHT = 0.1
CENTER_BONUS = 0.5
NEAR_CENTER_BONUS = 0.2


def agent1(board, player, var):
    """Minimax agent with alpha-beta pruning."""
    legal_moves = list_legal_moves_for(board, player)
    if not legal_moves:
        return None, None

    _, best_move = minimax(board, player, SEARCH_DEPTH, float('-inf'), float('inf'), True)
    return best_move if best_move else random.choice(legal_moves)


def minimax(board, player, depth, alpha, beta, maximizing_player):
    """
    Minimax algorithm with alpha-beta pruning.

    Returns:
        tuple: (evaluation_score, best_move)
    """
    # Terminal state check
    game_result = get_result(board)
    if game_result or depth == 0:
        return evaluate_board(board, player), None

    legal_moves = list_legal_moves_for(board, board.current_player)
    if not legal_moves:
        return evaluate_board(board, player), None

    best_move = None
    best_eval = float('-inf') if maximizing_player else float('inf')

    for piece, move in legal_moves:
        eval_score = _evaluate_move(board, player, piece, move, depth, alpha, beta, maximizing_player)

        if eval_score is None:
            continue

        if maximizing_player:
            if eval_score > best_eval:
                best_eval = eval_score
                best_move = (piece, move)
            alpha = max(alpha, eval_score)
        else:
            if eval_score < best_eval:
                best_eval = eval_score
                best_move = (piece, move)
            beta = min(beta, eval_score)

        # Alpha-beta pruning
        if beta <= alpha:
            break

    return best_eval, best_move


def _evaluate_move(board, player, piece, move, depth, alpha, beta, maximizing_player):
    """Helper function to evaluate a single move."""
    try:
        temp_board = board.clone()
        temp_board, temp_piece, temp_move = copy_piece_move(temp_board, piece, move)

        if not temp_piece or not temp_move:
            return None

        temp_piece.move(temp_move)
        eval_score, _ = minimax(temp_board, player, depth - 1, alpha, beta, not maximizing_player)
        return eval_score
    except:
        return None


def evaluate_board(board, player):
    """Evaluate board position from player's perspective."""
    # Terminal states
    game_result = get_result(board)
    if game_result:
        return _evaluate_terminal_state(game_result, player)

    # Material and positional evaluation
    material_balance = _calculate_material_balance(board, player)
    positional_score = _evaluate_position(board, player)

    return material_balance + positional_score


def _evaluate_terminal_state(game_result, player):
    """Evaluate terminal game states."""
    result_lower = game_result.lower()

    if "checkmate" in result_lower:
        if player.name in result_lower and "loses" in result_lower:
            return -WIN_SCORE
        else:
            return WIN_SCORE
    elif "draw" in result_lower or "stalemate" in result_lower:
        return 0

    return 0


def _calculate_material_balance(board, player):
    """Calculate material advantage."""
    our_score = _calculate_material_score(board, player)
    opponent_score = _calculate_material_score(board, _get_opponent(board, player))
    return our_score - opponent_score


def _calculate_material_score(board, player):
    """Calculate total material value for a player."""
    total_score = 0
    try:
        for piece in board.get_player_pieces(player):
            piece_name = _get_piece_name(piece).lower()
            if piece_name.startswith('pawn'):
                piece_name = 'pawn'
            total_score += PIECE_VALUES.get(piece_name, 0)
    except:
        pass
    return total_score


def _evaluate_position(board, player):
    """Evaluate positional factors."""
    score = 0
    try:
        for piece in board.get_player_pieces(player):
            # Mobility bonus
            try:
                moves = piece.get_move_options()
                score += len(moves) * MOBILITY_WEIGHT
            except:
                pass

            # Center control bonus
            pos = piece.position
            if pos.x == 2 and pos.y == 2:
                score += CENTER_BONUS
            elif abs(pos.x - 2) <= 1 and abs(pos.y - 2) <= 1:
                score += NEAR_CENTER_BONUS
    except:
        pass
    return score


def _get_piece_name(piece):
    """Safely extract piece name."""
    try:
        if hasattr(piece, 'name'):
            name = piece.name
            if isinstance(name, property):
                return name.fget(piece.__class__)
            elif callable(name):
                return name()
            else:
                return str(name)
        return "unknown"
    except:
        return "unknown"


def _get_opponent(board, player):
    """Get the opponent player."""
    for p in board.players:
        if p != player:
            return p
    return None

# TODO : add endgame tactics
#  1. King and Queen vs King
#  2. King and Rook(Right) vs King
#  3. King and Knight & Bishop vs King