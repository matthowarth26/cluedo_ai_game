import pygame
import sys
from setup_game import setup_game
from players import players
from rooms import rooms, cell_size, grid_size, screen_size
from agents import PlayerAgent
from agent_accusation import try_accusation

# Number of players input in terminal 
def get_number_of_players():
    try:
        total_players = int(input("Enter number of players (2–6): "))
        if total_players < 2 or total_players > 6:
            print("Invalid number. Defaulting to 6 players.")
            total_players = 6
    except:
        print("Invalid input. Defaulting to 6 players.")
        total_players = 6
    return total_players

total_players = get_number_of_players()

# Initialize pygame
pygame.init()

# Create a window that calls the define screen size based on the board game and add space for log and button panels 
screen = pygame.display.set_mode((screen_size + 600, screen_size + 200))  # 150 left + 600 board + 450 right, and taller
pygame.display.set_caption("Cluedo")

# Initialize colors for grid, buttons and background 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ROOM_COLOR = (240, 240, 255)
LIGHT_GRAY = (220, 220, 220)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
LEFT_PANEL_COLOR = (200, 200, 200)

# Initialize fonts 
font = pygame.font.SysFont('arial', 20)
button_font = pygame.font.SysFont('arial', 24)

# Call setup_game function and input # of players 
active_players, mystery_solution, player_knowledge, leftover_cards, player_start_positions = setup_game(total_players)

# Create the player agents, assign them an ID, color, starting position, and the cards they are dealt 
player_agents = []
for player in active_players:
    agent = PlayerAgent(
        player_id=player["id"],
        color=player["color"],
        start_position=player_start_positions[player["id"]],
        starting_cards=player_knowledge[player["id"]]
    )
    player_agents.append(agent)

# Leftover cards are left face up in the game, so add them to the player's knowledgebase 
for agent in player_agents:
    agent.knowledge.update(leftover_cards)

# Store the information from the starting cards each player is dealt for log panel 
initial_player_knowledge = {}
for agent in player_agents:
    initial_player_knowledge[agent.player_id] = sorted(list(agent.knowledge))

