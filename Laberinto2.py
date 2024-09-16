import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
import time

# Clase para representar el laberinto
class Maze:
    def __init__(self, filename):
        self.load_maze(filename)

    def load_maze(self, filename):
        with open(filename, 'r') as file:
            lines = file.read().splitlines()

        self.height = len(lines)
        self.width = max(len(line) for line in lines)

        self.walls = []
        self.start = None
        self.goal = None

        for i, line in enumerate(lines):
            row = []
            for j, char in enumerate(line):
                if char == 'A':
                    self.start = (i, j)
                    row.append(False)
                elif char == 'B':
                    self.goal = (i, j)
                    row.append(False)
                elif char == '#':
                    row.append(True)
                else:
                    row.append(False)
            self.walls.append(row)

        if self.start is None or self.goal is None:
            raise Exception("El laberinto debe tener un punto de inicio (A) y un punto final (B).")

    def is_wall(self, position):
        x, y = position
        return self.walls[x][y]

    def neighbors(self, position):
        row, col = position
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((r, c))
        return result

    # Resolver usando diferentes métodos
    def solve_with_method(self, method):
        if method == 'stack':  # DFS
            frontier = [(self.start, [])]  # Pila
        elif method == 'queue':  # BFS
            frontier = [(self.start, [])]  # Cola
        elif method == 'greedy':  # Greedy
            frontier = [(self.start, [], self.heuristic(self.start))]  # Prioridad por heurística
        elif method == 'astar':  # A*
            frontier = [(self.start, [], 0 + self.heuristic(self.start))]  # Prioridad por costo + heurística

        explored = set()
        node_count = 0

        while frontier:
            if method == 'stack':  # DFS
                current, path = frontier.pop()
            elif method == 'queue':  # BFS
                current, path = frontier.pop(0)
            elif method == 'greedy':  # Greedy
                frontier.sort(key=lambda x: x[2])  # Ordena por heurística (tercer elemento de la tupla)
                current, path, _ = frontier.pop(0)
            elif method == 'astar':  # A*
                frontier.sort(key=lambda x: x[2])  # Ordena por costo + heurística
                current, path, _ = frontier.pop(0)

            node_count += 1

            if current == self.goal:
                return path + [current], node_count  # Devuelve el camino y nodos visitados

            explored.add(current)

            for neighbor in self.neighbors(current):
                if neighbor not in explored and not any(frontier_node[0] == neighbor for frontier_node in frontier):
                    new_path = path + [current]

                    if method == 'greedy':
                        priority = self.heuristic(neighbor)
                        frontier.append((neighbor, new_path, priority))
                    elif method == 'astar':
                        cost = len(new_path)  # Costo real (longitud del camino actual)
                        priority = cost + self.heuristic(neighbor)  # Costo + heurística
                        frontier.append((neighbor, new_path, priority))
                    else:
                        frontier.append((neighbor, new_path))

        return [], node_count  # Si no hay solución

    # Heurística para Greedy y A*
    def heuristic(self, position):
        return abs(position[0] - self.goal[0]) + abs(position[1] - self.goal[1])


