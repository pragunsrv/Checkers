# Checkers Game

This is a command-line implementation of the classic game of Checkers (Draughts). It supports playing against a basic AI and includes features like move undo and game over detection.

## Features

- **Play Against AI**: Challenge a simple AI that makes decisions based on board evaluation.
- **Undo Moves**: Undo your last move if you change your mind or make a mistake.
- **Game Over Detection**: The game detects when a player has won or if no moves are left.

## How to Run

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/pragunsrv/checkers-game.git
   cd checkers-game
   ```

2. **Run the Game**:
   ```sh
   python checkers_game.py
   ```

3. **Gameplay Instructions**:
   - **Move Pieces**: Enter your move in the format `start_row start_col end_row end_col` (e.g., `2 1 3 2`).
   - **Undo Move**: Type `undo` to revert the last move.
   - **AI Moves**: The AI makes its move automatically. It will play against you if you're the human player.

## Example

```
Enter start position (row col): 5 2
Enter end position (row col): 4 3
```

If the AI is making a move, it will display something like:

```
black's turn (AI)
```

## AI Logic

The AI evaluates board positions to determine the best move. It prioritizes capturing pieces over simple moves and selects the move with the highest evaluation score.

## Files

- `checkers_game.py`: Contains the game logic, including piece movement, AI decisions, and game management.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
