import random
from rooms import rooms

# Full list of possible cards for accusations 
CHARACTERS = ["Miss Scarlet", "Professor Plum", "Mrs. White", "Colonel Mustard", "Mr. Green", "Mrs. Peacock"]
WEAPONS = ["Knife", "Revolver", "Rope", "Wrench", "Candlestick", "Lead Pipe"]
ROOMS = [
    "Study", "Great Hall", "Lounge",
    "Billiard Room", "Kitchen", "Dining Room",
    "Library", "Ballroom", "Conservatory"
]

# Function defines player trying to make an accusation to solve the mystery
def try_accusation(agent, other_agents, mystery_solution):
    # List the characters and weapons that the player does not know 
    unknown_characters = [c for c in CHARACTERS if c not in agent.knowledge]
    unknown_weapons = [w for w in WEAPONS if w not in agent.knowledge]

    # Player include current room in their accusation
    guessed_room = agent.is_in_room(rooms)

    # Check if agent is in a room
    if guessed_room is None:
        return False, (None, None, None)  # No accusation if not in a room

    # Generate random character and weapon from unknown lists
    guessed_character = random.choice(unknown_characters)
    guessed_weapon = random.choice(unknown_weapons)

    # Print accusation 
    print(f"{agent.player_id} makes an accusation: {guessed_character} in {guessed_room} with {guessed_weapon}")

    # Check if player's accusation solves the mystery 
    if (guessed_character == mystery_solution['murderer'] and
        guessed_weapon == mystery_solution['weapon'] and
        guessed_room == mystery_solution['room']):
        print(f"{agent.player_id} SOLVED the murder correctly!")
        agent.is_active = False
        return "WIN", (guessed_character, guessed_room, guessed_weapon) # If guess is correct, player wins 

    # If guess is incorrect, check if another player can disprove one element of their accusation
    revealed_card = None
    for other_agent in other_agents:
        if other_agent.player_id == agent.player_id:
            continue
        possible_cards = [guessed_character, guessed_weapon, guessed_room] # Check to see if another player possesses a card that was guessed 
        for card in possible_cards:
            if card in other_agent.knowledge:
                revealed_card = card
                break
        if revealed_card:
            break
    
    # If one player reveals their card to accusing player, add this information in their knowledge base 
    if revealed_card:
        agent.update_knowledge(revealed_card)
        print(f"{agent.player_id} learns {revealed_card} from another player.")
    else:
        print(f"No players could disprove {agent.player_id}'s accusation.") # No information gained during this round 

    return False, (guessed_character, guessed_room, guessed_weapon)

