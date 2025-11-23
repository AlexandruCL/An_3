"""
Advanced Predator-Prey Simulation
Project 1: Bonus Points Implementation

Features:
- Energy system for both predators and prey
- Reproduction mechanics with energy requirements
- Food resources for prey
- Flocking behavior (boids-like)
- Obstacle avoidance
- Population and birth rate tracking with graphs
- Interactive controls for simulation parameters
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
WIDTH, HEIGHT = 1200, 700
GRAPH_WIDTH = 350
SIMULATION_WIDTH = WIDTH - GRAPH_WIDTH - 50

# Colors
BACKGROUND_COLOR = (25, 25, 40)
PREY_COLOR = (100, 200, 100)
PREDATOR_COLOR = (200, 100, 100)
FOOD_COLOR = (255, 200, 50)
OBSTACLE_COLOR = (80, 80, 100)
TEXT_COLOR = (200, 200, 200)
GRAPH_BG = (40, 40, 55)

# Simulation parameters
FPS = 60
PREY_ENERGY_START = 100
PREY_ENERGY_LOSS = 0.1
PREY_ENERGY_FROM_FOOD = 30
PREY_REPRODUCE_THRESHOLD = 80
PREY_REPRODUCE_COST = 40

PREDATOR_ENERGY_START = 150
PREDATOR_ENERGY_LOSS = 0.15
PREDATOR_ENERGY_FROM_PREY = 50
PREDATOR_REPRODUCE_THRESHOLD = 120
PREDATOR_REPRODUCE_COST = 60

FOOD_RESPAWN_RATE = 0.02
REPRODUCTION_COOLDOWN = 300  # frames

# Initialize screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Predator-Prey Simulation")
clock = pygame.time.Clock()

# Font for text
FONT = pygame.font.SysFont(None, 20)
FONT_SMALL = pygame.font.SysFont(None, 16)


class Obstacle:
    """Static obstacle that agents must navigate around."""
    def __init__(self, x, y, radius=30):
        self.position = pygame.math.Vector2(x, y)
        self.radius = radius
    
    def draw(self):
        pygame.draw.circle(screen, OBSTACLE_COLOR, 
                         (int(self.position.x), int(self.position.y)), 
                         self.radius)


class Food:
    """Food resource that prey can consume for energy."""
    def __init__(self, x=None, y=None):
        if x is None or y is None:
            self.position = pygame.math.Vector2(
                random.uniform(20, SIMULATION_WIDTH - 20),
                random.uniform(20, HEIGHT - 20)
            )
        else:
            self.position = pygame.math.Vector2(x, y)
        self.energy = PREY_ENERGY_FROM_FOOD
    
    def draw(self):
        pygame.draw.circle(screen, FOOD_COLOR,
                         (int(self.position.x), int(self.position.y)), 3)


class Agent:
    """Base class for all agents in the simulation."""
    def __init__(self, position=None, speed=2, color=PREY_COLOR, energy=100):
        if position is None:
            self.position = pygame.math.Vector2(
                random.uniform(20, SIMULATION_WIDTH - 20),
                random.uniform(20, HEIGHT - 20)
            )
        else:
            self.position = position
        
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.speed = speed
        self.color = color
        self.energy = energy
        self.max_energy = energy * 2
        self.trail = []
        self.max_trail_length = 15
        self.reproduction_cooldown = 0
    
    def update_position(self, obstacles):
        """Update the agent's position based on velocity and avoid obstacles."""
        # Avoid obstacles
        self.avoid_obstacles(obstacles)
        
        # Move the agent
        self.position += self.velocity * self.speed
        
        # Bounce off walls
        self._bounce_off_walls()
        
        # Update trail
        self._update_trail()
    
    def avoid_obstacles(self, obstacles):
        """Steer away from nearby obstacles."""
        avoidance_force = pygame.math.Vector2(0, 0)
        for obstacle in obstacles:
            distance = self.position.distance_to(obstacle.position)
            if distance < obstacle.radius + 50:
                # Steer away from obstacle
                away = (self.position - obstacle.position)
                if away.length() > 0:
                    away = away.normalize()
                    strength = 1.0 - (distance / (obstacle.radius + 50))
                    avoidance_force += away * strength
        
        if avoidance_force.length() > 0:
            avoidance_force = avoidance_force.normalize()
            self.velocity = (self.velocity + avoidance_force * 0.5).normalize()
    
    def _bounce_off_walls(self):
        """Bounce the agent off the screen edges."""
        if self.position.x < 0 or self.position.x > SIMULATION_WIDTH:
            self.velocity.x *= -1
        if self.position.y < 0 or self.position.y > HEIGHT:
            self.velocity.y *= -1
        
        self.position.x = max(0, min(self.position.x, SIMULATION_WIDTH))
        self.position.y = max(0, min(self.position.y, HEIGHT))
    
    def _update_trail(self):
        """Update the trail of the agent for visualization."""
        self.trail.append(self.position.copy())
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
    
    def draw_trail(self):
        """Draw the trail of the agent."""
        if len(self.trail) > 1:
            pygame.draw.lines(screen, self.color, False,
                            [(int(p.x), int(p.y)) for p in self.trail], 1)
    
    def lose_energy(self, amount):
        """Decrease energy by the specified amount."""
        self.energy = max(0, self.energy - amount)
    
    def gain_energy(self, amount):
        """Increase energy by the specified amount."""
        self.energy = min(self.max_energy, self.energy + amount)
    
    def is_alive(self):
        """Check if the agent has energy remaining."""
        return self.energy > 0


