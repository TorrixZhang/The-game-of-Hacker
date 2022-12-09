from PIL import Image, ImageTk
from a3_support import *
import tkinter as tk
import random


class Entity:

    def display(self) -> str:
        """
        Return the character used to represent this entity in a text-based grid.
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """Return the character used to represent this entity in a
        text-based grid.
        """
        return f"{self.__class__.__name__}()"


class Player(Entity):

    def display(self) -> str:
        """
        Return the character used to represent this entity in a text-based grid.

        Returns:
            The character representing a player: ’P’
        """
        return PLAYER


class Destroyable(Entity):

    def display(self) -> str:
        """
        Return the character representing a destroyable: ’D’

        Returns:
            The character representing a destroyable: ’D’
        """
        return DESTROYABLE


class Collectable(Entity):

    def display(self) -> str:
        """
        Return the character representing a collectable: ’C’

        Returns:
            The character representing a collectable: ’C’
        """
        return COLLECTABLE


class Blocker(Entity):

    def display(self) -> str:
        """Return the character representing a blocker: ’B’

        Returns:
            The character representing a blocker: ’B’
        """
        return BLOCKER


class Grid:
    def __init__(self, size: int) -> None:
        """A grid is constructed with a size representing the number of rows
        (equal to the number of columns) in the grid.

        Parameters:
            size(int):
            A size representing the number of rows which is equal to
            the number of columns in the grid
        """
        self._size = size
        self._entities = {}

    def get_size(self) -> int:
        """Return the size of the grid

        Returns:
            Return the size of the grid
        """
        return self._size

    def add_entity(self, position: Position, entity: Entity) -> None:
        """Add a given entity into the grid at a specified position. This entity
         is only added if the position is valid.

         Parameters:
             position(Position): A specified position
             entity(Entity): A given entity
         """
        if self.in_bounds(position):
            self._entities[position] = entity

    def get_entities(self) -> Dict[Position, Entity]:
        """Return the dictionary containing grid entities.

        Returns:
            The dictionary containing grid entities
        """
        return self._entities

    def get_entity(self, position: Position) -> Optional[Entity]:
        """Return a entity from the grid at a specific position or None if
        the position does not have a mapped entity.

        Parameters:
            position(Position): A specified position

        Returns:
            A entity from the grid at a specific position or None
        """
        return self._entities.get(position)

    def remove_entity(self, position: Position) -> None:
        """Remove an entity from the grid at a specified position.

        Parameters:
            position(Position): A specified position
        """
        if position in self._entities:
            self._entities.pop(position)

    def serialise(self) -> Dict[Tuple[int, int], str]:
        """Convert dictionary of Position and Entities into a simplified,
        serialised dictionary mapping tuples to characters, and return
        this serialised mapping.

        Returns:
            A simplified, serialised dictionary mapping tuples to characters
        """
        return {(position.get_x(), position.get_y()): entity.display() for
                position, entity in self._entities.items()}

    def in_bounds(self, position: Position) -> bool:
        """Return a boolean based on whether the position is valid in terms of
        the dimensions of the grid.

        Parameters:
            position(Position): A specified position

        Returns:
            Return True iff: x ≥ 0 and x < grid size, y ≥ 1 and y < grid size
        """
        return 0 <= position.get_x() < self._size and \
               1 <= position.get_y() < self._size

    def renew_entities(self, entities):
        """Renew the entities position in the grid

        Parameters:
             entities: Entities in the grid
        """
        self._entities = entities

    def __repr__(self):
        """Return a representation of this Grid.
        """
        return f"{self.__class__.__name__}({self._size})"


class Game:

    def __init__(self, size: int) -> None:
        """A game is constructed with a size representing the dimensions of
        the playing grid.

        Parameters:
            size(int):
            A size representing the number of rows which is equal to
            the number of columns in the grid
        """
        self._size = size
        self._game_over = False
        self._grid = Grid(size)
        self._player_position = Position(self._size // 2, 0)
        self._num_collected = 0
        self._num_destroyed = 0
        self._total_shots = 0

    def get_grid(self) -> Grid:
        """Return the instance of the grid held by the game.

        Returns:
            The instance of the grid held by the game.
        """
        return self._grid

    def get_player_position(self) -> Position:
        """Return the position of the player in the grid (top row, centre column)

        Returns:
            The position of the player in the grid=
        """
        return self._player_position

    def get_num_collected(self) -> int:
        """Return the total of Collectables acquired.

        Returns:
            The total of Collectables acquired.
        """
        return self._num_collected

    def get_num_destroyed(self) -> int:
        """Return the total of Destroyables removed with a shot.

        Returns:
            The total of Destroyables removed with a shot.
        """
        return self._num_destroyed

    def get_total_shots(self) -> int:
        """Return the total of shots taken.

        Returns:
            The total of shots taken.
        """
        return self._total_shots

    def rotate_grid(self, direction: str) -> None:
        """Rotate the positions of the entities within the grid depending on
        the direction they are being rotated.

        Parameters:
            direction(str):
            The direction the entities are being rotated
        """
        new_entities = {}
        direction = DIRECTIONS.index(direction)
        next_pos = ROTATIONS[direction]
        for current_position, entity in self._grid.get_entities().items():
            x = (current_position.get_x() + next_pos[0]) % self._size
            new_entities[Position(x, current_position.get_y())] = entity
        self._grid.renew_entities(new_entities)

    def _create_entity(self, display: str) -> Entity:
        """Uses a display character to create an Entity.

        Parameters:
            display(str):
            A display character represents a specified entity

        Returns:
            A specified entity
        """
        if display == Player:
            return Player()
        elif display == DESTROYABLE:
            return Destroyable()
        elif display == COLLECTABLE:
            return Collectable()
        elif display == BLOCKER:
            return Blocker()
        else:
            raise NotImplementedError()

    def generate_entities(self) -> None:
        """
        Method given to the students to generate a random amount of entities to
        add into the game after each step
        """
        # Generate amount
        entity_count = random.randint(0, self.get_grid().get_size() - 3)
        entities = random.choices(ENTITY_TYPES, k=entity_count)

        # Blocker in a 1 in 4 chance
        blocker = random.randint(1, 4) % 4 == 0

        # UNCOMMENT THIS FOR TASK 3 (CSSE7030)
        # bomb = False
        # if not blocker:
        #     bomb = random.randint(1, 4) % 4 == 0

        total_count = entity_count
        if blocker:
            total_count += 1
            entities.append(BLOCKER)

        # UNCOMMENT THIS FOR TASK 3 (CSSE7030)
        # if bomb:
        #     total_count += 1
        #     entities.append(BOMB)

        entity_index = random.sample(range(self.get_grid().get_size()),
                                     total_count)

        # Add entities into grid
        for pos, entity in zip(entity_index, entities):
            position = Position(pos, self.get_grid().get_size() - 1)
            new_entity = self._create_entity(entity)
            self.get_grid().add_entity(position, new_entity)

    def step(self) -> None:
        """This method moves all entities on the board by an offset of (0, -1).
        """
        new_entities = {}
        offset = MOVE
        # Move the current existing entities
        for position, entity in self._grid.get_entities().items():
            y = position.get_y() + offset[1]
            if y >= 1:
                new_entities[Position(position.get_x(), y)] = entity
            else:
                if isinstance(entity, Destroyable):
                    self._game_over = True
                    break
        self._grid.renew_entities(new_entities)
        # Add new entities to the grid
        self.generate_entities()

    def fire(self, shot_type: str) -> None:
        """Handles the firing/collecting actions of a player towards
        an entity within the grid.

        Parameters:
            shot_type(str): The shot type is firing or collecting
        """
        self._total_shots += 1
        x = self._player_position.get_x()
        # Find out the entities in the player's column
        for y in range(1, self._size):
            position = Position(x, y)
            entity = self._grid.get_entity(position)
            if entity is not None:
                if isinstance(entity, Blocker):
                    break
                elif isinstance(entity, Destroyable):
                    if shot_type == DESTROY:
                        self._num_destroyed += 1
                        self._grid.remove_entity(position)
                        break
                    else:
                        break
                elif isinstance(entity, Collectable):
                    if shot_type == COLLECT:
                        self._num_collected += 1
                        self._grid.remove_entity(position)
                        break
                    else:
                        break

    def has_won(self) -> bool:
        """Return True if the player has won the game.

        Returns:
            True if the player has won the game
        """
        return self._num_collected >= COLLECTION_TARGET

    def has_lost(self) -> bool:
        """Returns True if the game is lost (a Destroyable has reached
        the top row)

        Returns:
            True if the game is lost
        """
        return self._game_over


class AbstractField(tk.Canvas):

    def __init__(self, master, rows, cols, width, height, **kwargs):
        """AbstractField is an abstract view class which inherits from tk.Canvas
         and provides base functionality for other view classes.

        Parameters:
            master: Represents the master window
            rows: The number of columns in the grid
            cols: The number of rows in the grid
            width: The width of the grid
            height: The height of the grid
            **kwargs: Additional named arguments
        """
        super().__init__(master, width=width, height=height, **kwargs)
        self._master = master
        self._rows = rows
        self._cols = cols
        self._width = width
        self._height = height
        self._cell_width = width // cols
        self._cell_height = height // rows

    def get_bbox(self, position: Tuple[int, int]):
        """Returns the bounding box for the position; this is a tuple
        containing information about the pixel positions of the edges of
        the shape, in the form (x_min, y_min, x_max, y_max).

        Parameters:
            position(Tuple):
            The pixel positions of the edges of the shape,
            in the form (x_min, y_min, x_max, y_max).

        Returns:
            The bounding box for the position
        """
        x, y = position
        x_min = x * self._cell_width
        y_min = y * self._cell_height
        x_max = x_min + self._cell_width
        y_max = y_min + self._cell_height
        return x_min, y_min, x_max, y_max

    def pixel_to_position(self, pixel: Tuple[int, int]):
        """Converts the (x, y) pixel position (in graphics units)
        to a (row, column) position.

        Parameters:
            pixel(Tuple):
            The (x, y) pixel position (in graphics units)

        Returns:
            Entity position in the form of (row, column)
        """
        x_pixel, y_pixel = pixel
        x = x_pixel // self._cell_width
        y = y_pixel // self._cell_height
        return x, y

    def get_position_center(self, position):
        """Gets the graphics coordinates for the center of
        the cell at the given (row, column) position.

        Parameters:
            position(Tuple):
            A specified position

        Returns:
            The graphics coordinates for the center of the cell
        """
        x_min, y_min, x_max, y_max = self.get_bbox(position)
        return (x_min + x_max) // 2, (y_min + y_max) // 2

    def annotate_position(self, position, text, fill="black"):
        """Annotates the center of the cell at the given
        (row, column) position with the provided text.

        Parameters:
            position(Tuple): The given position
            text(str): The text represents the kind of the entities
            fill(str): The default color
        """
        x, y = self.get_position_center(position)
        self.create_text(x, y, text=text, fill=fill)


class GameField(AbstractField):

    def __init__(self, master, size, width, height, **kwargs):
        """GameField is a visual representation of the game grid
        which inherits from AbstractField.

        Parameters:
            master: Represents the master window
            size: The number of rows (= number of columns) in the grid
            width: The width of the grid (in pixels)
            height: The height of the grid (in pixels)
            **kwargs: Additional named arguments
        """
        super().__init__(master, size, size, width, height, **kwargs)
        self._size = size

    def draw_grid(self, entities: Dict[Tuple[int, int], str]):
        """Draws the entities (found in the Grid’s entity dictionary)
        in the game grid at their given position using a coloured rectangle
        with superimposed text identifying the entity.

        Parameters:
            entities:
            A dictionary contains the position and the name of the entities
        """
        self.draw_player_area()
        for position, entity in entities.items():
            x_min, y_min, x_max, y_max = self.get_bbox(position)
            self.create_rectangle(x_min, y_min, x_max, y_max,
                                  fill=COLOURS[entity])
            self.annotate_position(position, entity)

    def draw_player_area(self):
        """Draws the grey area a player is placed on.
        """
        # Draw player area
        self.create_rectangle(0, 0, self._width, self._cell_height,
                              fill=PLAYER_AREA)
        # Draw player entity
        player_x = self._size // 2
        x_min, y_min, x_max, y_max = self.get_bbox((player_x, 0))
        self.create_rectangle(x_min, y_min, x_max, y_max,
                              fill=COLOURS[PLAYER])
        self.annotate_position((player_x, 0), PLAYER)


class ScoreBar(AbstractField):

    def __init__(self, master, rows, **kwargs):
        """ScoreBar is a visual representation of shot statistics from
        the player which inherits from AbstractField.

        Parameters:
            master: Represents the master window
            rows(int): The number of rows contained in the ScoreBar canvas
            **kwargs: Additional named arguments
        """
        super().__init__(master, rows, 2, SCORE_WIDTH, MAP_HEIGHT, **kwargs)

    def draw_scores(self, collected, destroyed):
        """Draws the score bar which contains the count of collected entities
        and destroyed entities

        Parameters:
            collected(str): The number of collected entities
            destroyed(str): The number of destroyed entities
        """
        self.create_text(SCORE_WIDTH / 2, MAP_HEIGHT / self._rows / 2,
                         text="Score", fill="white", font="Arial, 24")
        self.annotate_position((0, 1), text="Collected", fill="white")
        self.annotate_position((0, 2), text="Destroyed", fill="white")
        self.annotate_position((1, 1), text=collected, fill="white")
        self.annotate_position((1, 2), text=destroyed, fill="white")


class HackerController:

    def __init__(self, master: tk.Tk, size):
        """HackerController acts as the controller for the Hacker game

        Parameters:
            master: Represents the master window
            size(int): Represents the number of rows (= number of columns)
            in the game map
        """
        self._master = master
        self._size = size
        self._game = Game(size)

        # Draw the other elements in the game map
        self._title_label = tk.Label(master, text=TITLE, fg="white",
                                     bg=TITLE_BG, font=TITLE_FONT)
        self._title_label.pack(fill=tk.BOTH)
        self._frame = tk.Frame(self._master)
        self._frame.pack()
        self._game_field = GameField(self._frame, size, MAP_WIDTH,
                                     MAP_HEIGHT, bg=FIELD_COLOUR)
        self._game_field.pack(side=tk.LEFT)

        self._score_bar = ScoreBar(self._frame, size, bg=SCORE_COLOUR)
        self._score_bar.pack(side=tk.LEFT)

        # bind event with keypress
        self._master.bind("<Key>", self.handle_keypress)

        # Initialise the Game model
        self.draw(self._game)
        self._master.after(2000, self.step)

    def handle_keypress(self, event):
        """This method should be called when the user presses any key
        during the game. It must handle error checking and event calling and
        execute methods to update both the model and the view accordingly.

        Parameters:
            event: Represents the user press a key
        """
        key_press = event.keysym.upper()
        if key_press in DIRECTIONS:
            self.handle_rotate(key_press)
        elif key_press in SHOT_TYPES:
            self.handle_fire(key_press)

    def draw(self, game: Game):
        """Clears and redraws the view based on the current game state.

        Parameters:
            game: The current game state
        """
        self._game_field.delete(tk.ALL)
        self._game_field.draw_grid(game.get_grid().serialise())
        self._score_bar.delete(tk.ALL)
        self._score_bar.draw_scores(game.get_num_collected(),
                                    game.get_num_destroyed())

    def handle_rotate(self, direction):
        """Handles rotation of the entities and redrawing the game.
        It may be easiest for the handle_keypress method to call handle_rotate
        with the relevant arguments.

        Parameters:
            direction(str):
            The direction the entities are being rotated
        """
        self._game.rotate_grid(direction)
        self.draw(self._game)

    def handle_fire(self, shot_type):
        """Handles the firing of the specified shot type and redrawing of
        the game. It may be easiest for the handle_keypress method to call
        handle_fire with the relevant arguments.

        Parameters:
            shot_type(str): The shot type is firing or collecting
        """
        self._game.fire(shot_type)
        self.draw(self._game)

    def step(self):
        """The step method is called every 2 seconds. This method triggers
        the step method for the game and updates the view accordingly.
        """
        self._game.step()
        self.draw(self._game)
        # Use a recursion to call step
        self._master.after(2000, self.step)


class ImageGameField(GameField):

    def __init__(self, master, size, width, height, **kwargs):
        super().__init__(master, size, width, height, **kwargs)
        self._images = []

    def draw_grid(self, entities: Dict[Tuple[int, int], str]):
        """Draws the entities (found in the Grid’s entity dictionary)
        in the game grid at their given position using a coloured rectangle
        with superimposed text identifying the entity.

        Parameters:
            entities(Dict):
            A dictionary contains the position and the name of the entities
        """
        self.delete(tk.ALL)
        self.draw_player_area()

        for position, entity in entities.items():
            x, y = self.get_position_center(position)
            self.display_image(x, y, entity)

    def draw_player_area(self):
        """Draws the grey area a player is placed on.
        """
        # Draw player area
        self.create_rectangle(0, 0, self._rows * self._cell_width,
                              self._cell_height, fill=PLAYER_AREA, width=0)
        # Draw player image
        x, y = self.get_position_center((self._size // 2, 0))
        self.display_image(x, y, PLAYER)

    def display_image(self, x, y, entity):
        """Display the corresponding image on the position of a entity

        Parameters:
            x(int): The x position of the entity
            y(int): The y position of the entity
            entity(str): The type of the entity
        """
        image = Image.open(f"images/{IMAGES[entity]}")
        image = ImageTk.PhotoImage(image)
        self._images.append(image)
        self.create_image(x, y, image=image)


class AdvancedHackerController(HackerController):

    def __init__(self, master: tk.Tk, size):
        """AdvancedHackerController acts as the controller for the Hacker game
        in task 2

        Parameters:
            master: Represents the master window
            size(int): Represents the number of rows (= number of columns)
            in the game map
        """
        self._master = master
        self._size = size
        self._game = Game(size)

        # Draw the other elements in the game
        self._title_label = tk.Label(master, text=TITLE, fg="white",
                                     bg=TITLE_BG, font=TITLE_FONT)
        self._title_label.pack(fill=tk.BOTH)
        self._frame = tk.Frame(self._master)
        self._frame.pack()
        self._game_field = ImageGameField(self._frame, size, MAP_WIDTH,
                                          MAP_HEIGHT, bg=FIELD_COLOUR)
        self._game_field.pack(side=tk.LEFT)

        self._score_bar = ScoreBar(self._frame, size, bg=SCORE_COLOUR)
        self._score_bar.pack(side=tk.LEFT)
        self._status_bar = StatusBar(self._master)
        self._status_bar.pack()

        # bind event with keypress
        self._master.bind("<Key>", self.handle_keypress)

        # Initialise the Game model
        self.draw(self._game)
        self._master.after(2000, self.step)

    def draw(self, game):
        """Clears and redraws the view based on the current game state and
        update the total shot count number in the status bar

        Parameters:
            game: The current game state
        """
        super().draw(game)
        # Update the total shot count number
        self._status_bar.total_shots_count(game.get_total_shots())

    def step(self):
        """The step method is called every 2 seconds. This method triggers
        the step method for the game and updates the view accordingly."""
        self._game.step()
        self.draw(self._game)
        # Use a recursion to call step
        self._master.after(2000, self.step)


class StatusBar(tk.Frame):

    def __init__(self, master, **kwargs):
        """ A StatusBar class that inherits from tk.Frame. In this frame,
        it includes a shot counter, a game timer and a ‘Pause/Play’ button

        Parameters:
            master: Represents the master window
            **kwargs: Additional named arguments
        """
        super().__init__(master, **kwargs)
        # Draw the shot counter, game timer and pause button
        self._total_shots = tk.Label(master, text="Total Shots \n 0")
        self._total_shots.pack(side=tk.LEFT, padx=MAP_WIDTH // 5)
        self._timer_label = tk.Label(master, text="Timer \n 0m 0s")
        self._timer_label.pack(side=tk.LEFT, padx=MAP_WIDTH // 10)
        self._pause_button = tk.Button(master, text="Pause")
        self._pause_button.pack(side=tk.RIGHT, padx=SCORE_WIDTH // 2.5)

    def total_shots_count(self, total_shots):
        """Display the number of total shots on the status bar

        Parameters:
            total_shots(int): The number of total shots
        """
        self._total_shots.config(text=f"Total Shot \n {total_shots}")


def start_game(root, TASK=TASK):
    controller = HackerController

    if TASK != 1:
        controller = AdvancedHackerController

    app = controller(root, GRID_SIZE)
    return app


def main():
    root = tk.Tk()
    root.title(TITLE)
    app = start_game(root)
    root.mainloop()


if __name__ == '__main__':
    main()
