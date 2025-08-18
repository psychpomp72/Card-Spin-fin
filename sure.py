from manim import *
import numpy as np
import random

# --- Configuration ---
CARD_ASPECT_RATIO = 3.5 / 2.5
CARD_WIDTH = 1.5
CARD_HEIGHT = CARD_WIDTH * CARD_ASPECT_RATIO
CORNER_RADIUS = 0.08
PADDING = 0.12
TEXT_SCALE = 0.4
MIN_SEPARATION = max(CARD_WIDTH, CARD_HEIGHT) * 1.1

# --- PokerCard Class ---
class PokerCard(VGroup):
    # ... (PokerCard class code remains the same) ...
    def __init__(
        self,
        rank: str,
        suit: str,
        width: float = CARD_WIDTH,
        height: float = CARD_HEIGHT,
        corner_radius: float = CORNER_RADIUS,
        padding: float = PADDING,
        text_scale: float = TEXT_SCALE,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.rank = str(rank).upper()
        self.suit = suit.upper()
        self.card_width = width
        self.card_height = height
        self.corner_radius = corner_radius
        self.padding = padding
        self.text_scale = text_scale
        suit_map = {
            "S": {"char": "♠", "color": BLACK},
            "H": {"char": "♥", "color": RED},
            "D": {"char": "♦", "color": RED},
            "C": {"char": "♣", "color": BLACK},
        }
        if self.suit not in suit_map:
            raise ValueError(f"Invalid suit: {self.suit}. Use 'S', 'H', 'D', or 'C'.")
        suit_info = suit_map[self.suit]
        suit_char = suit_info["char"]
        suit_color = suit_info["color"]
        self.body = RoundedRectangle(
            width=self.card_width,
            height=self.card_height,
            corner_radius=self.corner_radius,
            color=WHITE, fill_opacity=1, stroke_color=BLACK, stroke_width=1.5,
        )
        try:
            font = "SF Pro Text Semibold"
            _ = Text("test", font=font) # Test font existence indirectly
        except:
            font = "Sans" # Fallback
        rank_text = Text(self.rank, color=suit_color, font=font).scale(self.text_scale)
        suit_text = Text(suit_char, color=suit_color, font=font).scale(self.text_scale * 1.5)
        top_left_rank = rank_text.copy()
        top_left_suit = suit_text.copy()
        top_left_group = VGroup(top_left_rank, top_left_suit).arrange(DOWN, buff=self.padding * 0.5, center=False, aligned_edge=LEFT)
        top_left_group.move_to(self.body.get_corner(UL) + RIGHT * self.padding + DOWN * self.padding, aligned_edge=UL)
        bottom_right_rank = rank_text.copy()
        bottom_right_suit = suit_text.copy()
        bottom_right_group = VGroup(bottom_right_rank, bottom_right_suit).arrange(DOWN, buff=self.padding * 0.5, center=False, aligned_edge=LEFT)
        bottom_right_group.rotate(PI)
        bottom_right_group.move_to(self.body.get_corner(DR) + LEFT * self.padding + UP * self.padding, aligned_edge=DR)
        self.add(self.body, top_left_group, bottom_right_group)
        self.move_to(ORIGIN)


# --- Scene Definition ---
class CardsMoveThenRotateCirclee(Scene): # Renamed class
    def construct(self):
        # 1. Define the cards (9 cards)
        card_defs = [
            ("Souptik", "D"), ("Rider", "S"), ("Mona", "S"), ("Badre", "D"),
            ("Bella", "H"), ("Eddie", "C"), ("Zhi", "C"), ("Abde", "D"),
            ("Mykel", "S")
        ]
        num_cards = len(card_defs)
        circle_radius = 3

        # Define screen boundaries for random placement
        max_x = config.frame_width / 2 - CARD_WIDTH / 2 - 0.3
        max_y = config.frame_height / 2 - CARD_HEIGHT / 2 - 0.3
        x_bounds = (-max_x, max_x)
        y_bounds = (-max_y, max_y)

        # 2. Create PokerCard objects with overlap prevention
        cards = VGroup()
        placed_card_centers = []
        max_placement_retries = 200

        for rank, suit in card_defs:
            card = PokerCard(rank, suit)
            placed = False
            for attempt in range(max_placement_retries):
                start_x = random.uniform(*x_bounds)
                start_y = random.uniform(*y_bounds)
                potential_center = np.array([start_x, start_y, 0])
                is_overlapping = False
                for existing_center in placed_card_centers:
                    distance = np.linalg.norm(potential_center - existing_center)
                    if distance < MIN_SEPARATION:
                        is_overlapping = True
                        break
                if not is_overlapping:
                    card.move_to(potential_center)
                    cards.add(card)
                    placed_card_centers.append(potential_center)
                    placed = True
                    break
            if not placed:
                print(f"Warning: Could not place card {rank}{suit} without overlap after {max_placement_retries} attempts. Placing anyway.")
                card.move_to(potential_center)
                cards.add(card)
                placed_card_centers.append(potential_center)

        # 3. Animate the appearance
        self.play(
            LaggedStart(*[Create(card) for card in cards], lag_ratio=0.1),
            run_time=3
        )
        self.wait(0.5)

        # --- MODIFIED STEP 4: Move to Circle Positions (No Rotation/Scale) ---
        move_animations = []
        target_positions = [] # Store target positions for rotation step
        angle_step = TAU / num_cards
        for i, card in enumerate(cards):
            angle = PI/2 - angle_step/2 + i * angle_step
            position = np.array([
                circle_radius * np.cos(angle),
                circle_radius * np.sin(angle),
                0
            ])
            target_positions.append(position) # Store the calculated position
            # Use .animate.move_to for movement only
            move_animations.append(card.animate.move_to(position))

        self.play(
            *move_animations,
            run_time=1 # Adjust time for movement
        )
        self.wait(0.1) # Pause after moving

        # --- ADDED STEP 4b: Rotate Cards In Place ---
        rotate_animations = []
        for i, card in enumerate(cards):
            # Calculate the same angle as before to know the target rotation
            angle = PI/2 - angle_step/2 + i * angle_step
            # Calculate required rotation angle to face outwards
            rotation_angle = angle - PI/2 + PI
            # Use Rotate animation class for rotation around Z-axis (OUT)
            rotate_animations.append(Rotate(card, angle=rotation_angle, axis=OUT))

        self.play(
            *rotate_animations,
            run_time=1.0 # Adjust time for rotation
        )
        self.wait(0.1) # Pause after rotating


        # --- Renumbered Steps ---
        # 5. Animate cards moving to the center (ORIGIN)
        self.play(
            *[card.animate.move_to(ORIGIN) for card in cards],
            run_time=1.5
        )
        self.wait(0.5)

        # 6. Rotate cards to be flat (face up) at the center
        target_cards_flat = VGroup()
        for rank, suit in card_defs:
            flat_card = PokerCard(rank, suit)
            target_cards_flat.add(flat_card)

        self.play(
            Transform(cards, target_cards_flat),
            run_time=1.0
        )
        self.wait(1)