import random
import copy
import pickle
import json
import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import requests
import cloudpickle

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
        self.move_history = []
        self.move_count = 0
        self.difficulty = 2
        self.user_profiles = self.load_profiles()
        self.current_profile = None
        self.stats = {"white_wins": 0, "black_wins": 0, "draws": 0}
        self.multiplayer_stats = {"white": {}, "black": {}}
        self.server_socket = None
        self.client_socket = None
        self.networked_mode = False

        self.window = tk.Tk()
        self.window.title("Checkers")
        self.create_widgets()

    def create_widgets(self):
        self.board_frame = tk.Frame(self.window)
        self.board_frame.grid(row=0, column=0)

        self.info_frame = tk.Frame(self.window)
        self.info_frame.grid(row=1, column=0)

        self.info_label = tk.Label(self.info_frame, text="Welcome to Checkers")
        self.info_label.pack()

        self.restart_button = tk.Button(self.info_frame, text="Restart", command=self.restart_game)
        self.restart_button.pack()

        self.quit_button = tk.Button(self.info_frame, text="Quit", command=self.window.quit)
        self.quit_button.pack()

        self.board_buttons = [[None for _ in range(self.board.size)] for _ in range(self.board.size)]
        for r in range(self.board.size):
            for c in range(self.board.size):
                button = tk.Button(self.board_frame, width=4, height=2, command=lambda row=r, col=c: self.on_square_click(row, col))
                button.grid(row=r, column=c)
                self.board_buttons[r][c] = button

        self.update_gui()

    def on_square_click(self, row, col):
        # Add functionality for handling square clicks
        pass

    def update_gui(self):
        for r in range(self.board.size):
            for c in range(self.board.size):
                piece = self.board.board[r][c]
                if piece:
                    self.board_buttons[r][c].config(text=str(piece), bg='light grey' if piece.color == "white" else 'dark grey')
                else:
                    self.board_buttons[r][c].config(text="", bg='white' if (r + c) % 2 == 0 else 'black')

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
        self.window.mainloop()

    def restart_game(self):
        self.board = Board()
        self.current_turn = "white"
        self.move_history = []
        self.move_count = 0
        self.update_gui()

    def setup_networked_mode(self):
        choice = simpledialog.askstring("Networked Mode", "Select role: 1 for Server, 2 for Client:")
        if choice == '1':
            self.start_server()
        elif choice == '2':
            self.start_client()
        else:
            messagebox.showerror("Error", "Invalid choice.")

    def start_server(self):
        self.networked_mode = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))
        self.server_socket.listen(1)
        print("Waiting for a client to connect...")
        self.client_socket, _ = self.server_socket.accept()
        print("Client connected.")
        threading.Thread(target=self.listen_for_client, daemon=True).start()

    def start_client(self):
        self.networked_mode = True
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))
        print("Connected to server.")
        threading.Thread(target=self.listen_for_server, daemon=True).start()

    def listen_for_client(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    start_row, start_col, end_row, end_col = map(int, message.split())
                    self.handle_remote_move(start_row, start_col, end_row, end_col)
                else:
                    break
            except Exception as e:
                print(f"Error: {e}")
                break

    def listen_for_server(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    start_row, start_col, end_row, end_col = map(int, message.split())
                    self.handle_remote_move(start_row, start_col, end_row, end_col)
                else:
                    break
            except Exception as e:
                print(f"Error: {e}")
                break

    def send_message(self, message):
        if self.networked_mode:
            try:
                if self.server_socket:
                    self.client_socket.sendall(message.encode())
                else:
                    self.client_socket.sendall(message.encode())
            except Exception as e:
                print(f"Failed to send message: {e}")

    def handle_remote_move(self, start_row, start_col, end_row, end_col):
        if self.board.valid_move(start_row, start_col, end_row, end_col):
            self.board.perform_move(start_row, start_col, end_row, end_col)
            self.update_gui()
            if self.board.get_winner():
                self.handle_end_game()
        else:
            messagebox.showerror("Invalid Move", "The move is not valid!")

    def play_single_player(self):
        while True:
            self.update_gui()
            winner = self.board.get_winner()
            if winner:
                messagebox.showinfo("Game Over", f"{winner.capitalize()} wins!")
                self.update_profile(winner)
                self.update_stats(winner)
                break

            if self.current_turn == "white":
                user_input = simpledialog.askstring("Your Turn", "Enter start and end position (row col row col):")
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
                if user_input.lower() == 'leaderboard':
                    self.view_leaderboard()
                    continue
                try:
                    start_row, start_col, end_row, end_col = map(int, user_input.split())
                except ValueError:
                    messagebox.showerror("Invalid Input", "Invalid input format. Please enter four integers separated by spaces.")
                    continue
            else:
                start_row, start_col, end_row, end_col = self.get_ai_move()
                messagebox.showinfo("AI Move", f"AI moves: {start_row} {start_col} -> {end_row} {end_col}")

            if self.board.valid_move(start_row, start_col, end_row, end_col):
                self.save_state(start_row, start_col, end_row, end_col)
                self.board.perform_move(start_row, start_col, end_row, end_col)
                if self.board.get_possible_captures(end_row, end_col):
                    messagebox.showinfo("Capture", f"{self.current_turn} must continue capturing")
                else:
                    self.current_turn = "black" if self.current_turn == "white" else "white"
                self.move_count += 1
            else:
                messagebox.showerror("Invalid Move", "Invalid move, try again")

    def play_multiplayer(self):
        while True:
            self.update_gui()
            winner = self.board.get_winner()
            if winner:
                messagebox.showinfo("Game Over", f"{winner.capitalize()} wins!")
                self.update_stats(winner)
                self.update_multiplayer_stats(winner)
                break

            if self.current_turn == "white":
                user_input = simpledialog.askstring("Your Turn", "Enter start and end position (row col row col):")
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
                if user_input.lower() == 'leaderboard':
                    self.view_leaderboard()
                    continue
                try:
                    start_row, start_col, end_row, end_col = map(int, user_input.split())
                except ValueError:
                    messagebox.showerror("Invalid Input", "Invalid input format. Please enter four integers separated by spaces.")
                    continue
                if self.networked_mode:
                    self.send_message(f"{start_row} {start_col} {end_row} {end_col}")
            else:
                message = self.receive_message()
                if message:
                    start_row, start_col, end_row, end_col = map(int, message.split())
                else:
                    continue

            if self.board.valid_move(start_row, start_col, end_row, end_col):
                self.save_state(start_row, start_col, end_row, end_col)
                self.board.perform_move(start_row, start_col, end_row, end_col)
                if self.board.get_possible_captures(end_row, end_col):
                    messagebox.showinfo("Capture", f"{self.current_turn} must continue capturing")
                else:
                    self.current_turn = "black" if self.current_turn == "white" else "white"
                self.move_count += 1
            else:
                messagebox.showerror("Invalid Move", "Invalid move, try again")

    def get_ai_move(self):
        return self.board.get_best_move(self.current_turn, self.difficulty)

    def save_state(self, start_row, start_col, end_row, end_col):
        self.move_history.append((start_row, start_col, end_row, end_col))
        with open("game_state.pkl", "wb") as f:
            cloudpickle.dump((self.board.board, self.current_turn, self.move_history, self.move_count, self.difficulty), f)

    def undo_move(self):
        if self.move_history:
            last_move = self.move_history.pop()
            start_row, start_col, end_row, end_col = last_move
            self.board.move_piece(end_row, end_col, start_row, start_col)
            self.current_turn = "black" if self.current_turn == "white" else "white"
            self.move_count -= 1
            self.update_gui()
        else:
            messagebox.showinfo("Undo", "No moves to undo.")

    def view_history(self):
        history_str = "\n".join([f"Move from {start_row},{start_col} to {end_row},{end_col}" for start_row, start_col, end_row, end_col in self.move_history])
        messagebox.showinfo("Move History", history_str or "No moves made yet.")

    def replay_game(self):
        self.restart_game()
        for move in self.move_history:
            start_row, start_col, end_row, end_col = move
            self.board.perform_move(start_row, start_col, end_row, end_col)
            self.update_gui()
            self.window.after(1000)  # Pause for 1 second

    def show_hint(self):
        best_move = self.board.get_best_move(self.current_turn, self.difficulty)
        if best_move:
            messagebox.showinfo("Hint", f"Hint: Move from ({best_move[0]},{best_move[1]}) to ({best_move[2]},{best_move[3]})")
        else:
            messagebox.showinfo("Hint", "No available moves or captures.")

    def save_game(self):
        with open("game_save.pkl", "wb") as f:
            cloudpickle.dump((self.board.board, self.current_turn, self.move_history, self.move_count, self.difficulty), f)
        messagebox.showinfo("Save Game", "Game saved")

    def load_game(self):
        try:
            with open("game_save.pkl", "rb") as f:
                self.board.board, self.current_turn, self.move_history, self.move_count, self.difficulty = cloudpickle.load(f)
            self.update_gui()
            messagebox.showinfo("Load Game", "Game loaded")
        except FileNotFoundError:
            messagebox.showerror("Load Game", "No saved game found")

    def change_difficulty(self):
        new_difficulty = simpledialog.askinteger("Change Difficulty", "Enter new difficulty level (1-5):")
        if new_difficulty and 1 <= new_difficulty <= 5:
            self.difficulty = new_difficulty
            messagebox.showinfo("Difficulty Change", f"Difficulty set to {self.difficulty}")
        else:
            messagebox.showerror("Difficulty Change", "Invalid difficulty level. Please enter a number between 1 and 5.")

    def customize_board(self):
        new_size = simpledialog.askinteger("Customize Board", "Enter new board size (must be an even number):")
        if new_size and new_size % 2 == 0 and new_size >= 6:
            self.board = Board(size=new_size)
            self.update_gui()
            messagebox.showinfo("Customize Board", f"Board size set to {new_size}")
        else:
            messagebox.showerror("Customize Board", "Invalid size. Please enter an even number greater than or equal to 6.")

    def update_profile(self, winner):
        if self.current_profile:
            if winner == self.current_profile:
                self.user_profiles[self.current_profile]["wins"] += 1
            else:
                self.user_profiles[self.current_profile]["losses"] += 1
            self.save_profiles()

    def update_stats(self, winner):
        if winner == "white":
            self.stats["white_wins"] += 1
        elif winner == "black":
            self.stats["black_wins"] += 1
        else:
            self.stats["draws"] += 1

    def update_multiplayer_stats(self, winner):
        if winner == "white":
            self.multiplayer_stats["white"]["white"] = self.multiplayer_stats["white"].get("white", 0) + 1
            self.multiplayer_stats["black"]["black"] = self.multiplayer_stats["black"].get("black", 0) + 1
        else:
            self.multiplayer_stats["white"]["black"] = self.multiplayer_stats["white"].get("black", 0) + 1
            self.multiplayer_stats["black"]["white"] = self.multiplayer_stats["black"].get("white", 0) + 1

    def view_stats(self):
        stats_str = (f"White Wins: {self.stats['white_wins']}\n"
                     f"Black Wins: {self.stats['black_wins']}\n"
                     f"Draws: {self.stats['draws']}\n"
                     "Multiplayer Stats:")
        for color, stats in self.multiplayer_stats.items():
            stats_str += f"\n{color.capitalize()}:"
            for opponent, wins in stats.items():
                stats_str += f"\n  {opponent}: {wins} wins"
        messagebox.showinfo("Statistics", stats_str)

    def view_leaderboard(self):
        leaderboard = requests.get("https://example.com/leaderboard").json()
        leaderboard_str = "Leaderboard:"
        for rank, player in enumerate(leaderboard, start=1):
            leaderboard_str += f"\nRank {rank}: {player['name']} - Wins: {player['wins']}"
        messagebox.showinfo("Leaderboard", leaderboard_str)

if __name__ == "__main__":
    game = Game()
    game.start()