class Prey(Agent):
    """Class representing a prey agent."""
    def __init__(self, position=None):
        super().__init__(position=position, speed=2.5, color=PREY_COLOR, 
                        energy=PREY_ENERGY_START)
        self.vision_radius = 60
        self.seeking_mate = False
        self.mate_target = None
    
    def update(self, predators, food_list, other_prey, obstacles, flocking_enabled):
        """Update the prey's state based on environment."""
        # Lose energy over time
        self.lose_energy(PREY_ENERGY_LOSS)
        
        # Update reproduction cooldown
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        
        # Behavior priority: flee > seek food > seek mate > flock
        nearest_predator = self._find_nearest_predator(predators)
        
        if nearest_predator:
            # High priority: flee from predators
            self.flee_from(nearest_predator)
        elif self.energy < 50 and food_list:
            # Medium priority: seek food when hungry
            self.seek_food(food_list)
        elif (self.energy > PREY_REPRODUCE_THRESHOLD and 
              self.reproduction_cooldown == 0):
            # Low priority: seek mate when energy is high
            self.seek_mate(other_prey)
        elif flocking_enabled:
            # Default: flock with nearby prey
            self.flock(other_prey)
        
        # Update position
        self.update_position(obstacles)
    
    def _find_nearest_predator(self, predators):
        """Find the nearest predator within vision radius."""
        nearest = None
        min_distance = self.vision_radius
        for predator in predators:
            distance = self.position.distance_to(predator.position)
            if distance < min_distance:
                min_distance = distance
                nearest = predator
        return nearest
    
    def flee_from(self, predator):
        """Change velocity to flee away from the predator."""
        flee_direction = (self.position - predator.position)
        if flee_direction.length() > 0:
            self.velocity = flee_direction.normalize()
    
    def seek_food(self, food_list):
        """Move towards the nearest food."""
        if not food_list:
            return
        
        nearest_food = min(food_list, 
                          key=lambda f: self.position.distance_to(f.position))
        direction = (nearest_food.position - self.position)
        if direction.length() > 0:
            self.velocity = direction.normalize()
    
    def seek_mate(self, other_prey):
        """Seek another prey for reproduction."""
        potential_mates = [
            p for p in other_prey 
            if p != self and p.energy > PREY_REPRODUCE_THRESHOLD 
            and p.reproduction_cooldown == 0
        ]
        
        if potential_mates:
            nearest_mate = min(potential_mates,
                             key=lambda p: self.position.distance_to(p.position))
            direction = (nearest_mate.position - self.position)
            if direction.length() > 0:
                self.velocity = direction.normalize()
    
    def flock(self, other_prey):
        """Implement flocking behavior (cohesion, alignment, separation)."""
        nearby_prey = [
            p for p in other_prey 
            if p != self and self.position.distance_to(p.position) < 50
        ]
        
        if not nearby_prey:
            return
        
        # Cohesion: move towards center of mass
        center = pygame.math.Vector2(0, 0)
        for prey in nearby_prey:
            center += prey.position
        center /= len(nearby_prey)
        cohesion = (center - self.position)
        if cohesion.length() > 0:
            cohesion = cohesion.normalize() * 0.3
        
        # Alignment: match velocity
        avg_velocity = pygame.math.Vector2(0, 0)
        for prey in nearby_prey:
            avg_velocity += prey.velocity
        avg_velocity /= len(nearby_prey)
        alignment = avg_velocity * 0.3
        
        # Separation: avoid crowding
        separation = pygame.math.Vector2(0, 0)
        for prey in nearby_prey:
            diff = self.position - prey.position
            if diff.length() > 0 and diff.length() < 20:
                separation += diff.normalize() / diff.length()
        if separation.length() > 0:
            separation = separation.normalize() * 0.4
        
        # Combine forces
        total_force = cohesion + alignment + separation
        if total_force.length() > 0:
            self.velocity = (self.velocity + total_force).normalize()
        
        # Speed bonus based on flock size
        flock_bonus = min(len(nearby_prey) * 0.1, 1.0)
        self.speed = 2.5 + flock_bonus
    
    def draw(self):
        """Draw the prey as a circle with energy indicator."""
        # Draw trail
        self.draw_trail()
        
        # Draw prey
        pygame.draw.circle(screen, self.color,
                         (int(self.position.x), int(self.position.y)), 5)
        
        # Draw energy bar
        bar_width = 10
        bar_height = max(1, int((self.energy / self.max_energy) * 10))
        pygame.draw.rect(screen, (0, 255, 0),
                        (int(self.position.x) - bar_width // 2,
                         int(self.position.y) - 10,
                         bar_width, bar_height))


