"""
PROJECT OPTION 1: Advanced Predator-Prey Simulation
Author: Alexandru CL
Date: November 23, 2025

Features:
- Reproduction mechanics for prey and predators
- Energy system with depletion and consumption
- Food resources that prey can eat
- Flocking behavior (cohesion, alignment, separation)
- Obstacles that agents navigate around
- Population tracking with real-time graphs
- Interactive controls for parameter adjustment

Controls:
- P: Add prey manually
- O: Add predator manually
- F: Add food resource
- B: Add obstacle (click to place)
- UP/DOWN: Adjust reproduction rate
- LEFT/RIGHT: Adjust energy consumption rate
- SPACE: Toggle flocking behavior
- ESC: Exit simulation
"""

import pygame
import random
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
GRAPH_WIDTH = 400

# Colors
BACKGROUND_COLOR = (25, 25, 40)
PREY_COLOR = (100, 200, 100)
PREDATOR_COLOR = (200, 100, 100)
FOOD_COLOR = (255, 200, 50)
OBSTACLE_COLOR = (100, 100, 120)
TEXT_COLOR = (200, 200, 200)
ENERGY_BAR_BG = (50, 50, 50)
ENERGY_BAR_FG = (0, 255, 0)

# Simulation parameters
FPS = 60
INITIAL_PREY = 30
INITIAL_PREDATORS = 5
INITIAL_FOOD = 20

# Energy parameters
PREY_ENERGY_LOSS = 0.1
PREDATOR_ENERGY_LOSS = 0.15
FOOD_ENERGY_GAIN = 50
PREY_CONSUMPTION_GAIN = 80
REPRODUCTION_ENERGY_THRESHOLD = 150
REPRODUCTION_ENERGY_COST = 100
MATING_DISTANCE = 20
MATING_TIME = 60  # frames

# Flocking parameters
COHESION_RADIUS = 50
ALIGNMENT_RADIUS = 40
SEPARATION_RADIUS = 25
COHESION_WEIGHT = 0.5
ALIGNMENT_WEIGHT = 0.8
SEPARATION_WEIGHT = 1.2

# Initialize screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Predator-Prey Simulation")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 20)
TITLE_FONT = pygame.font.SysFont(None, 24)


class Food:
    """Represents a food resource in the environment."""
    def __init__(self, position=None):
        if position:
            self.position = pygame.math.Vector2(position)
        else:
            self.position = pygame.math.Vector2(
                random.uniform(20, WIDTH - GRAPH_WIDTH - 20),
                random.uniform(20, HEIGHT - 20)
            )
        self.energy = FOOD_ENERGY_GAIN
        self.radius = 5

    def draw(self):
        pygame.draw.circle(screen, FOOD_COLOR, 
                         (int(self.position.x), int(self.position.y)), self.radius)


