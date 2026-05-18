import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk


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
        # 1 см = 19 px берем 20 из за размера изображения
        self.pixels_per_cm = 22
        # Один груз растягивает на 0.2 см
        self.cm_per_weight = 0.2

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
        main_frame = tk.Frame(self.root, bg="#f3f3f3")
        main_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(main_frame, width=800)
        self.left_frame.pack(side="left", fill="both")

        self.right_frame = tk.Frame(main_frame, bg="#ffffff")
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
            font=("Arial", 12),
            bg="white"
        ).grid(row=0, column=0, padx=5)

        self.weights_entry = tk.Entry(
            control_frame,
            width=10,
            font=("Arial", 12)
        )
        self.weights_entry.insert(0, "0")
        self.weights_entry.grid(row=0, column=1, padx=5)

        tk.Button(
            control_frame,
            text="Принять",
            font=("Arial", 12),
            command=self.accept_weights
        ).grid(row=0, column=2, padx=5)

        self.info_label = tk.Label(
            self.left_frame,
            text="Грузов: 0 | Длина пружины: 5.6 см",
            font=("Arial", 12),
            bg="white"
        )
        self.info_label.pack(pady=5)

        tk.Label(
            self.right_frame,
            text="Таблица расчётов",
            font=("Arial", 18, "bold"),
            bg="#ffffff"
        ).pack(pady=20)

        self.table_placeholder = tk.Label(
            self.right_frame,
            text="Здесь будут данные опытов:\nмасса, сила, длина, удлинение, k",
            font=("Arial", 12),
            bg="#ffffff",
            justify="left"
        )
        self.table_placeholder.pack(anchor="nw", padx=30)

    def draw_scene(self):
        self.canvas.delete("all")

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
                "Введите число от 0 до 5"
            )
            return

        self.current_weight_count = count
        self.show_weights = True

        stretch_cm = count * self.cm_per_weight

        self.target_stretch = int(
            stretch_cm * self.pixels_per_cm
        )
        self.animate_spring()

    def animate_spring(self):
        if self.current_stretch < self.target_stretch:
            self.current_stretch += 1

        elif self.current_stretch > self.target_stretch:
            self.current_stretch -= 1

        else:
            self.info_label.config(
                text=f"Грузов: {self.current_weight_count} | Длина пружины: {round((self.current_stretch/22)+5.6, 1 )} см"
            )
            return

        self.draw_scene()

        self.info_label.config(
            text=f"Грузов: {self.current_weight_count} | Длина пружины: {round((self.current_stretch/22)+5.6, 1 )} см"
        )

        self.root.after(10, self.animate_spring)


if __name__ == "__main__":
    root = tk.Tk()
    app = SpringApp(root)
    root.mainloop()