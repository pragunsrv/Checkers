import random

class Piece:
    def __init__(self, color):
        self.color = color
        self.king = False

    def make_king(self):
        self.king = True

    def __repr__(self):
        return f"{'K' if self.king else ''}{self.color[0]}"

class Board:
    def __init__(self):
        self.board = self.create_board()

    def create_board(self):
        board = []
        for row in range(8):
            board.append([None] * 8)
        
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = Piece("black")

        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = Piece("white")

        return board

    def print_board(self):
        for row in self.board:
            print(' '.join([str(piece) if piece else '.' for piece in row]))

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.board[start_row][start_col] is None:
            raise ValueError("No piece at start position")
        if self.board[end_row][end_col] is not None:
            raise ValueError("End position already occupied")
        
        piece = self.board[start_row][start_col]
        self.board[start_row][start_col] = None
        self.board[end_row][end_col] = piece

        if (piece.color == "white" and end_row == 0) or (piece.color == "black" and end_row == 7):
            piece.make_king()

    def capture_piece(self, start_row, start_col, end_row, end_col):
        middle_row = (start_row + end_row) // 2
        middle_col = (start_col + end_col) // 2
        if self.board[middle_row][middle_col] is None:
            raise ValueError("No piece to capture")
        self.board[middle_row][middle_col] = None

    def valid_move(self, start_row, start_col, end_row, end_col):
        if not (0 <= start_row < 8 and 0 <= start_col < 8 and 0 <= end_row < 8 and 0 <= end_col < 8):
            return False
        if self.board[start_row][start_col] is None:
            return False
        if self.board[end_row][end_col] is not None:
            return False
        piece = self.board[start_row][start_col]
        if piece.color == "white" and not piece.king and end_row >= start_row:
            return False
        if piece.color == "black" and not piece.king and end_row <= start_row:
            return False
        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)
        if row_diff == 1 and col_diff == 1:
            return True
        if row_diff == 2 and col_diff == 2:
            middle_row = (start_row + end_row) // 2
            middle_col = (start_col + end_col) // 2
            if self.board[middle_row][middle_col] is None or self.board[middle_row][middle_col].color == piece.color:
                return False
            return True
        return False

    def perform_move(self, start_row, start_col, end_row, end_col):
        if abs(start_row - end_row) == 2 and abs(start_col - end_col) == 2:
            self.capture_piece(start_row, start_col, end_row, end_col)
        self.move_piece(start_row, start_col, end_row, end_col)

    def get_possible_moves(self, row, col):
        piece = self.board[row][col]
        if piece is None:
            return []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        moves = []
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.valid_move(row, col, new_row, new_col):
                moves.append((new_row, new_col))
        return moves

    def get_possible_captures(self, row, col):
        piece = self.board[row][col]
        if piece is None:
            return []
        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        captures = []
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.valid_move(row, col, new_row, new_col):
                captures.append((new_row, new_col))
        return captures

    def has_moves(self, color):
        for row in range(8):
            for col in range(8):
                if self.board[row][col] and self.board[row][col].color == color:
                    if self.get_possible_moves(row, col) or self.get_possible_captures(row, col):
                        return True
        return False

    def get_winner(self):
        white_pieces = sum(1 for row in self.board for piece in row if piece and piece.color == "white")
        black_pieces = sum(1 for row in self.board for piece in row if piece and piece.color == "black")
        if white_pieces == 0:
            return "black"
        elif black_pieces == 0:
            return "white"
        elif not self.has_moves("white"):
            return "black"
        elif not self.has_moves("black"):
            return "white"
        return None

class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = "white"

    def start(self):
        while True:
            self.board.print_board()
            winner = self.board.get_winner()
            if winner:
                print(f"{winner.capitalize()} wins!")
                break

            if self.current_turn == "white":
                print(f"{self.current_turn}'s turn")
                start_row, start_col = map(int, input("Enter start position (row col): ").split())
                end_row, end_col = map(int, input("Enter end position (row col): ").split())
            else:
                print(f"{self.current_turn}'s turn (AI)")
                start_row, start_col, end_row, end_col = self.get_ai_move()

            if self.board.valid_move(start_row, start_col, end_row, end_col):
                self.board.perform_move(start_row, start_col, end_row, end_col)
                if self.board.get_possible_captures(end_row, end_col):
                    print(f"{self.current_turn} must continue capturing")
                else:
                    self.current_turn = "black" if self.current_turn == "white" else "white"
            else:
                print("Invalid move, try again")

    def get_ai_move(self):
        possible_moves = []
        for row in range(8):
            for col in range(8):
                if self.board.board[row][col] and self.board.board[row][col].color == "black":
                    moves = self.board.get_possible_moves(row, col)
                    captures = self.board.get_possible_captures(row, col)
                    if captures:
                        possible_moves.extend([(row, col, end_row, end_col) for end_row, end_col in captures])
                    else:
                        possible_moves.extend([(row, col, end_row, end_col) for end_row, end_col in moves])

        if not possible_moves:
            raise ValueError("No possible moves for AI")
        
        return random.choice(possible_moves)

if __name__ == "__main__":
    game = Game()
    game.start()