class Obstacle:
    """Represents a static obstacle in the environment."""
    def __init__(self, position, width=60, height=60):
        self.position = pygame.math.Vector2(position)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(position[0] - width//2, position[1] - height//2, width, height)

    def draw(self):
        pygame.draw.rect(screen, OBSTACLE_COLOR, self.rect)
        pygame.draw.rect(screen, (150, 150, 170), self.rect, 2)


class Agent:
    """Base class for all agents in the simulation."""
    def __init__(self, position=None, speed=2, color=PREY_COLOR, energy=100):
        if position:
            self.position = pygame.math.Vector2(position)
        else:
            self.position = pygame.math.Vector2(
                random.uniform(50, WIDTH - GRAPH_WIDTH - 50),
                random.uniform(50, HEIGHT - 50)
            )
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.speed = speed
        self.base_speed = speed
        self.color = color
        self.energy = energy
        self.max_energy = 200
        self.trail = []
        self.max_trail_length = 15
        self.mating_timer = 0

    def update_position(self, obstacles):
        """Update agent position and handle wall/obstacle collision."""
        # Avoid obstacles
        avoidance = self.avoid_obstacles(obstacles)
        if avoidance.length() > 0:
            self.velocity = (self.velocity + avoidance * 2).normalize()
        
        self.position += self.velocity * self.speed
        self._bounce_off_walls()
        self._update_trail()

    def avoid_obstacles(self, obstacles):
        """Calculate avoidance vector for nearby obstacles."""
        avoidance = pygame.math.Vector2(0, 0)
        for obstacle in obstacles:
            # Check distance to obstacle center
            to_obstacle = obstacle.position - self.position
            distance = to_obstacle.length()
            
            if distance < 80:  # Detection radius
                # Simple avoidance - move away from obstacle
                if distance > 0:
                    avoidance -= to_obstacle.normalize() / (distance + 1)
        
        return avoidance

    def _bounce_off_walls(self):
        """Bounce off screen edges."""
        if self.position.x < 10 or self.position.x > WIDTH - GRAPH_WIDTH - 10:
            self.velocity.x *= -1
        if self.position.y < 10 or self.position.y > HEIGHT - 10:
            self.velocity.y *= -1
        
        self.position.x = max(10, min(self.position.x, WIDTH - GRAPH_WIDTH - 10))
        self.position.y = max(10, min(self.position.y, HEIGHT - 10))

    def _update_trail(self):
        """Update movement trail for visualization."""
        self.trail.append(self.position.copy())
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    def draw_trail(self):
        """Draw the movement trail."""
        if len(self.trail) > 1:
            pygame.draw.lines(screen, self.color, False, 
                            [(int(p.x), int(p.y)) for p in self.trail], 1)

    def draw_energy_bar(self):
        """Draw energy bar above agent."""
        bar_width = 20
        bar_height = 3
        x = int(self.position.x - bar_width // 2)
        y = int(self.position.y - 15)
        
        # Background
        pygame.draw.rect(screen, ENERGY_BAR_BG, (x, y, bar_width, bar_height))
        
        # Foreground (energy level)
        energy_ratio = max(0, min(1, self.energy / self.max_energy))
        energy_width = int(bar_width * energy_ratio)
        
        # Color based on energy level
        if energy_ratio > 0.6:
            color = (0, 255, 0)
        elif energy_ratio > 0.3:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        
        pygame.draw.rect(screen, color, (x, y, energy_width, bar_height))


class Prey(Agent):
    """Prey agent with fleeing, eating, flocking, and reproduction behaviors."""
    def __init__(self, position=None):
        super().__init__(position=position, speed=2.5, color=PREY_COLOR, energy=100)
        self.vision_radius = 60
        self.hunger_threshold = 80

    def update(self, predators, other_prey, food_list, obstacles, flocking_enabled, energy_loss_rate):
        """Update prey state."""
        # Lose energy over time
        self.energy -= PREY_ENERGY_LOSS * energy_loss_rate
        
        # Update mating timer
        if self.mating_timer > 0:
            self.mating_timer -= 1
            return  # Don't move while mating
        
        # Behavior priorities
        flee_vector = self.flee_from_predators(predators)
        
        # Seek food if hungry
        if self.energy < self.hunger_threshold:
            food_vector = self.seek_food(food_list)
        else:
            food_vector = pygame.math.Vector2(0, 0)
        
        # Flocking behavior
        if flocking_enabled and flee_vector.length() == 0:
            flock_vector = self.flock(other_prey)
            # Speed boost based on nearby flock members
            nearby = sum(1 for p in other_prey 
                        if p != self and self.position.distance_to(p.position) < COHESION_RADIUS)
            self.speed = self.base_speed + min(nearby * 0.1, 1.0)
        else:
            flock_vector = pygame.math.Vector2(0, 0)
            self.speed = self.base_speed
        
        # Combine behaviors
        if flee_vector.length() > 0:
            self.velocity = flee_vector.normalize()
        elif food_vector.length() > 0:
            self.velocity = (self.velocity * 0.5 + food_vector.normalize() * 0.5).normalize()
        elif flock_vector.length() > 0:
            self.velocity = (self.velocity * 0.7 + flock_vector.normalize() * 0.3).normalize()
        
        self.update_position(obstacles)

    def flee_from_predators(self, predators):
        """Calculate flee vector from nearby predators."""
        flee = pygame.math.Vector2(0, 0)
        for predator in predators:
            distance = self.position.distance_to(predator.position)
            if distance < self.vision_radius and distance > 0:
                flee_dir = (self.position - predator.position).normalize()
                flee += flee_dir / distance  # Stronger when closer
        return flee

    def seek_food(self, food_list):
        """Move towards nearest food."""
        if not food_list:
            return pygame.math.Vector2(0, 0)
        
        nearest_food = min(food_list, 
                          key=lambda f: self.position.distance_to(f.position))
        distance = self.position.distance_to(nearest_food.position)
        
        if distance < 100:  # Only seek if within range
            return (nearest_food.position - self.position).normalize()
        return pygame.math.Vector2(0, 0)

    def flock(self, other_prey):
        """Calculate flocking behavior (cohesion, alignment, separation)."""
        cohesion = pygame.math.Vector2(0, 0)
        alignment = pygame.math.Vector2(0, 0)
        separation = pygame.math.Vector2(0, 0)
        
        cohesion_count = 0
        alignment_count = 0
        separation_count = 0
        
        for other in other_prey:
            if other == self:
                continue
            
            distance = self.position.distance_to(other.position)
            
            # Cohesion - steer towards center of nearby flock
            if distance < COHESION_RADIUS:
                cohesion += other.position
                cohesion_count += 1
            
            # Alignment - align velocity with nearby flock
            if distance < ALIGNMENT_RADIUS:
                alignment += other.velocity
                alignment_count += 1
            
            # Separation - avoid crowding
            if distance < SEPARATION_RADIUS and distance > 0:
                separation += (self.position - other.position) / distance
                separation_count += 1
        
        # Calculate averages
        if cohesion_count > 0:
            cohesion = (cohesion / cohesion_count - self.position) * COHESION_WEIGHT
        if alignment_count > 0:
            alignment = (alignment / alignment_count) * ALIGNMENT_WEIGHT
        if separation_count > 0:
            separation = (separation / separation_count) * SEPARATION_WEIGHT
        
        return cohesion + alignment + separation

    def eat_food(self, food_list):
        """Check if prey can eat nearby food."""
        for food in food_list[:]:
            if self.position.distance_to(food.position) < 10:
                self.energy = min(self.max_energy, self.energy + food.energy)
                food_list.remove(food)
                return True
        return False

    def can_reproduce(self):
        """Check if prey has enough energy to reproduce."""
        return self.energy >= REPRODUCTION_ENERGY_THRESHOLD and self.mating_timer == 0

    def draw(self):
        """Draw prey as a circle with trail and energy bar."""
        self.draw_trail()
        pygame.draw.circle(screen, self.color, 
                         (int(self.position.x), int(self.position.y)), 5)
        self.draw_energy_bar()


class Predator(Agent):
    """Predator agent with hunting and reproduction behaviors."""
    def __init__(self, position=None):
        super().__init__(position=position, speed=2.8, color=PREDATOR_COLOR, energy=120)
        self.hunt_radius = 150

    def update(self, prey_list, obstacles, energy_loss_rate):
        """Update predator state."""
        # Lose energy over time
        self.energy -= PREDATOR_ENERGY_LOSS * energy_loss_rate
        
        # Update mating timer
        if self.mating_timer > 0:
            self.mating_timer -= 1
            return  # Don't move while mating
        
        # Hunt nearest prey
        if prey_list:
            nearest_prey = min(prey_list, 
                             key=lambda p: self.position.distance_to(p.position))
            distance = self.position.distance_to(nearest_prey.position)
            
            if distance < self.hunt_radius:
                direction = (nearest_prey.position - self.position).normalize()
                self.velocity = direction
        
        self.update_position(obstacles)

    def catch_prey(self, prey_list):
        """Check if predator caught any prey."""
        for prey in prey_list[:]:
            if self.position.distance_to(prey.position) < 8:
                self.energy = min(self.max_energy, self.energy + PREY_CONSUMPTION_GAIN)
                prey_list.remove(prey)
                return True
        return False

    def can_reproduce(self):
        """Check if predator has enough energy to reproduce."""
        return self.energy >= REPRODUCTION_ENERGY_THRESHOLD and self.mating_timer == 0

    def draw(self):
        """Draw predator as a triangle with trail and energy bar."""
        self.draw_trail()
        
        # Calculate rotation angle
        angle = self.velocity.angle_to(pygame.math.Vector2(1, 0))
        
        # Triangle points
        points = [
            pygame.math.Vector2(12, 0),
            pygame.math.Vector2(-6, -6),
            pygame.math.Vector2(-6, 6)
        ]
        
        # Rotate and translate
        rotated = [self.position + p.rotate(-angle) for p in points]
        pygame.draw.polygon(screen, self.color, rotated)
        
        self.draw_energy_bar()


class PopulationTracker:
    """Tracks and visualizes population statistics."""
    def __init__(self, max_history=300):
        self.max_history = max_history
        self.time_steps = []
        self.prey_counts = []
        self.predator_counts = []
        self.prey_births = []
        self.predator_births = []
        self.current_time = 0
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(5, 6))
        self.fig.patch.set_facecolor('#1a1a28')
        self.canvas = FigureCanvasAgg(self.fig)
        self.cached_surface = None
        self.needs_redraw = False

    def update(self, prey_count, predator_count, prey_birth_rate=0, predator_birth_rate=0):
        """Update population data."""
        self.current_time += 1
        self.time_steps.append(self.current_time)
        self.prey_counts.append(prey_count)
        self.predator_counts.append(predator_count)
        self.prey_births.append(prey_birth_rate)
        self.predator_births.append(predator_birth_rate)
        
        # Keep only recent history
        if len(self.time_steps) > self.max_history:
            self.time_steps.pop(0)
            self.prey_counts.pop(0)
            self.predator_counts.pop(0)
            self.prey_births.pop(0)
            self.predator_births.pop(0)
            
        self.needs_redraw = True

    def draw(self, screen, x_offset, y_offset):
        """Draw population graphs."""
        if len(self.time_steps) < 2:
            return
            
        if self.needs_redraw or self.cached_surface is None:
            # Clear axes
            self.ax1.clear()
            self.ax2.clear()
            
            # Style configuration
            for ax in [self.ax1, self.ax2]:
                ax.set_facecolor('#2a2a38')
                ax.tick_params(colors='white', labelsize=8)
                ax.spines['bottom'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
            
            # Population graph
            # Normalize colors for matplotlib (0-255 -> 0-1)
            prey_color_norm = tuple(c/255 for c in PREY_COLOR)
            predator_color_norm = tuple(c/255 for c in PREDATOR_COLOR)
            
            self.ax1.plot(self.time_steps, self.prey_counts, 
                         color=prey_color_norm, label='Prey', linewidth=2)
            self.ax1.plot(self.time_steps, self.predator_counts, 
                         color=predator_color_norm, label='Predators', linewidth=2)
            self.ax1.set_ylabel('Population', color='white', fontsize=9)
            self.ax1.set_title('Population Over Time', color='white', fontsize=10)
            self.ax1.legend(loc='upper right', fontsize=8, facecolor='#2a2a38', 
                           edgecolor='white', labelcolor='white')
            self.ax1.grid(True, alpha=0.2, color='white')
            
            # Birth rates graph
            self.ax2.plot(self.time_steps, self.prey_births, 
                         color=prey_color_norm, label='Prey Births', linewidth=2)
            self.ax2.plot(self.time_steps, self.predator_births, 
                         color=predator_color_norm, label='Predator Births', linewidth=2)
            self.ax2.set_xlabel('Time', color='white', fontsize=9)
            self.ax2.set_ylabel('Birth Rate', color='white', fontsize=9)
            self.ax2.set_title('Birth Rates Over Time', color='white', fontsize=10)
            self.ax2.legend(loc='upper right', fontsize=8, facecolor='#2a2a38', 
                           edgecolor='white', labelcolor='white')
            self.ax2.grid(True, alpha=0.2, color='white')
            
            # Render to surface
            self.canvas.draw()
            raw_data = self.canvas.buffer_rgba()
            size = self.canvas.get_width_height()
            
            self.cached_surface = pygame.image.frombuffer(raw_data, size, "RGBA")
            self.needs_redraw = False
        
        if self.cached_surface:
            screen.blit(self.cached_surface, (x_offset, y_offset))


class Simulation:
    """Main simulation manager."""
    def __init__(self):
        self.prey_list = [Prey() for _ in range(INITIAL_PREY)]
        self.predator_list = [Predator() for _ in range(INITIAL_PREDATORS)]
        self.food_list = [Food() for _ in range(INITIAL_FOOD)]
        self.obstacles = []
        
        self.running = True
        self.flocking_enabled = True
        self.reproduction_rate = 1.0
        self.energy_consumption_rate = 1.0
        
        self.tracker = PopulationTracker()
        self.frame_count = 0
        
        self.prey_birth_counter = 0
        self.predator_birth_counter = 0
        
        # Add some initial obstacles
        self.obstacles.append(Obstacle((200, 200)))
        self.obstacles.append(Obstacle((500, 400)))
        self.obstacles.append(Obstacle((300, 600)))

    def run(self):
        """Main simulation loop."""
        while self.running:
            clock.tick(FPS)
            self.handle_events()
            self.update()
            self.render()
        
        pygame.quit()

    def handle_events(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.prey_list.append(Prey())
                elif event.key == pygame.K_o:
                    self.predator_list.append(Predator())
                elif event.key == pygame.K_f:
                    self.food_list.append(Food())
                elif event.key == pygame.K_b:
                    # Add obstacle at random location
                    pos = (random.uniform(100, WIDTH - GRAPH_WIDTH - 100),
                          random.uniform(100, HEIGHT - 100))
                    self.obstacles.append(Obstacle(pos))
                elif event.key == pygame.K_SPACE:
                    self.flocking_enabled = not self.flocking_enabled
                elif event.key == pygame.K_UP:
                    self.reproduction_rate = min(2.0, self.reproduction_rate + 0.1)
                elif event.key == pygame.K_DOWN:
                    self.reproduction_rate = max(0.1, self.reproduction_rate - 0.1)
                elif event.key == pygame.K_RIGHT:
                    self.energy_consumption_rate = min(2.0, self.energy_consumption_rate + 0.1)
                elif event.key == pygame.K_LEFT:
                    self.energy_consumption_rate = max(0.1, self.energy_consumption_rate - 0.1)

    def update(self):
        """Update simulation state."""
        self.frame_count += 1
        self.prey_birth_counter = 0
        self.predator_birth_counter = 0
        
        # Update prey
        for prey in self.prey_list[:]:
            prey.update(self.predator_list, self.prey_list, self.food_list, 
                       self.obstacles, self.flocking_enabled, self.energy_consumption_rate)
            prey.eat_food(self.food_list)
            
            # Remove if dead
            if prey.energy <= 0:
                self.prey_list.remove(prey)
        
        # Update predators
        for predator in self.predator_list[:]:
            predator.update(self.prey_list, self.obstacles, self.energy_consumption_rate)
            predator.catch_prey(self.prey_list)
            
            # Remove if dead
            if predator.energy <= 0:
                self.predator_list.remove(predator)
        
        # Handle reproduction
        self.handle_reproduction()
        
        # Randomly spawn food
        if random.random() < 0.02 and len(self.food_list) < 50:
            self.food_list.append(Food())
        
        # Update tracker every 10 frames
        if self.frame_count % 10 == 0:
            self.tracker.update(len(self.prey_list), len(self.predator_list),
                              self.prey_birth_counter, self.predator_birth_counter)

    def handle_reproduction(self):
        """Handle reproduction for prey and predators."""
        # Prey reproduction
        for i, prey1 in enumerate(self.prey_list):
            if not prey1.can_reproduce():
                continue
            
            for prey2 in self.prey_list[i+1:]:
                if not prey2.can_reproduce():
                    continue
                
                distance = prey1.position.distance_to(prey2.position)
                if distance < MATING_DISTANCE:
                    # Reproduction influenced by rate
                    if random.random() < 0.02 * self.reproduction_rate:
                        # Create offspring
                        offspring_pos = (prey1.position + prey2.position) / 2
                        self.prey_list.append(Prey(position=offspring_pos))
                        
                        # Consume energy
                        prey1.energy -= REPRODUCTION_ENERGY_COST
                        prey2.energy -= REPRODUCTION_ENERGY_COST
                        
                        # Start mating timer
                        prey1.mating_timer = MATING_TIME
                        prey2.mating_timer = MATING_TIME
                        
                        self.prey_birth_counter += 1
                        break
        
        # Predator reproduction
        for i, pred1 in enumerate(self.predator_list):
            if not pred1.can_reproduce():
                continue
            
            for pred2 in self.predator_list[i+1:]:
                if not pred2.can_reproduce():
                    continue
                
                distance = pred1.position.distance_to(pred2.position)
                if distance < MATING_DISTANCE:
                    # Reproduction influenced by rate
                    if random.random() < 0.015 * self.reproduction_rate:
                        # Create offspring
                        offspring_pos = (pred1.position + pred2.position) / 2
                        self.predator_list.append(Predator(position=offspring_pos))
                        
                        # Consume energy
                        pred1.energy -= REPRODUCTION_ENERGY_COST
                        pred2.energy -= REPRODUCTION_ENERGY_COST
                        
                        # Start mating timer
                        pred1.mating_timer = MATING_TIME
                        pred2.mating_timer = MATING_TIME
                        
                        self.predator_birth_counter += 1
                        break

    def render(self):
        """Render all simulation elements."""
        screen.fill(BACKGROUND_COLOR)
        
        # Draw main simulation area separator
        pygame.draw.line(screen, TEXT_COLOR, 
                        (WIDTH - GRAPH_WIDTH, 0), (WIDTH - GRAPH_WIDTH, HEIGHT), 2)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw()
        
        # Draw food
        for food in self.food_list:
            food.draw()
        
        # Draw agents
        for prey in self.prey_list:
            prey.draw()
        
        for predator in self.predator_list:
            predator.draw()
        
        # Draw UI
        self.draw_ui()
        
        # Draw graphs
        self.tracker.draw(screen, WIDTH - GRAPH_WIDTH + 10, 100)
        
        pygame.display.flip()

    def draw_ui(self):
        """Draw user interface elements."""
        y_offset = 10
        line_height = 22
        
        # Title
        title = TITLE_FONT.render("ADVANCED PREDATOR-PREY SIMULATION", True, TEXT_COLOR)
        screen.blit(title, (10, y_offset))
        y_offset += line_height + 5
        
        # Statistics
        stats = [
            f"Prey: {len(self.prey_list)}",
            f"Predators: {len(self.predator_list)}",
            f"Food: {len(self.food_list)}",
            f"Obstacles: {len(self.obstacles)}",
        ]
        
        for stat in stats:
            text = FONT.render(stat, True, TEXT_COLOR)
            screen.blit(text, (10, y_offset))
            y_offset += line_height
        
        y_offset += 10
        
        # Parameters
        params = [
            f"Flocking: {'ON' if self.flocking_enabled else 'OFF'} (SPACE)",
            f"Reproduction Rate: {self.reproduction_rate:.1f}x (UP/DOWN)",
            f"Energy Consumption: {self.energy_consumption_rate:.1f}x (LEFT/RIGHT)",
        ]
        
        for param in params:
            text = FONT.render(param, True, (150, 200, 255))
            screen.blit(text, (10, y_offset))
            y_offset += line_height
        
        y_offset += 10
        
        # Controls
        controls = [
            "Controls:",
            "P - Add Prey",
            "O - Add Predator",
            "F - Add Food",
            "B - Add Obstacle",
            "ESC - Exit",
        ]
        
        for control in controls:
            text = FONT.render(control, True, (200, 200, 150))
            screen.blit(text, (10, y_offset))
            y_offset += line_height


if __name__ == "__main__":
    print("Starting Advanced Predator-Prey Simulation...")
    print("\nObjective: Achieve a stable ecosystem where both species coexist!")
    print("Tip: Balance reproduction rate and energy consumption for stability.\n")
    
    simulation = Simulation()
    simulation.run()