class Predator(Agent):
    """Class representing a predator agent."""
    def __init__(self, position=None):
        super().__init__(position=position, speed=3.0, color=PREDATOR_COLOR,
                        energy=PREDATOR_ENERGY_START)
    
    def update(self, prey_list, other_predators, obstacles):
        """Update the predator's state based on nearby prey."""
        # Lose energy over time
        self.lose_energy(PREDATOR_ENERGY_LOSS)
        
        # Update reproduction cooldown
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        
        if prey_list:
            nearest_prey = self._find_nearest_prey(prey_list)
            if nearest_prey:
                self.hunt(nearest_prey)
        elif (self.energy > PREDATOR_REPRODUCE_THRESHOLD and 
              self.reproduction_cooldown == 0):
            # Seek mate when no prey and energy is high
            self.seek_mate(other_predators)
        
        # Update position
        self.update_position(obstacles)
    
    def _find_nearest_prey(self, prey_list):
        """Find the nearest prey."""
        return min(prey_list, 
                  key=lambda prey: self.position.distance_to(prey.position),
                  default=None)
    
    def hunt(self, prey):
        """Change velocity to move towards the prey."""
        direction = (prey.position - self.position)
        if direction.length() > 0:
            self.velocity = direction.normalize()
    
    def seek_mate(self, other_predators):
        """Seek another predator for reproduction."""
        potential_mates = [
            p for p in other_predators 
            if p != self and p.energy > PREDATOR_REPRODUCE_THRESHOLD
            and p.reproduction_cooldown == 0
        ]
        
        if potential_mates:
            nearest_mate = min(potential_mates,
                             key=lambda p: self.position.distance_to(p.position))
            direction = (nearest_mate.position - self.position)
            if direction.length() > 0:
                self.velocity = direction.normalize()
    
    def draw(self):
        """Draw the predator as a triangle with energy indicator."""
        # Draw trail
        self.draw_trail()
        
        # Calculate the angle
        angle = self.velocity.angle_to(pygame.math.Vector2(1, 0))
        
        # Define triangle points
        point_list = [
            pygame.math.Vector2(12, 0),
            pygame.math.Vector2(-6, -6),
            pygame.math.Vector2(-6, 6),
        ]
        
        # Rotate and translate
        rotated_points = [self.position + p.rotate(-angle) for p in point_list]
        
        # Draw predator
        pygame.draw.polygon(screen, self.color, rotated_points)
        
        # Draw energy bar
        bar_width = 12
        bar_height = max(1, int((self.energy / self.max_energy) * 12))
        pygame.draw.rect(screen, (255, 0, 0),
                        (int(self.position.x) - bar_width // 2,
                         int(self.position.y) - 15,
                         bar_width, bar_height))


