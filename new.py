import pygame
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess  # For opening the folder

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Virtual Snap Gauge Simulator")

# Colors
WHITE = (255, 255, 255)
GRAY = (169, 169, 169)
BLUE = (30, 144, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# Font
font = pygame.font.Font(None, 24)

# Snap Gauge Parameters
gauge_x, gauge_y, gauge_width, gauge_height = 350, 250, 200, 50
nominal_diameter = 50
Tolerance = 0.5
UCL = nominal_diameter + Tolerance
LCL = nominal_diameter - Tolerance

# Load Snap Gauge Image
image_path = "snap_gauge_image.jpeg"
snap_gauge_image = pygame.image.load(image_path)
snap_gauge_image = pygame.transform.scale(snap_gauge_image, (120, 120))

# Sphere Class
class Sphere:
    def __init__(self, x, y, diameter):
        self.x = x
        self.y = y
        self.diameter = diameter
        self.radius = diameter / 2
        self.selected = False

    def draw(self):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), int(self.radius))
        text = font.render(f"{self.diameter:.2f} mm", True, WHITE)
        screen.blit(text, (self.x - self.radius, self.y + self.radius + 5))

    def is_clicked(self, pos):
        return (self.x - pos[0])**2 + (self.y - pos[1])**2 < self.radius**2

    def move(self, pos):
        self.x, self.y = pos

# Generate 15 Spheres placed at the bottom-right without overlapping
spheres = []
sphere_diameter = 50
padding = 35  # Increased padding
cols = 5
start_x = WIDTH - (cols * (sphere_diameter + padding)) - 20
start_y = HEIGHT - sphere_diameter - padding

for i in range(15):
    col = i % cols
    row = i // cols
    x = start_x + col * (sphere_diameter + padding)
    y = start_y - row * (sphere_diameter + padding)
    spheres.append(Sphere(x, y, round(random.uniform(49.3, 50.7), 2)))

# Results storage
batches = []
current_batch = []
selected_sphere = None

# Quality check
def check_quality(d):
    return "Go" if LCL <= d <= UCL else "No Go"

def plot_p_chart():
    if not batches:
        return

    batch_sizes = [len(batch) for batch in batches]
    defective_counts = [sum(1 for res in batch if res[1] == "No Go") for batch in batches]
    proportions = [defective / size for defective, size in zip(defective_counts, batch_sizes)]

    avg_p = np.mean(proportions)
    ucl = avg_p + 3 * np.sqrt((avg_p * (1 - avg_p)) / np.mean(batch_sizes))
    lcl = max(0, avg_p - 3 * np.sqrt((avg_p * (1 - avg_p)) / np.mean(batch_sizes)))

    plt.figure(figsize=(10, 5))
    plt.plot(proportions, marker='o', linestyle='-', color='blue', label="P Chart")
    plt.axhline(y=avg_p, color='r', linestyle='dashed', label="Central Line (CL)")
    plt.axhline(y=ucl, color='g', linestyle='dashed', label="UCL")
    plt.axhline(y=lcl, color='g', linestyle='dashed', label="LCL")

    max_defects = max(defective_counts)
    for i, count in enumerate(defective_counts):
        if count == max_defects:
            plt.annotate(f"Most Defectives: {count}", (i, proportions[i]), textcoords="offset points", xytext=(0,10), ha='center', color='red')

    plt.title("P-Chart (Defective Proportion per Batch)")
    plt.xlabel("Batch Number")
    plt.ylabel("Defective Proportion")
    plt.legend()
    plt.grid()
    plt.show()

# Main loop
running = True
while running:
    screen.fill(BLACK)

    # Draw Snap Gauge
    pygame.draw.rect(screen, GRAY, (gauge_x, gauge_y, gauge_width, gauge_height), 3)
    gauge_label = font.render(f"Snap Gauge: {nominal_diameter}mm ± {Tolerance}mm", True, WHITE)
    screen.blit(gauge_label, (gauge_x - 40, gauge_y - 30))

    # Draw Snap Gauge image and label
    screen.blit(snap_gauge_image, (30, 400))
    label = font.render("Snap Gauge", True, WHITE)
    screen.blit(label, (50, 525))

    # Draw spheres
    for sphere in spheres:
        sphere.draw()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if selected_sphere is None:
                for sphere in spheres:
                    if sphere.is_clicked(pos):
                        selected_sphere = sphere
                        break
            else:
                selected_sphere.move(pos)
                result = check_quality(selected_sphere.diameter)
                current_batch.append((selected_sphere.diameter, result))
                spheres.remove(selected_sphere)
                selected_sphere = None

    # Show live results
    y_offset = 10
    for i, (d, r) in enumerate(current_batch[-5:]):
        text = font.render(f"Sphere {i+1}: {d} mm -> {r}", True, GREEN if r == "Go" else RED)
        screen.blit(text, (650, y_offset))
        y_offset += 25

    pygame.display.flip()

    if len(current_batch) == 5:
        batches.append(current_batch[:])
        current_batch.clear()

    if len(batches) == 3:
        plot_p_chart()

        df = pd.DataFrame(
            [(i + 1, sphere[0], sphere[1]) for i, batch in enumerate(batches) for sphere in batch],
            columns=["Batch", "Diameter (mm)", "Result"]
        )

        os.makedirs("results", exist_ok=True)
        excel_path = "results/snap_gauge_results.xlsx"
        csv_path = "results/snap_gauge_results.csv"
        df.to_excel(excel_path, index=False)
        df.to_csv(csv_path, index=False)

        # Use Windows command to open folder
        subprocess.run(["explorer", os.path.realpath("results")])

        print("Results saved successfully in both Excel and CSV format.")
        running = False

pygame.quit()
