import random
import copy
import pickle
import json

class Piece:
    def __init__(self, color):
        self.color = color
        self.king = False

    def make_king(self):
        self.king = True

    def __repr__(self):
        return f"{'K' if self.king else ''}{self.color[0]}"

class Board:
    def __init__(self, size=8, colors=("white", "black")):
        self.size = size
        self.colors = colors
        self.board = self.create_board()

    def create_board(self):
        board = [[None] * self.size for _ in range(self.size)]
        for row in range(self.size // 2 - 1):
            for col in range(self.size):
                if (row + col) % 2 == 1:
                    board[row][col] = Piece(self.colors[1])

        for row in range(self.size // 2 + 1, self.size):
            for col in range(self.size):
                if (row + col) % 2 == 1:
                    board[row][col] = Piece(self.colors[0])

        return board

    def print_board(self):
        print("  " + " ".join(str(i) for i in range(self.size)))
        for i, row in enumerate(self.board):
            print(i, " ".join([str(piece) if piece else '.' for piece in row]))
        print()

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.board[start_row][start_col] is None:
            raise ValueError("No piece at start position")
        if self.board[end_row][end_col] is not None:
            raise ValueError("End position already occupied")
        
        piece = self.board[start_row][start_col]
        self.board[start_row][start_col] = None
        self.board[end_row][end_col] = piece

        if (piece.color == self.colors[0] and end_row == 0) or (piece.color == self.colors[1] and end_row == self.size - 1):
            piece.make_king()

    def capture_piece(self, start_row, start_col, end_row, end_col):
        middle_row = (start_row + end_row) // 2
        middle_col = (start_col + end_col) // 2
        if self.board[middle_row][middle_col] is None:
            raise ValueError("No piece to capture")
        self.board[middle_row][middle_col] = None

    def valid_move(self, start_row, start_col, end_row, end_col):
        if not (0 <= start_row < self.size and 0 <= start_col < self.size and 0 <= end_row < self.size and 0 <= end_col < self.size):
            return False
        if self.board[start_row][start_col] is None:
            return False
        if self.board[end_row][end_col] is not None:
            return False
        piece = self.board[start_row][start_col]
        if piece.color == self.colors[0] and not piece.king and end_row >= start_row:
            return False
        if piece.color == self.colors[1] and not piece.king and end_row <= start_row:
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
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] and self.board[row][col].color == color:
                    if self.get_possible_moves(row, col) or self.get_possible_captures(row, col):
                        return True
        return False

    def get_winner(self):
        white_pieces = sum(1 for row in self.board for piece in row if piece and piece.color == self.colors[0])
        black_pieces = sum(1 for row in self.board for piece in row if piece and piece.color == self.colors[1])
        if white_pieces == 0:
            return self.colors[1]
        elif black_pieces == 0:
            return self.colors[0]
        elif not self.has_moves(self.colors[0]):
            return self.colors[1]
        elif not self.has_moves(self.colors[1]):
            return self.colors[0]
        return None

    def evaluate(self):
        white_pieces = sum(1 for row in self.board for piece in row if piece and piece.color == self.colors[0])
        black_pieces = sum(1 for row in self.board for piece in row if piece and piece.color == self.colors[1])
        white_kings = sum(1 for row in self.board for piece in row if piece and piece.color == self.colors[0] and piece.king)
        black_kings = sum(1 for row in self.board for piece in row if piece and piece.color == self.colors[1] and piece.king)
        return black_pieces + 2 * black_kings - (white_pieces + 2 * white_kings)

    def get_all_moves(self, color):
        moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] and self.board[row][col].color == color:
                    piece_moves = self.get_possible_moves(row, col)
                    piece_captures = self.get_possible_captures(row, col)
                    moves.extend([(row, col, end_row, end_col) for end_row, end_col in piece_moves])
                    moves.extend([(row, col, end_row, end_col) for end_row, end_col in piece_captures])
        return moves

    def minimax(self, depth, maximizing_player, alpha, beta):
        if depth == 0 or self.get_winner():
            return self.evaluate()

        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_all_moves(self.colors[1]):
                new_board = copy.deepcopy(self)
                new_board.perform_move(*move)
                eval = new_board.minimax(depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_all_moves(self.colors[0]):
                new_board = copy.deepcopy(self)
                new_board.perform_move(*move)
                eval = new_board.minimax(depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, color, difficulty=2):
        best_move = None
        best_value = float('-inf') if color == self.colors[1] else float('inf')
        depth = 4 if color == self.colors[1] else 3
        depth = depth + difficulty if color == self.colors[1] else depth - difficulty

        for move in self.get_all_moves(color):
            new_board = copy.deepcopy(self)
            new_board.perform_move(*move)
            board_value = new_board.minimax(depth, color == self.colors[1], float('-inf'), float('inf'))
            if (color == self.colors[1] and board_value > best_value) or (color == self.colors[0] and board_value < best_value):
                best_value = board_value
                best_move = move

        return best_move

class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = "white"
        self.history = []
        self.move_history = []
        self.move_count = 0
        self.difficulty = 2
        self.user_profiles = self.load_profiles()
        self.current_profile = None
        self.stats = {"white_wins": 0, "black_wins": 0, "draws": 0}
        self.multiplayer_stats = {"white": {}, "black": {}}

    def load_profiles(self):
        try:
            with open("profiles.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_profiles(self):
        with open("profiles.json", "w") as f:
            json.dump(self.user_profiles, f)

    def start(self):
        print("Welcome to Checkers!")
        while True:
            mode = input("Select mode: 1 for Single Player, 2 for Multiplayer, or 0 to Quit: ").strip()
            if mode == '0':
                print("Exiting game.")
                break
            elif mode == '1':
                self.current_profile = input("Enter your profile name: ").strip()
                if self.current_profile not in self.user_profiles:
                    self.user_profiles[self.current_profile] = {"wins": 0, "losses": 0}
                    self.save_profiles()
                self.play_single_player()
            elif mode == '2':
                self.play_multiplayer()
            else:
                print("Invalid mode. Please choose 1, 2, or 0.")

    def play_single_player(self):
        while True:
            self.board.print_board()
            winner = self.board.get_winner()
            if winner:
                print(f"{winner.capitalize()} wins!")
                self.update_profile(winner)
                self.update_stats(winner)
                break

            if self.current_turn == "white":
                print(f"{self.current_turn}'s turn")
                user_input = input("Enter start and end position (row col row col), 'undo' to undo last move, 'history' to view move history, 'replay' to replay game, 'stats' to view game statistics, 'hint' for move hint, 'save' to save game, 'load' to load game, 'difficulty' to change AI difficulty, or 'customize' to customize board: ").strip()
                if user_input.lower() == 'undo':
                    self.undo_move()
                    continue
                if user_input.lower() == 'history':
                    self.view_history()
                    continue
                if user_input.lower() == 'replay':
                    self.replay_game()
                    continue
                if user_input.lower() == 'stats':
                    self.view_stats()
                    continue
                if user_input.lower() == 'hint':
                    self.show_hint()
                    continue
                if user_input.lower() == 'save':
                    self.save_game()
                    continue
                if user_input.lower() == 'load':
                    self.load_game()
                    continue
                if user_input.lower() == 'difficulty':
                    self.change_difficulty()
                    continue
                if user_input.lower() == 'customize':
                    self.customize_board()
                    continue
                try:
                    start_row, start_col, end_row, end_col = map(int, user_input.split())
                except ValueError:
                    print("Invalid input format. Please enter four integers separated by spaces.")
                    continue
            else:
                print(f"{self.current_turn}'s turn (AI)")
                start_row, start_col, end_row, end_col = self.get_ai_move()
                print(f"AI moves: {start_row} {start_col} -> {end_row} {end_col}")

            if self.board.valid_move(start_row, start_col, end_row, end_col):
                self.save_state(start_row, start_col, end_row, end_col)
                self.board.perform_move(start_row, start_col, end_row, end_col)
                if self.board.get_possible_captures(end_row, end_col):
                    print(f"{self.current_turn} must continue capturing")
                else:
                    self.current_turn = "black" if self.current_turn == "white" else "white"
                self.move_count += 1
            else:
                print("Invalid move, try again")

    def play_multiplayer(self):
        self.current_turn = "white"
        while True:
            self.board.print_board()
            winner = self.board.get_winner()
            if winner:
                print(f"{winner.capitalize()} wins!")
                self.update_stats(winner)
                self.update_multiplayer_stats(winner)
                break

            print(f"{self.current_turn}'s turn")
            user_input = input("Enter start and end position (row col row col), 'undo' to undo last move, 'history' to view move history, 'replay' to replay game, 'stats' to view game statistics, or 'customize' to customize board: ").strip()
            if user_input.lower() == 'undo':
                self.undo_move()
                continue
            if user_input.lower() == 'history':
                self.view_history()
                continue
            if user_input.lower() == 'replay':
                self.replay_game()
                continue
            if user_input.lower() == 'stats':
                self.view_stats()
                continue
            if user_input.lower() == 'customize':
                self.customize_board()
                continue
            try:
                start_row, start_col, end_row, end_col = map(int, user_input.split())
            except ValueError:
                print("Invalid input format. Please enter four integers separated by spaces.")
                continue

            if self.board.valid_move(start_row, start_col, end_row, end_col):
                self.save_state(start_row, start_col, end_row, end_col)
                self.board.perform_move(start_row, start_col, end_row, end_col)
                if self.board.get_possible_captures(end_row, end_col):
                    print(f"{self.current_turn} must continue capturing")
                else:
                    self.current_turn = "black" if self.current_turn == "white" else "white"
                self.move_count += 1
            else:
                print("Invalid move, try again")

    def get_ai_move(self):
        best_move = self.board.get_best_move(self.current_turn, self.difficulty)
        return best_move if best_move else (0, 0, 0, 0)

    def save_state(self, start_row, start_col, end_row, end_col):
        self.move_history.append((start_row, start_col, end_row, end_col, self.board.board))
        with open("game_state.pkl", "wb") as f:
            pickle.dump((self.board.board, self.current_turn, self.move_history, self.move_count, self.difficulty), f)

    def undo_move(self):
        if not self.move_history:
            print("No moves to undo")
            return
        self.board.board, self.current_turn, self.move_history, self.move_count, self.difficulty = self.move_history.pop()
        print("Move undone")

    def view_history(self):
        for i, move in enumerate(self.move_history):
            print(f"Move {i+1}: {move}")

    def replay_game(self):
        for board_state in self.move_history:
            self.board.board = board_state[4]
            self.board.print_board()
            input("Press Enter to continue...")

    def show_hint(self):
        best_move = self.board.get_best_move(self.current_turn, self.difficulty)
        if best_move:
            print(f"Hint: Move from {best_move[0]}, {best_move[1]} to {best_move[2]}, {best_move[3]}")
        else:
            print("No hint available")

    def save_game(self):
        with open("game_save.pkl", "wb") as f:
            pickle.dump((self.board.board, self.current_turn, self.move_history, self.move_count, self.difficulty), f)
        print("Game saved")

    def load_game(self):
        try:
            with open("game_save.pkl", "rb") as f:
                self.board.board, self.current_turn, self.move_history, self.move_count, self.difficulty = pickle.load(f)
            print("Game loaded")
        except FileNotFoundError:
            print("No saved game found.")

    def change_difficulty(self):
        new_difficulty = input("Enter new difficulty level (1-5): ").strip()
        if new_difficulty.isdigit() and 1 <= int(new_difficulty) <= 5:
            self.difficulty = int(new_difficulty)
            print(f"AI difficulty set to {self.difficulty}.")
        else:
            print("Invalid difficulty level. Please enter a number between 1 and 5.")

    def customize_board(self):
        new_size = input("Enter new board size (even number between 6 and 12): ").strip()
        if new_size.isdigit() and 6 <= int(new_size) <= 12 and int(new_size) % 2 == 0:
            self.board = Board(size=int(new_size))
            print(f"Board size set to {new_size}.")
        else:
            print("Invalid board size. Please enter an even number between 6 and 12.")

    def update_profile(self, winner):
        if self.current_profile:
            if winner == "white":
                self.user_profiles[self.current_profile]["wins"] += 1
            else:
                self.user_profiles[self.current_profile]["losses"] += 1
            self.save_profiles()

    def update_stats(self, winner):
        if winner == "white":
            self.stats["white_wins"] += 1
        else:
            self.stats["black_wins"] += 1

    def update_multiplayer_stats(self, winner):
        if winner not in self.multiplayer_stats["white"]:
            self.multiplayer_stats["white"][winner] = 0
        if winner not in self.multiplayer_stats["black"]:
            self.multiplayer_stats["black"][winner] = 0
        if winner == "white":
            self.multiplayer_stats["white"][winner] += 1
        else:
            self.multiplayer_stats["black"][winner] += 1

    def view_stats(self):
        print(f"White Wins: {self.stats['white_wins']}")
        print(f"Black Wins: {self.stats['black_wins']}")
        print(f"Draws: {self.stats['draws']}")
        print("Multiplayer Stats:")
        for color, stats in self.multiplayer_stats.items():
            print(f"{color.capitalize()}:")
            for opponent, wins in stats.items():
                print(f"  {opponent}: {wins} wins")

if __name__ == "__main__":
    game = Game()
    game.start()
