import tkinter as tk
import sys
from dataclasses import dataclass
from tkinter import messagebox, ttk
from pathlib import Path
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(__file__).resolve().parent / relative_path


@dataclass(frozen=True)
class SpringVersion:
    stiffness: int
    spring_file: str
    clamp_file: str
    l0_cm: float
    cm_per_weight: float
    stretch_per_weight_px: float
    spring_width: int
    spring_start_height: int
    spring_x_offset: int = 0
    hook_x_offset: int = 0
    hook_y_offset: int = 0
    weight_x_offset: int = 0
    weight_y_offset: int = 125


class SpringApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа: сила упругости")

        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda event: self.root.attributes("-fullscreen", False))

        self.base_dir = resource_path("")

        self.weight_path = self.base_dir / "pins" / "weight.png"
        self.hook_path = self.base_dir / "pins" / "hook.png"
        self.logo_path = self.base_dir / "pins" / "KIP_FIN.png"

        self.max_weights = 5

        # Масштаб изображения: 1 см = 22 px
        self.pixels_per_cm = 22

        # Условия лабораторной работы
        self.g = 9.8                  # м/с^2
        self.mass_per_weight = 0.08   # кг
        self.l0_cm = 5.6              # начальная длина пружины, см
        self.cm_per_weight = 0.2      # удлинение на один груз из исходного опыта, см

        self.stiffness_options = (200, 300, 400, 500, 600)
        self.spring_versions = self.create_spring_versions()
        self.applied_stiffness = 400
        self.selected_stiffness = tk.IntVar(value=self.applied_stiffness)
        self.active_spring_version = self.spring_versions[self.applied_stiffness]
        self.spring_path = self.get_spring_path(self.active_spring_version)

        # Относительная погрешность:
        # eps_m = 0.02, eps_g = 0.01, eps_x = 0.05
        self.epsilon_k = 0.02 + 0.01 + 0.05

        # Здесь хранятся проведённые опыты до закрытия приложения
        self.experiments = {}

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

        # Груз
        self.weight_x = 483

        self.create_widgets()
        self.draw_scene()

    def create_spring_versions(self):
        versions = {}
        asset_scale = 3
        stretch_by_stiffness = {
            200: 40 / self.max_weights,
            300: 30 / self.max_weights,
            400: 22 / self.max_weights,
            500: 17.6 / self.max_weights,
            600: 14.7 / self.max_weights
        }
        lab_lengths = {
            # формат: жёсткость: (длина без груза, длина с 5 грузами), см
            200: (6.6, 8.6),
            300: (6.0, 7.4),
            400: (self.l0_cm, self.l0_cm + self.max_weights * self.cm_per_weight),
            500: (5.0, 5.8),
            600: (4.5, 5.2)
        }
        hook_offsets = {
            # формат: жёсткость: (сдвиг крюка по x, сдвиг начала крюка по y)
            200: (0, 0),
            300: (0, 0),
            400: (0, 0),
            500: (0, 0),
            600: (0, 0)
        }

        for stiffness in self.stiffness_options:
            spring_file = f"spring{stiffness}.png"
            spring_width, spring_height = self.get_scaled_image_size(
                spring_file,
                asset_scale
            )

            versions[stiffness] = SpringVersion(
                stiffness=stiffness,
                spring_file=spring_file,
                clamp_file=f"clamp{stiffness}.png",
                l0_cm=lab_lengths[stiffness][0],
                cm_per_weight=(
                    (lab_lengths[stiffness][1] - lab_lengths[stiffness][0])
                    / self.max_weights
                ),
                stretch_per_weight_px=stretch_by_stiffness[stiffness],
                spring_width=spring_width,
                spring_start_height=spring_height,
                # Для ручной подгонки стыка крюка и пружины
                spring_x_offset=0,
                hook_x_offset=hook_offsets[stiffness][0],
                hook_y_offset=hook_offsets[stiffness][1],
                weight_x_offset=0,
                weight_y_offset=125
            )

        return versions

    def get_scaled_image_size(self, file_name, scale):
        path = self.base_dir / "pins" / file_name

        with Image.open(path) as image:
            width, height = image.size

        return round(width / scale), round(height / scale)

    def get_spring_path(self, version):
        return self.base_dir / "pins" / version.spring_file

    def get_clamp_path(self, version):
        return self.base_dir / "pins" / version.clamp_file

    def load_image(self, path, width, height):
        image = Image.open(path)
        image = image.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#000000")
        main_frame.pack(fill="both", expand=True)

        self.create_stiffness_panel(main_frame)

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
            "num": 40,
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
            text=self.get_interval_placeholder_text(),
            font=("Times New Roman", 13),
            fg="black",
            bg="white",
            justify="left"
        )
        self.interval_label.pack(anchor="nw", padx=30, pady=10)

        self.init_table()

    def create_stiffness_panel(self, parent):
        self.stiffness_buttons = {}

        panel = tk.Frame(parent, bg="#111827")
        panel.pack(side="top", fill="x")

        content = tk.Frame(panel, bg="#111827")
        content.pack(fill="x", padx=36, pady=12)

        self.header_logo_img = self.load_image(
            self.logo_path,
            width=150,
            height=72
        )

        tk.Label(
            content,
            image=self.header_logo_img,
            bg="#111827",
            bd=0
        ).pack(side="right", anchor="ne", padx=(20, 0))

        tk.Label(
            content,
            text="Выбор жёсткости:",
            font=("Times New Roman", 14, "bold"),
            bg="#111827",
            fg="#F9FAFB"
        ).pack(side="left", padx=(0, 18))

        for stiffness in self.stiffness_options:
            button = tk.Radiobutton(
                content,
                text=f"{stiffness}\nН/м",
                variable=self.selected_stiffness,
                value=stiffness,
                indicatoron=False,
                width=8,
                height=2,
                font=("Times New Roman", 13, "bold"),
                command=self.refresh_stiffness_buttons,
                relief="flat",
                bd=0,
                cursor="hand2"
            )
            button.pack(side="left", padx=4)
            self.stiffness_buttons[stiffness] = button

        tk.Button(
            content,
            text="Применить",
            font=("Times New Roman", 12, "bold"),
            fg="black",
            bg="#A11A05",
            activeforeground="white",
            activebackground="#E40000",
            relief="flat",
            padx=24,
            pady=10,
            cursor="hand2",
            command=self.apply_selected_stiffness
        ).pack(side="left", padx=(32, 12))

        self.current_stiffness_label = tk.Label(
            content,
            text="",
            font=("Times New Roman", 12, "bold"),
            bg="#F9FAFB",
            fg="#111827",
            padx=16,
            pady=10,
            relief="solid",
            bd=1
        )
        self.current_stiffness_label.pack(side="left", padx=4)

        self.refresh_stiffness_buttons()
        self.update_current_stiffness_label()

    def refresh_stiffness_buttons(self):
        selected = self.selected_stiffness.get()

        for stiffness, button in self.stiffness_buttons.items():
            if stiffness == selected:
                button.config(
                    bg="#2563EB",
                    fg="white",
                    activebackground="#2563EB",
                    activeforeground="white"
                )
            else:
                button.config(
                    bg="#F9FAFB",
                    fg="#111827",
                    activebackground="#E5E7EB",
                    activeforeground="#111827"
                )

    def update_current_stiffness_label(self):
        self.current_stiffness_label.config(
            text=f"Текущее значение: {self.applied_stiffness} Н/м"
        )

    def apply_selected_stiffness(self):
        new_stiffness = self.selected_stiffness.get()

        if new_stiffness == self.applied_stiffness:
            return

        if self.experiments:
            confirmed = messagebox.askyesno(
                "Подтверждение смены жёсткости",
                (
                    "В таблице уже есть проведённые опыты.\n"
                    "При смене жёсткости текущие данные будут очищены.\n\n"
                    "Продолжить?"
                )
            )

            if not confirmed:
                self.selected_stiffness.set(self.applied_stiffness)
                self.refresh_stiffness_buttons()
                return

        self.set_spring_version(new_stiffness)

    def set_spring_version(self, stiffness):
        self.active_spring_version = self.spring_versions[stiffness]
        self.applied_stiffness = stiffness
        self.spring_path = self.get_spring_path(self.active_spring_version)

        self.reset_experiments()
        self.update_current_stiffness_label()
        self.refresh_stiffness_buttons()
        self.draw_scene()

    def reset_experiments(self):
        self.experiments.clear()
        self.current_weight_count = 0
        self.show_weights = False
        self.current_stretch = 0
        self.target_stretch = 0

        self.weights_entry.delete(0, tk.END)
        self.weights_entry.insert(0, "0")
        self.update_info_label()

        self.init_table()
        self.draw_empty_graph()
        self.interval_label.config(text=self.get_interval_placeholder_text())

    def get_interval_placeholder_text(self):
        return (
            "Доверительный интервал для k:\n"
            "Появится после проведения всех 5 испытаний и построения графика.\n\n"
            "Результат: k = kср ± Δkср"
        )

    def update_info_label(self):
        version = self.active_spring_version
        length_cm = version.l0_cm + (self.current_weight_count * version.cm_per_weight)
        self.info_label.config(
            text=(
                f"Грузов: {self.current_weight_count} | "
                f"Длина пружины: {length_cm:.1f} см"
            )
        )

    def init_table(self):
        self.table.delete(*self.table.get_children())

        for i in range(0, self.max_weights + 1):
            if i == 0:
                values = (
                    0,
                    "0",
                    "0",
                    f"{self.active_spring_version.l0_cm / 100:.3f}",
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
        x_cm = count * self.active_spring_version.cm_per_weight
        x_m = x_cm / 100

        # Полная длина пружины
        l_cm = self.active_spring_version.l0_cm + x_cm
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

        x_min, x_max = self.get_length_axis_limits()
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(0, 4.2)

        self.ax.grid(True)

        self.graph_canvas.draw()

    def get_length_axis_limits(self):
        version = self.active_spring_version
        min_l = version.l0_cm / 100
        max_l = (version.l0_cm + self.max_weights * version.cm_per_weight) / 100
        padding = max(0.001, (max_l - min_l) * 0.15)

        return min_l - padding, max_l + padding

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
        self.ax.set_xlim(*self.get_length_axis_limits())

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
        self.canvas.delete("all")

        version = self.active_spring_version
        spring_height = version.spring_start_height + self.current_stretch
        spring_bottom_y = self.spring_y + spring_height
        spring_x = self.spring_x + version.spring_x_offset
        hook_x = self.hook_x + version.hook_x_offset
        weight_x = self.weight_x + version.weight_x_offset

        self.clamp_img = self.load_image(
            self.get_clamp_path(version),
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
            width=version.spring_width,
            height=spring_height
        )

        self.canvas.create_image(
            spring_x,
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
            hook_x,
            spring_bottom_y + version.hook_y_offset,
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
                    weight_x,
                    spring_bottom_y + version.weight_y_offset + (i * self.weight_spacing),
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

        self.target_stretch = int(
            round(count * self.active_spring_version.stretch_per_weight_px)
        )

        self.update_experiment_table(count)

        self.animate_spring()

    def animate_spring(self):
        if self.current_stretch < self.target_stretch:
            self.current_stretch += 1

        elif self.current_stretch > self.target_stretch:
            self.current_stretch -= 1

        else:
            self.update_info_label()
            return

        self.draw_scene()

        self.update_info_label()

        self.root.after(10, self.animate_spring)


if __name__ == "__main__":
    root = tk.Tk()
    app = SpringApp(root)
    root.mainloop()
