import random
from characters import characters
from players import players
from weapons import weapons
from rooms import rooms, cell_size, grid_size, screen_size

# Define function to setup new game based on number of players
def setup_game(total_players):
    active_players = players[:total_players]

    # Randomly select cards for murder deck (mystery solution)
    murderer_card = random.choice(characters)
    murder_weapon = random.choice(weapons)
    murder_room = random.choice([room for row in rooms for room in row])

    # Store mystery_solution 
    mystery_solution = {
        "murderer": murderer_card["name"],
        "weapon": murder_weapon,
        "room": murder_room
    }

    # Prepare deck for dealing by removing the cards chosen for murder deck 
    remaining_characters = [c for c in characters if c != murderer_card]
    remaining_weapons = [w for w in weapons if w != murder_weapon]
    remaining_rooms = [r for row in rooms for r in row if r != murder_room]

    # Create the deck & randomly shuffle
    deck = [c["name"] for c in remaining_characters] + remaining_weapons + remaining_rooms
    random.shuffle(deck)

    # Deal cards evenly to players 
    cards_per_player = len(deck) // total_players # # of cards per player 
    player_knowledge = {player["id"]: [] for player in active_players}

    # Dealing loop 
    deck_pointer = 0
    for _ in range(cards_per_player):
        for player in active_players:
            player_id = player["id"]
            player_knowledge[player_id].append(deck[deck_pointer])
            deck_pointer += 1

    leftover_cards = deck[deck_pointer:] # Record if there are cards leftover for start of game 

    # Define possible starting positions for each player on board 
    starting_positions = [
        (0, 2), (0, 7), (0, 12),
        (14, 2), (14, 7), (14, 12)
    ]
    random.shuffle(starting_positions)

    player_start_positions = {}
    for i, player in enumerate(active_players):
        player_start_positions[player["id"]] = starting_positions[i]

    return active_players, mystery_solution, player_knowledge, leftover_cards, player_start_positions
