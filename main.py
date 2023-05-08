import simpy
import tkinter as tk


class JuiceDispenser:
    def __init__(self, env, master):
        self.env = env
        self.master = master
        master.title("Vending Machine")
        self.canvas = tk.Canvas(master, width=700, height=300, bg="red")
        self.canvas.pack(side="left", padx=150, pady=150)

        self.juice_rectangles = []
        JUICE_COLORS = {
            "Fanta": "orange",
            "Coke": "black",
            "Sprite": "green",
            "Pepsi": "blue"
        }
        for i, (name, color) in enumerate(JUICE_COLORS.items()):
            x1, y1, x2, y2 = 50 + 150 * i, 120, 150 + 150 * i, 220
            juice_rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
            self.juice_rectangles.append(juice_rect)

        self.juice_containers = []
        self.juice_labels = []
        for i, (name, color) in enumerate(JUICE_COLORS.items()):
            juice_container = simpy.Container(env, init=100, capacity=150)
            self.juice_containers.append(juice_container)
            button = tk.Button(master, text=f"Dispense {name}", command=lambda index=i: self.dispense_juice(index))
            button.pack(side="top", padx=10, pady=5)
            refill_button = tk.Button(master, text=f"Refill {name}", command=lambda index=i: self.refill_juice(index))
            refill_button.pack(side="top", padx=10, pady=5)
            juice_label = tk.Label(master, text=f"Level: 100%", font=("Arial", 10))
            juice_label.pack(side="top", padx=10, pady=5)
            self.juice_labels.append(juice_label)

        self.profit = 0  # Track the profit
        self.profit_label = tk.Label(master, text="Money: $0", font=("Arial", 12, "bold"))
        self.profit_label.pack(side="bottom", pady=10)

        self.process = env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(0.1)

    def dispense_juice(self, index):
        container = self.juice_containers[index]
        if container.level >= 10:
            container.get(10)
            self.update_juice_rect(index)
            self.profit += 40  # Increase profit by 30 (charging 30 rupees per dispense)
            self.update_profit_label()

    def refill_juice(self, index):
        container = self.juice_containers[index]
        if container.level < container.capacity:
            space_available = container.capacity - container.level
            amount_to_refill = min(space_available, 10)  # Refill 10% at a time
            container.put(amount_to_refill)
            self.update_juice_rect(index)
            self.profit -= 25  # Decrease profit by 25 (charging 25 rupees per 10% refill)
            self.update_profit_label()

    def update_juice_rect(self, index):
        container = self.juice_containers[index]
        juice_rect = self.juice_rectangles[index]
        x1, y1, x2, y2 = self.canvas.coords(juice_rect)
        y1 = 220 - container.level
        self.canvas.coords(juice_rect, x1, y1, x2, y2)
        percentage = int((container.level / container.capacity) * 100)
        level_text = f"Level: {percentage}%"
        self.juice_labels[index].config(text=level_text)

        if container.level == 0:
            # If the juice container is empty, disable the dispense button
            dispense_button = self.master.winfo_children()[index * 2]
            dispense_button.config(state="disabled")

        if container.level >= 10:
            # If the juice container is refilled, enable the dispense button
            dispense_button = self.master.winfo_children()[index * 2]
            dispense_button.config(state="normal")

    def update_profit_label(self):
        self.profit_label.config(text=f"Money: ${self.profit}")

env = simpy.Environment()
root = tk.Tk()
app = JuiceDispenser(env, root)
root.mainloop()
