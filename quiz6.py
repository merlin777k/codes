import pygame
import sys
import random
import ast
import time
import json
import os

pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 168, 82)
RED = (255, 70, 70)
FONT = pygame.font.SysFont(None, 28)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Syntax Quiz")

clock = pygame.time.Clock()

# --- Questions ---
questions = [
    ("Create a list with the numbers 1, 2, 3", [1, 2, 3], list),
    ("Create a tuple with the numbers 4, 5, 6", (4, 5, 6), tuple),
    ("Create a dictionary with keys 'a' and 'b' and values 1 and 2", {'a': 1, 'b': 2}, dict),
    ("Create an empty list", [], list),
    ("Create an empty dictionary", {}, dict),
    ("Create a tuple with one element: number 7", (7,), tuple),
    ("Create a list of strings: 'apple', 'banana'", ['apple', 'banana'], list),
    ("Create a dictionary with 'name': 'John', 'age': 30", {'name': 'John', 'age': 30}, dict),
    ("Create a list with nested list: [1, [2, 3]]", [1, [2, 3]], list),
    ("Create a tuple with mixed types: 1, 'a', True", (1, 'a', True), tuple),
    ("Create a dictionary with int key 1 and value 'one'", {1: 'one'}, dict),
    ("Create a list using range from 0 to 4: [0, 1, 2, 3, 4]", [0, 1, 2, 3, 4], list),
    ("Create a tuple with numbers from 10 to 12", (10, 11, 12), tuple),
    ("Create a dict with 'x': 100 and 'y': 200", {'x': 100, 'y': 200}, dict),
    ("Create a list with repeated element 5, five times", [5, 5, 5, 5, 5], list),
    ("Create a tuple with values 1 to 3 using tuple()", (1, 2, 3), tuple),
    ("Create a dictionary with boolean keys True and False", {True: 'yes', False: 'no'}, dict),
    ("Create a list containing a dictionary: [{'a': 1}]", [{'a': 1}], list),
    ("Create a tuple with another tuple inside: (1, (2, 3))", (1, (2, 3)), tuple),
    ("Create a dictionary with a tuple as key: {(1, 2): 'pair'}", {(1, 2): 'pair'}, dict),
]
random.shuffle(questions)

# --- Helper functions ---
def is_valid_syntax(user_input, expected_result, expected_type):
    try:
        value = ast.literal_eval(user_input)
        return isinstance(value, expected_type) and value == expected_result
    except:
        return False

def draw_text(surface, text, pos, color=BLACK, font=FONT):
    rendered = font.render(text, True, color)
    surface.blit(rendered, pos)

def draw_multiline(surface, text, pos, color=BLACK, font=FONT, line_spacing=5):
    lines = text.split('\n')
    y_offset = 0
    for line in lines:
        draw_text(surface, line, (pos[0], pos[1] + y_offset), color, font)
        y_offset += font.get_height() + line_spacing

def save_score_to_json(name, score, total, time_out):
    filename = "scores.json"
    data = []

    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    name_lower = name.strip().lower()
    found = False
    for record in data:
        if record["name"].strip().lower() == name_lower:
            record["score"] = score
            record["total"] = total
            record["time_out"] = time_out
            found = True
            break

    if not found:
        data.append({
            "name": name,
            "score": score,
            "total": total,
            "time_out": time_out
        })

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# --- Game state ---
input_text = ""
feedback = ""
score = 0
current_question = 0
finished = False
student_name = ""
name_entered = False
start_time = None
time_limit = 120  # seconds

# --- Main loop ---
running = True
while running:
    screen.fill(WHITE)
    now = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        if not finished and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not name_entered:
                    name_entered = True
                    start_time = time.time()
                else:
                    elapsed = time.time() - start_time
                    if elapsed >= time_limit:
                        finished = True
                        feedback = "⏱️ Time's up! Quiz ended."
                        save_score_to_json(student_name, score, len(questions), time_out=True)
                    else:
                        question, expected_answer, expected_type = questions[current_question]
                        if is_valid_syntax(input_text, expected_answer, expected_type):
                            feedback = "✅ Correct!"
                            score += 1
                        else:
                            feedback = f"❌ Incorrect! Example: {repr(expected_answer)}"
                        current_question += 1
                        input_text = ""
                        if current_question >= len(questions):
                            finished = True
                            save_score_to_json(student_name, score, len(questions), time_out=False)
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode

    if name_entered and not finished:
        elapsed = int(time.time() - start_time)
        remaining = max(0, time_limit - elapsed)
        if remaining == 0:
            feedback = "⏱️ Time's up! Quiz ended."
            finished = True
            save_score_to_json(student_name, score, len(questions), time_out=True)

    if not name_entered:
        draw_text(screen, "Enter your name and press Enter:", (50, 50))
        draw_text(screen, student_name + ("_" if pygame.time.get_ticks() // 500 % 2 == 0 else ""), (50, 90))
        input_text = student_name
        student_name = input_text
    elif finished:
        draw_text(screen, f"🎉 Quiz ended, {student_name}!", (50, 100), GREEN if score > 0 else RED)
        draw_text(screen, f"Your final score: {score}/{len(questions)}", (50, 150), BLACK)
        draw_text(screen, f"Result saved to scores.json", (50, 200), BLACK)
        if remaining == 0:
            draw_text(screen, "Time expired during the quiz.", (50, 240), RED)
    else:
        question_text = questions[current_question][0]
        draw_multiline(screen, f"Question {current_question+1}/{len(questions)}:\n{question_text}", (50, 50))
        draw_text(screen, "Your answer:", (50, 150))
        draw_text(screen, input_text + ("_" if pygame.time.get_ticks() // 500 % 2 == 0 else ""), (50, 190))
        draw_text(screen, feedback, (50, 240), GREEN if "Correct" in feedback else RED)
        draw_text(screen, f"⏱️ Time left: {remaining} seconds", (600, 20), RED if remaining <= 10 else BLACK)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
