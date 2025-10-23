import random
import time
import os
import csv

SCORES_FILE = "scores.csv"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def load_words():
    try:
        with open("words_alpha.txt") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: words_alpha.txt not found in the same folder as this program.")
        return []

    # Liklihood of letters used to generate board
def generate_board():
    letters = [
        ('E', 8), ('T', 8), ('A', 7), ('O', 7), ('I', 7), ('N', 6.75),
        ('S', 6.33), ('H', 6.09), ('R', 6), ('D', 4.25), ('L', 4.03), ('C', 2.78),
        ('U', 2.76), ('M', 2.41), ('W', 2.36), ('F', 2.23), ('G', 3), ('Y', 2),
        ('P', 2), ('B', 2), ('V', 2), ('K', 2), ('J', 1), ('X', 0.5),
        ('Q', 0.5), ('Z', 0.5)
    ]
    all_letters = [l for l, freq in letters for _ in range(int(freq * 10))]
    board = []
    letter_counts = {}

    while True:
        board = []
        letter_counts = {}
        for _ in range(4):
            row = []
            for _ in range(4):
                tries = 0
                while True:
                    letter = random.choice(all_letters)
                    if letter_counts.get(letter, 0) < 3:
                        row.append(letter)
                        letter_counts[letter] = letter_counts.get(letter, 0) + 1
                        break
                    tries += 1
                    # Failsafe: if stuck, reset and try again
                    if tries > 100:
                        break
                else:
                    continue
            board.append(row)
        # Check if all rows are filled (no failsafe triggered)
        if all(len(row) == 4 for row in board):
            return board
        
def display_board(board):
    for row in board:
        print(" ".join(row))

def is_adjacent_word(word, board):
    rows, cols = len(board), len(board[0])

    def dfs(r, c, index, visited):
        if index == len(word):
            return True
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1), (1, 0), (1, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols and
                (nr, nc) not in visited and
                board[nr][nc].lower() == word[index]):
                if dfs(nr, nc, index + 1, visited | {(nr, nc)}):
                    return True
        return False

    for r in range(rows):
        for c in range(cols):
            if board[r][c].lower() == word[0]:
                if dfs(r, c, 1, {(r, c)}):
                    return True
    return False

def calculate_score(word):
    length = len(word)
    if length < 3:
        return 0
    if length == 3:
        return 100
    if length == 4:
        return 400
    if length == 5:
        return 800
    if length == 6:
        return 1400
    # For words longer than 6 letters
    return 3200 + (length - 6) * 400

def save_score(score, words_found):
    file_exists = os.path.isfile(SCORES_FILE)
    with open(SCORES_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["score", "words_found", "time"])
        writer.writerow([score, len(words_found), int(time.time())])

def show_stats():
    if not os.path.isfile(SCORES_FILE):
        return
    scores = []
    with open(SCORES_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scores.append(int(row["score"]))
    if scores:
        print("\n📊 Player Stats:")
        print(f"Games Played: {len(scores)}")
        print(f"Highest Score: {max(scores)}")
        print(f"Average Score: {sum(scores)//len(scores)}")



def find_possible_words(board, words_list):
    found = set()
    for word in words_list:
        if 3 <= len(word) <= 9 and is_adjacent_word(word, board):
            found.add(word)
    return found

def main():
    words_list = load_words()
    if not words_list:
        return

    board = generate_board()
    found_words = set()
    total_score = 0
    invalid_guesses = 0

    start_time = time.time()
    time_limit = 90

    while True:
        clear_screen()
        time_left = int(time_limit - (time.time() - start_time))
        if time_left <= 0:
            break

        print("Your Word Hunt board:")
        display_board(board)
        print(f"\n⏱ Time left: {time_left} seconds")
        print(f"Score: {total_score}")
        print(f"Words found: {len(found_words)}")
        if found_words:
            print(", ".join(sorted(found_words)))
        print("\nType a word (or 'new' for a new board):")

        guess = input("> ").lower().strip()

        if guess == "new":
            board = generate_board()
            found_words.clear()
            total_score = 0
            start_time = time.time()
            continue

        if guess == "end game":
            # Sets time_left to 0 to end the game
            time_left = 0
            break

        if guess in words_list and guess not in found_words and len(guess) >= 3:
            if is_adjacent_word(guess, board):
                score = calculate_score(guess)
                found_words.add(guess)
                total_score += score
                print(f"✅ {guess} (+{score} points)")
            else:
                invalid_guesses += 1
                print("❌ Word not adjacent on board")
        elif guess in found_words:
            print("❌ Already found")
        else:
            invalid_guesses += 1
            print("❌ Not a valid word")
        time.sleep(1)

    clear_screen()
    print("⏰ Time's up!")
    display_board(board)
    print(f"\nYou found {len(found_words)} words for {total_score} points:")
    print(", ".join(sorted(found_words)) if found_words else "No words 😢")

    # Save score + show stats
    save_score(total_score, found_words)
    show_stats()

    # Show top 5 longest words
    if found_words:
        top_words = sorted(found_words, key=lambda w: (-len(w), w))[:5]
        print(f"\n🏆 Top words you found: {', '.join(top_words)}")
    print(f"Invalid guesses: {invalid_guesses}")

    # Show top possible words on this board (limit to 9 letters or less)
    possible_words = find_possible_words(board, words_list)
    possible_words -= found_words
    top_possible = sorted(
        possible_words,
        key=lambda w: (-calculate_score(w), -len(w), w)
    )[:12]
    if top_possible:
        print("\n💡Best words you could have found:")
        for w in top_possible:
            print(f"  {w} ({calculate_score(w)} points)")
    else:
        print("\n(No additional possible words found!)")

if __name__ == "__main__":
    main()
