import random
import copy
import json
import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk

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

        self.tournament_button = tk.Button(self.info_frame, text="Tournament Mode", command=self.start_tournament)
        self.tournament_button.pack()

        self.save_button = tk.Button(self.info_frame, text="Save Game", command=self.save_game)
        self.save_button.pack()

        self.load_button = tk.Button(self.info_frame, text="Load Game", command=self.load_game)
        self.load_button.pack()

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
                self.send_message(f"{start_row} {start_col} {end_row} {end_col}")
            else:
                message = self.receive_message()
                if message:
                    start_row, start_col, end_row, end_col = map(int, message.split())
                    self.handle_remote_move(start_row, start_col, end_row, end_col)

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

    def receive_message(self):
        if self.networked_mode and self.client_socket:
            try:
                message = self.client_socket.recv(1024).decode()
                return message
            except Exception as e:
                print(f"Failed to receive message: {e}")
                return None
        return None

    def start_tournament(self):
        num_games = simpledialog.askinteger("Tournament Mode", "Enter number of games:")
        if num_games and num_games > 0:
            results = {"white_wins": 0, "black_wins": 0, "draws": 0}
            for _ in range(num_games):
                self.restart_game()
                self.play_single_player()
                winner = self.board.get_winner()
                if winner == "white":
                    results["white_wins"] += 1
                elif winner == "black":
                    results["black_wins"] += 1
                else:
                    results["draws"] += 1
            messagebox.showinfo("Tournament Results", f"White Wins: {results['white_wins']}\nBlack Wins: {results['black_wins']}\nDraws: {results['draws']}")

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

    def get_ai_move(self):
        move = self.board.get_best_move(self.current_turn, self.difficulty)
        if move:
            return move
        return random.choice(self.board.get_all_moves(self.current_turn))

    def undo_move(self):
        if self.move_history:
            last_move = self.move_history.pop()
            self.board = last_move["board"]
            self.current_turn = last_move["turn"]
            self.move_count = last_move["move_count"]
            self.update_gui()
        else:
            messagebox.showwarning("Undo", "No moves to undo!")

    def save_game(self):
        file = filedialog.asksaveasfile(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file:
            game_data = {
                "board": self.board.board,
                "current_turn": self.current_turn,
                "move_history": self.move_history,
                "move_count": self.move_count
            }
            json.dump(game_data, file)
            file.close()

    def load_game(self):
        file = filedialog.askopenfile(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file:
            game_data = json.load(file)
            self.board.board = game_data["board"]
            self.current_turn = game_data["current_turn"]
            self.move_history = game_data["move_history"]
            self.move_count = game_data["move_count"]
            file.close()
            self.update_gui()

    def replay_game(self):
        if self.move_history:
            replay_board = Board()
            for move in self.move_history:
                replay_board.board = copy.deepcopy(move["board"])
                self.update_gui()
                self.window.update()
                self.window.after(1000)  # 1-second delay between moves
        else:
            messagebox.showwarning("Replay", "No move history to replay!")

    def show_hint(self):
        move = self.board.get_best_move(self.current_turn, self.difficulty)
        if move:
            messagebox.showinfo("Hint", f"Try moving from ({move[0]}, {move[1]}) to ({move[2]}, {move[3]})")
        else:
            messagebox.showinfo("Hint", "No hints available.")

    def change_difficulty(self):
        difficulty = simpledialog.askinteger("Difficulty", "Enter difficulty level (1-3):", minvalue=1, maxvalue=3)
        if difficulty:
            self.difficulty = difficulty

    def customize_board(self):
        color1 = simpledialog.askstring("Board Customization", "Enter color for white pieces:")
        color2 = simpledialog.askstring("Board Customization", "Enter color for black pieces:")
        if color1 and color2:
            self.board.colors = (color1, color2)
            self.update_gui()

    def view_history(self):
        history_str = "\n".join(f"Move {i+1}: {move}" for i, move in enumerate(self.move_history))
        messagebox.showinfo("Move History", history_str)

    def save_state(self, start_row, start_col, end_row, end_col):
        self.move_history.append({
            "board": copy.deepcopy(self.board),
            "turn": self.current_turn,
            "move_count": self.move_count
        })

if __name__ == "__main__":
    game = Game()
    game.start()