# Clase principal del juego
class MazeGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maze Solver")
        self.geometry("1600x900")  # Dimensiones fijas

        self.current_window = None
        self.character_image = None
        self.character_label = None
        self.maze_canvas = None
        self.cell_size = 40
        self.move_count = 0
        self.node_count = 0  # Contador de nodos visitados
        self.maze = None
        self.auto_solve = False
        self.solve_method = None

        # Iniciar la primera ventana
        self.show_first_window()

    def set_gif_background(self, frame, gif_file):
        gif_image = Image.open(gif_file)
        
        gif_frames = [ImageTk.PhotoImage(frame) for frame in ImageSequence.Iterator(gif_image)]

        def animate_gif(frame_index):
            frame.config(image=gif_frames[frame_index])
            frame_index = (frame_index + 1) % len(gif_frames)
            self.after(100, animate_gif, frame_index)

        frame = tk.Label(self.current_window)
        frame.pack(fill="both", expand=True)
        animate_gif(0)

    def show_first_window(self):
        if self.current_window:
            self.current_window.destroy()

        self.current_window = tk.Frame(self, bg="lightblue")
        self.current_window.pack(expand=True, fill="both")

        # Cargar fondo animado .gif
        self.set_gif_background(self.current_window, "background1.gif")

        label = tk.Label(self.current_window, text="Seleccione el método de resolución automática", bg="lightblue", font=("Arial", 16))
        label.place(relx=0.5, rely=0.4, anchor="center")

        # Botones para diferentes algoritmos
        methods = [("Resolver con Pilas (DFS)", 'stack', "blue"),
                   ("Resolver con Colas (BFS)", 'queue', "purple"),
                   ("Resolver con Greedy", 'greedy', "green"),
                   ("Resolver con A*", 'astar', "orange")]

        for i, (text, method, color) in enumerate(methods):
            button = tk.Button(self.current_window, text=text, command=lambda m=method: self.start_auto_mode(m), bg=color, font=("Arial", 14))
            button.place(relx=0.5, rely=0.5 + (i * 0.1), anchor="center")

    def start_auto_mode(self, method):
        self.auto_solve = True
        self.solve_method = method
        self.show_difficulty_window()

    def show_difficulty_window(self):
        if self.current_window:
            self.current_window.destroy()

        self.current_window = tk.Frame(self, bg="lightblue")
        self.current_window.pack(expand=True, fill="both")

        # Fondo animado para selección de dificultad
        self.set_gif_background(self.current_window, "background3.gif")

        label = tk.Label(self.current_window, text="Seleccione la dificultad del laberinto", bg="lightblue", font=("Arial", 16))
        label.place(relx=0.5, rely=0.2, anchor="center")

        difficulties = [("Fácil", "laberinto1.txt", "lightgreen"), 
                        ("Medio", "laberinto2.txt", "yellow"), 
                        ("Medio-Difícil", "laberinto3.txt", "orange"), 
                        ("Difícil", "laberinto4.txt", "red"), 
                        ("Maníaco", "laberinto5.txt", "purple")]

        for i, (text, file, color) in enumerate(difficulties):
            button = tk.Button(self.current_window, text=text, command=lambda f=file: self.load_maze(f), bg=color, font=("Arial", 14))
            button.place(relx=0.5, rely=0.3 + (i * 0.1), anchor="center")

    def load_maze(self, filename):
        self.maze = Maze(filename)
        self.show_maze_window()

    def show_maze_window(self):
        if self.current_window:
            self.current_window.destroy()

        
        self.current_window = tk.Frame(self, bg="lightblue")
        self.current_window.pack(expand=True, fill="both")

        # Ajustar el tamaño de las celdas en función del tamaño del laberinto y la ventana
        max_cell_width = 1400 // self.maze.width
        max_cell_height = 700 // self.maze.height
        self.cell_size = min(max_cell_width, max_cell_height)

        canvas_width = self.maze.width * self.cell_size
        canvas_height = self.maze.height * self.cell_size
        

        # Crear el canvas ajustado al tamaño del laberinto
        self.maze_canvas = tk.Canvas(self.current_window, width=canvas_width, height=canvas_height, bg="lightblue")
        

        # Centrar el canvas
        self.maze_canvas.pack(expand=True, anchor='center')
        

        # Dibujar el laberinto
        self.draw_maze()

        # Cargar imagen del personaje
        character_image = Image.open("character.jpg")
        character_image = character_image.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
        self.character_image = ImageTk.PhotoImage(character_image)

        self.character_label = tk.Label(self.maze_canvas, image=self.character_image)
        self.character_label.place(x=self.maze.start[1] * self.cell_size, y=self.maze.start[0] * self.cell_size)

        # Contador de movimientos
        self.move_count_label = tk.Label(self.current_window, text="Pasos: 0", font=("Arial", 16), bg="lightblue")
        self.move_count_label.pack()

        # Contador de nodos visitados
        self.node_count_label = tk.Label(self.current_window, text="Nodos visitados: 0", font=("Arial", 16), bg="lightblue")
        self.node_count_label.pack()

        if self.auto_solve:
            self.after(500, self.solve_maze_automatically)

    def draw_maze(self):
        for i in range(self.maze.height):
            for j in range(self.maze.width):
                if self.maze.walls[i][j]:
                    color = "gray"
                elif (i, j) == self.maze.start:
                    color = "green"
                elif (i, j) == self.maze.goal:
                    color = "red"
                else:
                    color = "white"

                self.maze_canvas.create_rectangle(
                    j * self.cell_size, i * self.cell_size,
                    (j + 1) * self.cell_size, (i + 1) * self.cell_size,
                    fill=color
                )

    def solve_maze_automatically(self):
        path, nodes = self.maze.solve_with_method(self.solve_method)
        self.node_count = nodes
        self.node_count_label.config(text=f"Nodos visitados: {self.node_count}")
        self.move_character_automatically(path)

    def move_character_automatically(self, path):
        if not path:
            messagebox.showinfo("Error", "No se encontró un camino.")
            return

        def move_step(index):
            if index < len(path):
                position = path[index]
                self.character_label.place(x=position[1] * self.cell_size, y=position[0] * self.cell_size)
                self.move_count += 1
                self.move_count_label.config(text=f"Pasos: {self.move_count}")
                self.after(500, move_step, index + 1)
            else:
                self.show_end_message()

        move_step(0)

    def show_end_message(self):
        result = messagebox.askyesno("¡Éxito!", "¡El personaje ha llegado a la meta! ¿Desea continuar?")
        if result:
            self.move_count = 0 
            self.show_first_window()
        else:
            self.quit()

if __name__ == "__main__":
    game = MazeGame()
    game.mainloop()
