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
        if abs(start_row - end_row) != 1 or abs(start_col - end_col) != 1:
            return False
        return True

class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = "white"

    def start(self):
        while True:
            self.board.print_board()
            print(f"{self.current_turn}'s turn")
            start_row, start_col = map(int, input("Enter start position (row col): ").split())
            end_row, end_col = map(int, input("Enter end position (row col): ").split())

            if self.board.valid_move(start_row, start_col, end_row, end_col):
                self.board.move_piece(start_row, start_col, end_row, end_col)
                self.current_turn = "black" if self.current_turn == "white" else "white"
            else:
                print("Invalid move, try again")

if __name__ == "__main__":
    game = Game()
    game.start()