class Simulation:
    """Class to manage the entire simulation."""
    def __init__(self):
        self.prey_list = [Prey() for _ in range(30)]
        self.predator_list = [Predator() for _ in range(5)]
        self.food_list = [Food() for _ in range(40)]
        self.obstacles = [
            Obstacle(200, 150),
            Obstacle(400, 400),
            Obstacle(600, 250),
        ]
        self.running = True
        self.flocking_enabled = True
        
        # History tracking
        self.history = {
            'time': [],
            'prey_count': [],
            'predator_count': [],
            'prey_births': [],
            'predator_births': []
        }
        self.timestep = 0
        self.prey_births_this_step = 0
        self.predator_births_this_step = 0
        
        # Adjustable parameters
        self.reproduction_rate_multiplier = 1.0
        self.energy_consumption_multiplier = 1.0
        
        # Graph setup
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(4, 6))
        self.fig.patch.set_facecolor('#28283a')
        self.canvas = FigureCanvasAgg(self.fig)
    
    def run(self):
        """Main loop of the simulation."""
        while self.running:
            clock.tick(FPS)
            self.handle_events()
            self.update_agents()
            self.handle_interactions()
            self.respawn_food()
            self.track_history()
            self.render()
        
        pygame.quit()
    
    def handle_events(self):
        """Handle user input and events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.prey_list.append(Prey())
                elif event.key == pygame.K_o:
                    self.predator_list.append(Predator())
                elif event.key == pygame.K_f:
                    # Add food
                    self.food_list.append(Food())
                elif event.key == pygame.K_b:
                    # Toggle flocking
                    self.flocking_enabled = not self.flocking_enabled
                elif event.key == pygame.K_r:
                    # Increase reproduction rate
                    self.reproduction_rate_multiplier += 0.1
                elif event.key == pygame.K_t:
                    # Decrease reproduction rate
                    self.reproduction_rate_multiplier = max(0.1, 
                                                           self.reproduction_rate_multiplier - 0.1)
                elif event.key == pygame.K_e:
                    # Increase energy consumption
                    self.energy_consumption_multiplier += 0.1
                elif event.key == pygame.K_d:
                    # Decrease energy consumption
                    self.energy_consumption_multiplier = max(0.1,
                                                            self.energy_consumption_multiplier - 0.1)
    
    def update_agents(self):
        """Update all agents in the simulation."""
        # Reset birth counters
        self.prey_births_this_step = 0
        self.predator_births_this_step = 0
        
        # Update prey
        for prey in self.prey_list[:]:
            prey.update(self.predator_list, self.food_list, self.prey_list,
                       self.obstacles, self.flocking_enabled)
            if not prey.is_alive():
                self.prey_list.remove(prey)
        
        # Update predators
        for predator in self.predator_list[:]:
            predator.update(self.prey_list, self.predator_list, self.obstacles)
            if not predator.is_alive():
                self.predator_list.remove(predator)
    
    def handle_interactions(self):
        """Handle collisions and interactions between agents."""
        # Prey eating food
        for prey in self.prey_list:
            for food in self.food_list[:]:
                if prey.position.distance_to(food.position) < 8:
                    prey.gain_energy(food.energy)
                    self.food_list.remove(food)
        
        # Predators eating prey
        for predator in self.predator_list:
            for prey in self.prey_list[:]:
                if predator.position.distance_to(prey.position) < 10:
                    predator.gain_energy(PREDATOR_ENERGY_FROM_PREY)
                    self.prey_list.remove(prey)
                    break
        
        # Prey reproduction
        self.handle_prey_reproduction()
        
        # Predator reproduction
        self.handle_predator_reproduction()
    
    def handle_prey_reproduction(self):
        """Handle reproduction between prey."""
        for i, prey1 in enumerate(self.prey_list):
            if (prey1.energy > PREY_REPRODUCE_THRESHOLD * self.reproduction_rate_multiplier
                and prey1.reproduction_cooldown == 0):
                for prey2 in self.prey_list[i+1:]:
                    if (prey2.energy > PREY_REPRODUCE_THRESHOLD * self.reproduction_rate_multiplier
                        and prey2.reproduction_cooldown == 0
                        and prey1.position.distance_to(prey2.position) < 15):
                        # Reproduce
                        offspring_pos = (prey1.position + prey2.position) / 2
                        self.prey_list.append(Prey(position=offspring_pos))
                        prey1.lose_energy(PREY_REPRODUCE_COST)
                        prey2.lose_energy(PREY_REPRODUCE_COST)
                        prey1.reproduction_cooldown = REPRODUCTION_COOLDOWN
                        prey2.reproduction_cooldown = REPRODUCTION_COOLDOWN
                        self.prey_births_this_step += 1
                        break
    
    def handle_predator_reproduction(self):
        """Handle reproduction between predators."""
        for i, pred1 in enumerate(self.predator_list):
            if (pred1.energy > PREDATOR_REPRODUCE_THRESHOLD * self.reproduction_rate_multiplier
                and pred1.reproduction_cooldown == 0):
                for pred2 in self.predator_list[i+1:]:
                    if (pred2.energy > PREDATOR_REPRODUCE_THRESHOLD * self.reproduction_rate_multiplier
                        and pred2.reproduction_cooldown == 0
                        and pred1.position.distance_to(pred2.position) < 15):
                        # Reproduce
                        offspring_pos = (pred1.position + pred2.position) / 2
                        self.predator_list.append(Predator(position=offspring_pos))
                        pred1.lose_energy(PREDATOR_REPRODUCE_COST)
                        pred2.lose_energy(PREDATOR_REPRODUCE_COST)
                        pred1.reproduction_cooldown = REPRODUCTION_COOLDOWN
                        pred2.reproduction_cooldown = REPRODUCTION_COOLDOWN
                        self.predator_births_this_step += 1
                        break
    
    def respawn_food(self):
        """Randomly respawn food resources."""
        if random.random() < FOOD_RESPAWN_RATE:
            self.food_list.append(Food())
    
    def track_history(self):
        """Track population and birth rates over time."""
        self.timestep += 1
        if self.timestep % 10 == 0:  # Record every 10 frames
            self.history['time'].append(self.timestep)
            self.history['prey_count'].append(len(self.prey_list))
            self.history['predator_count'].append(len(self.predator_list))
            self.history['prey_births'].append(self.prey_births_this_step)
            self.history['predator_births'].append(self.predator_births_this_step)
    
    def render(self):
        """Render all elements on the screen."""
        screen.fill(BACKGROUND_COLOR)
        
        # Draw simulation area
        pygame.draw.rect(screen, (35, 35, 50), 
                        (0, 0, SIMULATION_WIDTH, HEIGHT))
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw()
        
        # Draw food
        for food in self.food_list:
            food.draw()
        
        # Draw prey
        for prey in self.prey_list:
            prey.draw()
        
        # Draw predators
        for predator in self.predator_list:
            predator.draw()
        
        # Draw UI
        self.draw_legend()
        self.draw_stats()
        self.draw_controls()
        self.draw_graphs()
        
        pygame.display.flip()
    
    def draw_legend(self):
        """Draw the legend on the screen."""
        y_offset = 10
        texts = [
            ('Prey (Green)', PREY_COLOR),
            ('Predator (Red)', PREDATOR_COLOR),
            ('Food (Yellow)', FOOD_COLOR),
            ('Obstacle (Gray)', OBSTACLE_COLOR)
        ]
        for text, color in texts:
            rendered = FONT_SMALL.render(text, True, color)
            screen.blit(rendered, (10, y_offset))
            y_offset += 18
    
    def draw_stats(self):
        """Draw the simulation statistics."""
        y_offset = HEIGHT - 120
        stats = [
            f'Timestep: {self.timestep}',
            f'Prey: {len(self.prey_list)}',
            f'Predators: {len(self.predator_list)}',
            f'Food: {len(self.food_list)}',
            f'Flocking: {"ON" if self.flocking_enabled else "OFF"}',
            f'Repro Rate: {self.reproduction_rate_multiplier:.1f}x',
            f'Energy Use: {self.energy_consumption_multiplier:.1f}x'
        ]
        for stat in stats:
            rendered = FONT_SMALL.render(stat, True, TEXT_COLOR)
            screen.blit(rendered, (10, y_offset))
            y_offset += 18
    
    def draw_controls(self):
        """Draw control instructions."""
        y_offset = HEIGHT - 250
        controls = [
            'Controls:',
            'P: Add Prey',
            'O: Add Predator',
            'F: Add Food',
            'B: Toggle Flocking',
            'R/T: Repro Rate +/-',
            'E/D: Energy Use +/-'
        ]
        for control in controls:
            rendered = FONT_SMALL.render(control, True, TEXT_COLOR)
            screen.blit(rendered, (10, y_offset))
            y_offset += 18
    
    def draw_graphs(self):
        """Draw population and birth rate graphs."""
        if len(self.history['time']) < 2:
            return
        
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        
        # Population graph
        self.ax1.plot(self.history['time'], self.history['prey_count'], 
                     'g-', label='Prey', linewidth=2)
        self.ax1.plot(self.history['time'], self.history['predator_count'],
                     'r-', label='Predators', linewidth=2)
        self.ax1.set_ylabel('Population', color='white')
        self.ax1.set_title('Population Over Time', color='white')
        self.ax1.legend(loc='upper right')
        self.ax1.set_facecolor('#28283a')
        self.ax1.tick_params(colors='white')
        for spine in self.ax1.spines.values():
            spine.set_color('white')
        
        # Birth rate graph
        self.ax2.plot(self.history['time'], self.history['prey_births'],
                     'g-', label='Prey Births', linewidth=2)
        self.ax2.plot(self.history['time'], self.history['predator_births'],
                     'r-', label='Predator Births', linewidth=2)
        self.ax2.set_xlabel('Time', color='white')
        self.ax2.set_ylabel('Births', color='white')
        self.ax2.set_title('Birth Rates', color='white')
        self.ax2.legend(loc='upper right')
        self.ax2.set_facecolor('#28283a')
        self.ax2.tick_params(colors='white')
        for spine in self.ax2.spines.values():
            spine.set_color('white')
        
        # Render to pygame surface
        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.buffer_rgba()
        size = self.canvas.get_width_height()
        
        surf = pygame.image.frombuffer(raw_data, size, "RGBA")
        screen.blit(surf, (SIMULATION_WIDTH, 0))


if __name__ == "__main__":
    simulation = Simulation()
    simulation.run()
