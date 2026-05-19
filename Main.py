import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SpringApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа: сила упругости")

        self.root.state("zoomed")

        self.base_dir = Path(__file__).resolve().parent

        self.spring_path = self.base_dir / "pins" / "spring.png"
        self.weight_path = self.base_dir / "pins" / "weight.png"
        self.clamp_path = self.base_dir / "pins" / "clamp.png"
        self.hook_path = self.base_dir / "pins" / "hook.png"

        self.max_weights = 5

        # Масштаб изображения: 1 см = 22 px
        self.pixels_per_cm = 22

        # Один груз растягивает пружину на 0.2 см
        self.cm_per_weight = 0.2

        # Условия лабораторной работы
        self.g = 9.8                  # м/с^2
        self.mass_per_weight = 0.08   # кг
        self.l0_cm = 5.6              # начальная длина пружины, см

        # Относительная погрешность:
        # eps_m = 0.02, eps_g = 0.01, eps_x = 0.05
        self.epsilon_k = 0.02 + 0.01 + 0.05

        # Здесь хранятся проведённые опыты до закрытия приложения
        self.experiments = {}

        self.spring_start_height = 107
        self.current_stretch = 0
        self.target_stretch = 0

        self.current_weight_count = 0
        self.show_weights = False

        # Расстояние между грузами
        self.weight_spacing = 42

        # Координаты установки
        self.clamp_x = 45
        self.clamp_y = 57

        self.spring_x = 485
        self.spring_y = 118

        # Крючок
        self.hook_x = 485
        self.hook_offset_y = 0

        # Груз
        self.weight_x = 483
        self.weight_offset_y = 125

        self.create_widgets()
        self.draw_scene()

    def load_image(self, path, width, height):
        image = Image.open(path)
        image = image.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#000000")
        main_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(main_frame, width=800)
        self.left_frame.pack(side="left", fill="both")

        self.right_frame = tk.Frame(main_frame, bg="#FFFFFF")
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.left_frame,
            width=700,
            height=700,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        control_frame = tk.Frame(self.left_frame, bg="white")
        control_frame.pack(pady=10)

        tk.Label(
            control_frame,
            text="Количество грузов:",
            font=("Times New Roman", 12),
            bg="white",
            fg="black"
        ).grid(row=0, column=0, padx=5)

        self.weights_entry = tk.Entry(
            control_frame,
            width=10,
            font=("Times New Roman", 12),
            bg="white",
            fg="black"
        )
        self.weights_entry.insert(0, "0")
        self.weights_entry.grid(row=0, column=1, padx=5)

        tk.Button(
            control_frame,
            text="Принять",
            font=("Times New Roman", 12),
            fg="black",
            bg="white",
            command=self.accept_weights
        ).grid(row=0, column=2, padx=5)

        self.info_label = tk.Label(
            self.left_frame,
            text="Грузов: 0 | Длина пружины: 5.6 см",
            font=("Times New Roman", 12),
            bg="white",
            fg="black"
        )
        self.info_label.pack(pady=5)

        tk.Label(
            self.right_frame,
            text="Таблица расчётов",
            font=("Times New Roman", 18, "bold"),
            bg="white",
            fg="black"
        ).pack(pady=20)

        columns = (
            "num", "m", "mg", "l", "x", "k", "k_avg", "eps", "delta"
        )

        self.table = ttk.Treeview(
            self.right_frame,
            columns=columns,
            show="headings",
            height=6
        )

        headers = {
            "num": "№ опыта",
            "m": "m, кг",
            "mg": "mg, Н",
            "l": "l, м",
            "x": "x, м",
            "k": "K, Н/м",
            "k_avg": "kср, Н/м",
            "eps": "εk",
            "delta": "Δkср, Н/м"
        }

        widths = {
            "num": 70,
            "m": 80,
            "mg": 90,
            "l": 90,
            "x": 90,
            "k": 90,
            "k_avg": 100,
            "eps": 70,
            "delta": 110
        }

        for col in columns:
            self.table.heading(col, text=headers[col])
            self.table.column(col, width=widths[col], anchor="center")

        self.table.pack(fill="x", padx=20, pady=10)

        self.graph_button = tk.Button(
            self.right_frame,
            text="Построить график",
            font=("Times New Roman", 12),
            fg="black",
            bg="white",
            command=self.build_graph
        )
        self.graph_button.pack(pady=5)

        self.graph_frame = tk.Frame(self.right_frame, bg="white")
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.figure = Figure(figsize=(6.5, 3.2), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.graph_canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.graph_canvas.get_tk_widget().pack(fill="both", expand=True)

        self.draw_empty_graph()

        self.interval_label = tk.Label(
            self.right_frame,
            text=(
                "Доверительный интервал для k:\n"
                "Появится после проведения всех 5 испытаний и построения графика.\n\n"
                "Результат: k = kср ± Δkср"
            ),
            font=("Times New Roman", 13),
            fg="black",
            bg="white",
            justify="left"
        )
        self.interval_label.pack(anchor="nw", padx=30, pady=10)

        self.init_table()

    def init_table(self):
        self.table.delete(*self.table.get_children())

        for i in range(0, self.max_weights + 1):
            if i == 0:
                values = (
                    0,
                    "0",
                    "0",
                    f"{self.l0_cm / 100:.3f}",
                    "0",
                    "0",
                    "",
                    "",
                    ""
                )
            else:
                values = (i, "", "", "", "", "", "", "", "")

            self.table.insert("", "end", iid=str(i), values=values)

    def update_experiment_table(self, count):
        if count == 0:
            return

        # Масса грузов
        m = count * self.mass_per_weight

        # Сила упругости: F = mg
        mg = m * self.g

        # Удлинение пружины
        x_cm = count * self.cm_per_weight
        x_m = x_cm / 100

        # Полная длина пружины
        l_cm = self.l0_cm + x_cm
        l_m = l_cm / 100

        # Жёсткость пружины
        k = mg / x_m

        self.experiments[count] = {
            "m": m,
            "mg": mg,
            "l": l_m,
            "x": x_m,
            "k": k
        }

        filled_k = [data["k"] for data in self.experiments.values()]
        k_avg = sum(filled_k) / len(filled_k)

        delta_k = self.epsilon_k * k_avg

        for exp_num, data in self.experiments.items():
            self.table.item(
                str(exp_num),
                values=(
                    exp_num,
                    f"{data['m']:.2f}",
                    f"{data['mg']:.2f}",
                    f"{data['l']:.3f}",
                    f"{data['x']:.3f}",
                    f"{data['k']:.0f}",
                    f"{k_avg:.0f}",
                    f"{self.epsilon_k:.2f}",
                    f"{delta_k:.0f}"
                )
            )

    def draw_empty_graph(self):
        self.ax.clear()

        self.ax.set_title("График зависимости Fупр = f(l)", fontsize=12)
        self.ax.set_xlabel("l, м", fontsize=11)
        self.ax.set_ylabel("Fупр, Н", fontsize=11)

        self.ax.set_xlim(0.056, 0.067)
        self.ax.set_ylim(0, 4.2)

        self.ax.grid(True)

        self.graph_canvas.draw()

    def build_graph(self):
        if len(self.experiments) < self.max_weights:
            messagebox.showwarning(
                "Недостаточно данных",
                "Для построения графика нужно провести все 5 испытаний."
            )
            return

        sorted_experiments = sorted(self.experiments.items())

        l_values = [data["l"] for _, data in sorted_experiments]
        force_values = [data["mg"] for _, data in sorted_experiments]

        k_values = [data["k"] for _, data in sorted_experiments]
        k_avg = sum(k_values) / len(k_values)
        delta_k = self.epsilon_k * k_avg

        k_min = k_avg - delta_k
        k_max = k_avg + delta_k

        self.ax.clear()

        self.ax.plot(l_values, force_values, marker="o")
        self.ax.set_title("График зависимости Fупр = f(l)", fontsize=12)
        self.ax.set_xlabel("l, м", fontsize=11)
        self.ax.set_ylabel("Fупр, Н", fontsize=11)

        self.ax.grid(True)

        self.graph_canvas.draw()

        self.interval_label.config(
            text=(
                "Доверительный интервал для k:\n"
                f"{k_min:.0f} ≤ k ≤ {k_max:.0f} Н/м\n\n"
                f"Результат: k = {k_avg:.0f} ± {delta_k:.0f} Н/м"
            )
        )

    def draw_scene(self):
        spring_height = self.spring_start_height + self.current_stretch
        spring_bottom_y = self.spring_y + spring_height

        self.clamp_img = self.load_image(
            self.clamp_path,
            width=519,
            height=801
        )

        self.canvas.create_image(
            self.clamp_x,
            self.clamp_y,
            image=self.clamp_img,
            anchor="nw"
        )

        self.spring_img = self.load_image(
            self.spring_path,
            width=38,
            height=spring_height
        )

        self.canvas.create_image(
            self.spring_x,
            self.spring_y,
            image=self.spring_img,
            anchor="n"
        )

        self.hook_img = self.load_image(
            self.hook_path,
            width=13,
            height=131
        )

        self.canvas.create_image(
            self.hook_x,
            spring_bottom_y + self.hook_offset_y,
            image=self.hook_img,
            anchor="n"
        )

        if self.show_weights and self.current_weight_count > 0:

            self.weight_images = []

            for i in range(self.current_weight_count):
                weight_img = self.load_image(
                    self.weight_path,
                    width=66,
                    height=48
                )

                self.weight_images.append(weight_img)

                self.canvas.create_image(
                    self.weight_x,
                    spring_bottom_y + self.weight_offset_y + (i * self.weight_spacing),
                    image=weight_img,
                    anchor="n"
                )

    def accept_weights(self):
        try:
            count = int(self.weights_entry.get())

            if count < 0 or count > self.max_weights:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Ошибка",
                "Введите целое число от 0 до 5"
            )
            return

        self.current_weight_count = count
        self.show_weights = True

        stretch_cm = count * self.cm_per_weight

        self.target_stretch = int(
            stretch_cm * self.pixels_per_cm
        )

        self.update_experiment_table(count)

        self.animate_spring()

    def animate_spring(self):
        if self.current_stretch < self.target_stretch:
            self.current_stretch += 1

        elif self.current_stretch > self.target_stretch:
            self.current_stretch -= 1

        else:
            self.info_label.config(
                text=f"Грузов: {self.current_weight_count} | Длина пружины: {round((self.current_stretch / self.pixels_per_cm) + self.l0_cm, 1)} см"
            )
            return

        self.draw_scene()

        self.info_label.config(
            text=f"Грузов: {self.current_weight_count} | Длина пружины: {round((self.current_stretch / self.pixels_per_cm) + self.l0_cm, 1)} см"
        )

        self.root.after(10, self.animate_spring)


if __name__ == "__main__":
    root = tk.Tk()
    app = SpringApp(root)
    root.mainloop()
