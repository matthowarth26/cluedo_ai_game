import random

# Define class for player that moves, stores knowledge of cards, makes accusations, and updates knowledge 
class PlayerAgent:
    def __init__(self, player_id, color, start_position, starting_cards):
        self.player_id = player_id # Assign player IDs
        self.color = color # Assign associated color 
        self.row, self.col = start_position # Assign starting position on board 
        self.knowledge = set(starting_cards)  # What cards they know
        self.is_active = True  # Still in the game

    # Random dice roll will determine how many tiles the agent can move 
    def roll_dice(self):
        return random.randint(1, 6) + random.randint(1, 6)

    # Player can move up, down, left and right and cannot move off of the grid 
    def move(self, moves_left, grid_size):
        for _ in range(moves_left):
            direction = random.choice(["up", "down", "left", "right"])
            if direction == "up" and self.row > 0:
                self.row -= 1
            elif direction == "down" and self.row < grid_size - 1:
                self.row += 1
            elif direction == "left" and self.col > 0:
                self.col -= 1
            elif direction == "right" and self.col < grid_size - 1:
                self.col += 1

    # Return current location of player
    def get_position(self):
        return (self.col, self.row)

    # Update knowledge base after another player shows them a card (disproving an accusation)
    def update_knowledge(self, new_card):
        self.knowledge.add(new_card)

    # Provide text summary for log
    def log_status(self):
        knowledge_list = ", ".join(sorted(self.knowledge))
        return f"{self.player_id} at ({self.col}, {self.row}) knows: {knowledge_list}"

    # Check if agent is currently in a room, needs to be in a room to make accusation 
    def is_in_room(self, rooms):
        for row_idx, row in enumerate(rooms):
            for col_idx, room_name in enumerate(row):
                if (self.col // 5 == col_idx) and (self.row // 5 == row_idx):
                    return room_name
        return None