# Set up positions for Next Round and Quite Game buttons 
button_rect = pygame.Rect(25, (screen_size + 200) // 2 - 25, 100, 50)  # Centered in taller window
quit_button_rect = pygame.Rect(screen_size // 2 + 100, (screen_size + 200) // 2 + 100, 200, 50)

# Initialize game state variables 
clock = pygame.time.Clock()
running = True # Quit game if false 
waiting_for_click = True # Wait for player to choose Next Round
round_number = 1 # Track # of rounds
round_accusations = [] # Store accusations made in current round 
show_initial_cards = True # Show initially dealt cards in log panel 
winner = None # Flag if player makes correct guess 

# Start game loop 
while running:
    screen.fill(WHITE)

    #Check to see if Next Round or Quit Game buttons are selected 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False #End game if Quit Game is selected

        if event.type == pygame.MOUSEBUTTONDOWN:
            if winner:
                if quit_button_rect.collidepoint(event.pos):
                    running = False # Check to see if winner is declared and end game
            else:
                if button_rect.collidepoint(event.pos):
                    waiting_for_click = False #Move to next round if selected

    #If next round is selected and no winner yet
    if not waiting_for_click and not winner:
        print("=" * 50)
        print(f"ROUND {round_number}")
        print("=" * 50)

        round_accusations = []  # Reset accusations for this round

        # Agent rolls dice, moves across the board given the sum of dice roll, enter new room, can make an accusation, and can update knowledge base is someone disproves them 
        for agent in player_agents:
            if not agent.is_active:
                continue

            moves = agent.roll_dice() # Dice roll 
            agent.move(moves, grid_size) # Moves based on dice roll 

            if agent.is_in_room(rooms):
                result, accusation = try_accusation(agent, player_agents, mystery_solution)
                guessed_character, guessed_room, guessed_weapon = accusation

                if guessed_character and guessed_room and guessed_weapon:
                    text = f"{agent.player_id}: {guessed_character} in {guessed_room} with {guessed_weapon}"
                    round_accusations.append(text)

                if result == "WIN":
                    winner = agent.player_id
                    waiting_for_click = True
                    break

        # Log player statuses
        for agent in player_agents: 
            print(agent.log_status())

        # Wait for click to start next round 
        round_number += 1
        waiting_for_click = True
        show_initial_cards = False

    # Add Quit Game button 
    pygame.draw.rect(screen, LEFT_PANEL_COLOR, (0, 0, 150, screen_size + 200))

    # Add Next Round button 
    if not winner:
        pygame.draw.rect(screen, GREEN, button_rect)
        button_text = button_font.render("Next Round", True, WHITE)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)

    # Draw game board & room layout 
    for row_idx, row in enumerate(rooms):
        for col_idx, room_name in enumerate(row):
            room_rect = pygame.Rect(
                150 + col_idx * 5 * cell_size,
                row_idx * 5 * cell_size,
                5 * cell_size,
                5 * cell_size
            )
            pygame.draw.rect(screen, ROOM_COLOR, room_rect)

            # Add names to each room 
            text_surface = font.render(room_name, True, BLACK) 
            text_rect = text_surface.get_rect(center=room_rect.center)
            screen.blit(text_surface, text_rect)

    # Add lighter gridlines to show tiles 
    for x in range(0, screen_size, cell_size):
        pygame.draw.line(screen, LIGHT_GRAY, (150 + x, 0), (150 + x, screen_size), 1)
    for y in range(0, screen_size, cell_size):
        pygame.draw.line(screen, LIGHT_GRAY, (150, y), (150 + screen_size, y), 1)

    # Add darker gridlines to show rooms 
    for row_idx, row in enumerate(rooms):
        for col_idx, room_name in enumerate(row):
            room_rect = pygame.Rect(
                150 + col_idx * 5 * cell_size,
                row_idx * 5 * cell_size,
                5 * cell_size,
                5 * cell_size
            )
            pygame.draw.rect(screen, BLACK, room_rect, 3)

    # Add player game pieces
    for agent in player_agents:
        x = 150 + agent.col * cell_size + cell_size // 2
        y = agent.row * cell_size + cell_size // 2
        pygame.draw.circle(screen, agent.color, (x, y), cell_size // 2 - 4)
        text_surface = font.render(agent.player_id, True, BLACK)
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    # Add right log panel 
    pygame.draw.rect(screen, (220, 220, 220), (screen_size + 150, 0, 450, screen_size + 200))

    # Display the answer to the mystery that the players are trying to solve 
    sidebar_font = pygame.font.SysFont('arial', 24)
    title_surface = sidebar_font.render("Mystery", True, (0, 0, 0))
    screen.blit(title_surface, (screen_size + 170, 20))

    murder_text = [
        f"{mystery_solution['murderer']}",
        f"in {mystery_solution['room']}",
        f"with {mystery_solution['weapon']}"
    ]
    y_offset = 60
    for line in murder_text:
        murder_surface = font.render(line, True, (0, 0, 0))
        screen.blit(murder_surface, (screen_size + 170, y_offset))
        y_offset += 30

    # Check if there are leftover cards and display them so that everyone can see what they are 
    if leftover_cards:
        y_offset += 30
        leftover_title = font.render("Leftover Cards:", True, (0, 0, 0))
        screen.blit(leftover_title, (screen_size + 170, y_offset))
        y_offset += 25
        for card in leftover_cards:
            card_surface = font.render(f"- {card}", True, (0, 0, 0))
            screen.blit(card_surface, (screen_size + 190, y_offset))
            y_offset += 20

    # Show all of the player's initial cards at start of game and then show accusations after each round 
    if show_initial_cards:
        y_offset += 30
        initial_cards_title = font.render("Player Cards:", True, (0, 0, 0))
        screen.blit(initial_cards_title, (screen_size + 170, y_offset))
        y_offset += 25

        for pid, cards in initial_player_knowledge.items():
            player_surface = font.render(f"{pid}:", True, (0, 0, 0))
            screen.blit(player_surface, (screen_size + 190, y_offset))
            y_offset += 20
            for card in cards:
                card_surface = font.render(f"- {card}", True, (0, 0, 0))
                screen.blit(card_surface, (screen_size + 210, y_offset))
                y_offset += 18
            y_offset += 10
    else:
        y_offset += 30
        accusation_title = font.render("Accusations This Round:", True, (0, 0, 0))
        screen.blit(accusation_title, (screen_size + 170, y_offset))
        y_offset += 25

        if round_accusations:
            for accusation in round_accusations:
                accusation_surface = font.render(f"- {accusation}", True, (0, 0, 0))
                screen.blit(accusation_surface, (screen_size + 190, y_offset))
                y_offset += 20
        else:
            no_accusation_surface = font.render("- None this round", True, (0, 0, 0))
            screen.blit(no_accusation_surface, (screen_size + 190, y_offset))
            y_offset += 20

    # If there is a winner announce who solved the murder and show Quit Game button to end game 
    if winner:
        winner_font = pygame.font.SysFont('arial', 48)
        winner_text = winner_font.render(f"{winner} solved the murder!", True, RED)
        winner_rect = winner_text.get_rect(center=(screen_size // 2 + 150, (screen_size + 200) // 2))
        screen.blit(winner_text, winner_rect)

        # Show quit game button 
        pygame.draw.rect(screen, BLACK, quit_button_rect)
        quit_text = font.render("Quit Game", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
        screen.blit(quit_text, quit_text_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
