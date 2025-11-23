"""
Epidemic Simulation - SIR Model
Project 2: Bonus Points Implementation

Features:
- SIR (Susceptible, Infected, Recovered) model with death
- Proximity-based infection with duration-dependent probability
- Recovery and death mechanics
- Movement with temporary grouping behavior
- Quarantine zones for infected agents
- Vaccination system with success rates
- Real-time graphs for S/I/R/D populations and rates
- Interactive controls for infection, recovery, and vaccination rates
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
SUSCEPTIBLE_COLOR = (100, 150, 255)  # Blue
INFECTED_COLOR = (255, 50, 50)       # Red
RECOVERED_COLOR = (100, 255, 100)    # Green
DEAD_COLOR = (100, 100, 100)         # Gray
QUARANTINE_COLOR = (150, 100, 50)    # Brown
TEXT_COLOR = (200, 200, 200)

# Simulation parameters
FPS = 60
INITIAL_POPULATION = 100
INITIAL_INFECTED = 5
VACCINATION_RATE = 0.3  # 30% of population attempts vaccination
VACCINATION_SUCCESS_RATE = 0.9  # 90% success rate

# Disease parameters
BASE_INFECTION_PROBABILITY = 0.002  # Per frame when in proximity
INFECTION_DISTANCE = 15
EXPOSURE_THRESHOLD = 60  # Frames of exposure before high infection risk
INFECTION_DURATION = 300  # Frames before recovery attempt
RECOVERY_PROBABILITY = 0.7  # 70% chance to recover, 30% to die

# Movement parameters
AGENT_SPEED = 2.0
GROUPING_PROBABILITY = 0.3
GROUPING_DISTANCE = 40

# Quarantine
QUARANTINE_ZONE = pygame.Rect(50, 50, 200, 150)
QUARANTINE_ENABLED = True

# Initialize screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Epidemic Simulation - SIR Model")
clock = pygame.time.Clock()

# Fonts
FONT = pygame.font.SysFont(None, 20)
FONT_SMALL = pygame.font.SysFont(None, 16)


class Agent:
    """Agent in the epidemic simulation."""
    
    # State constants
    SUSCEPTIBLE = 0
    INFECTED = 1
    RECOVERED = 2
    DEAD = 3
    
    def __init__(self, position=None, state=SUSCEPTIBLE, vaccinated=False):
        if position is None:
            self.position = pygame.math.Vector2(
                random.uniform(20, SIMULATION_WIDTH - 20),
                random.uniform(20, HEIGHT - 20)
            )
        else:
            self.position = position
        
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.speed = AGENT_SPEED
        
        self.state = state
        self.vaccinated = vaccinated
        if vaccinated:
            self.state = Agent.RECOVERED  # Vaccinated = immune
        
        self.infection_time = 0
        self.exposure_time = {}  # Track exposure to each infected agent
        self.in_quarantine = False
        self.group_target = None
        self.group_timer = 0
        
        self.trail = []
        self.max_trail_length = 10
    
    def update(self, other_agents, quarantine_enabled):
        """Update agent state and position."""
        if self.state == Agent.DEAD:
            return
        
        # Update infection timer
        if self.state == Agent.INFECTED:
            self.infection_time += 1
            
            # Attempt recovery after infection duration
            if self.infection_time >= INFECTION_DURATION:
                if random.random() < RECOVERY_PROBABILITY:
                    self.state = Agent.RECOVERED
                    self.in_quarantine = False
                else:
                    self.state = Agent.DEAD
                return
        
        # Check for infection
        if self.state == Agent.SUSCEPTIBLE and not self.vaccinated:
            self.check_infection(other_agents)
        
        # Move to quarantine if infected and quarantine enabled
        if (self.state == Agent.INFECTED and quarantine_enabled 
            and not self.in_quarantine):
            self.move_to_quarantine()
        
        # Update movement
        self.update_movement(other_agents)
        
        # Update trail
        self._update_trail()
    
    def check_infection(self, other_agents):
        """Check if agent gets infected by nearby infected agents."""
        for other in other_agents:
            if other.state == Agent.INFECTED:
                distance = self.position.distance_to(other.position)
                
                if distance < INFECTION_DISTANCE:
                    # Track exposure time
                    if id(other) not in self.exposure_time:
                        self.exposure_time[id(other)] = 0
                    self.exposure_time[id(other)] += 1
                    
                    # Calculate infection probability based on exposure
                    exposure = self.exposure_time[id(other)]
                    infection_prob = BASE_INFECTION_PROBABILITY * (1 + exposure / EXPOSURE_THRESHOLD)
                    
                    if random.random() < infection_prob:
                        self.state = Agent.INFECTED
                        self.infection_time = 0
                        return
                else:
                    # Reset exposure if not in proximity
                    if id(other) in self.exposure_time:
                        self.exposure_time[id(other)] = max(0, self.exposure_time[id(other)] - 1)
    
    def move_to_quarantine(self):
        """Move agent towards quarantine zone."""
        self.in_quarantine = True
        # Teleport to quarantine zone
        self.position = pygame.math.Vector2(
            random.uniform(QUARANTINE_ZONE.left + 10, QUARANTINE_ZONE.right - 10),
            random.uniform(QUARANTINE_ZONE.top + 10, QUARANTINE_ZONE.bottom - 10)
        )
    
    def update_movement(self, other_agents):
        """Update agent position with grouping behavior."""
        if self.in_quarantine:
            # Limited movement in quarantine
            self.position += self.velocity * (self.speed * 0.3)
            
            # Stay within quarantine bounds
            if not QUARANTINE_ZONE.collidepoint(self.position.x, self.position.y):
                # Bounce back into quarantine
                center = pygame.math.Vector2(QUARANTINE_ZONE.centerx, QUARANTINE_ZONE.centery)
                self.velocity = (center - self.position).normalize()
        else:
            # Normal movement with occasional grouping
            if self.group_timer > 0:
                self.group_timer -= 1
                if self.group_target and self.group_target.state != Agent.DEAD:
                    # Move towards group target
                    direction = (self.group_target.position - self.position)
                    if direction.length() > GROUPING_DISTANCE:
                        self.velocity = direction.normalize()
                else:
                    self.group_target = None
                    self.group_timer = 0
            else:
                # Random chance to start grouping
                if random.random() < 0.01:  # 1% chance per frame
                    nearby = [a for a in other_agents 
                             if a != self and a.state != Agent.DEAD
                             and self.position.distance_to(a.position) < 100]
                    if nearby:
                        self.group_target = random.choice(nearby)
                        self.group_timer = random.randint(60, 180)
            
            # Move agent
            self.position += self.velocity * self.speed
            
            # Bounce off walls
            if self.position.x < 0 or self.position.x > SIMULATION_WIDTH:
                self.velocity.x *= -1
            if self.position.y < 0 or self.position.y > HEIGHT:
                self.velocity.y *= -1
            
            self.position.x = max(0, min(self.position.x, SIMULATION_WIDTH))
            self.position.y = max(0, min(self.position.y, HEIGHT))
            
            # Random direction changes
            if random.random() < 0.02:
                angle = random.uniform(-math.pi/4, math.pi/4)
                self.velocity = self.velocity.rotate(math.degrees(angle))
    
    def _update_trail(self):
        """Update movement trail."""
        self.trail.append(self.position.copy())
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
    
    def draw(self):
        """Draw the agent based on its state."""
        if self.state == Agent.DEAD:
            return  # Don't draw dead agents
        
        # Draw trail
        if len(self.trail) > 1:
            color = self.get_color()
            pygame.draw.lines(screen, color, False,
                            [(int(p.x), int(p.y)) for p in self.trail], 1)
        
        # Draw agent
        color = self.get_color()
        radius = 5
        pygame.draw.circle(screen, color,
                         (int(self.position.x), int(self.position.y)), radius)
        
        # Draw vaccination indicator
        if self.vaccinated and self.state == Agent.RECOVERED:
            pygame.draw.circle(screen, (255, 255, 255),
                             (int(self.position.x), int(self.position.y)),
                             radius + 2, 1)
    
    def get_color(self):
        """Get color based on agent state."""
        if self.state == Agent.SUSCEPTIBLE:
            return SUSCEPTIBLE_COLOR
        elif self.state == Agent.INFECTED:
            return INFECTED_COLOR
        elif self.state == Agent.RECOVERED:
            return RECOVERED_COLOR
        else:  # DEAD
            return DEAD_COLOR


class Simulation:
    """Main simulation class for epidemic model."""
    
    def __init__(self):
        self.agents = []
        self.running = True
        self.timestep = 0
        self.quarantine_enabled = QUARANTINE_ENABLED
        
        # Adjustable parameters
        self.infection_rate_multiplier = 1.0
        self.recovery_rate_multiplier = 1.0
        self.vaccination_rate = VACCINATION_RATE
        
        # Initialize population
        self.initialize_population()
        
        # History tracking
        self.history = {
            'time': [],
            'susceptible': [],
            'infected': [],
            'recovered': [],
            'dead': [],
            'new_infections': [],
            'new_recoveries': []
        }
        self.prev_infected_count = INITIAL_INFECTED
        self.prev_recovered_count = 0
        
        # Graph setup
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(4, 6))
        self.fig.patch.set_facecolor('#28283a')
        self.canvas = FigureCanvasAgg(self.fig)
    
    def initialize_population(self):
        """Create initial population with some infected and some vaccinated."""
        # Create susceptible agents
        for _ in range(INITIAL_POPULATION - INITIAL_INFECTED):
            # Determine if agent gets vaccinated
            vaccinated = random.random() < self.vaccination_rate
            if vaccinated:
                # Vaccination success check
                vaccinated = random.random() < VACCINATION_SUCCESS_RATE
            
            agent = Agent(state=Agent.SUSCEPTIBLE, vaccinated=vaccinated)
            self.agents.append(agent)
        
        # Create initial infected agents
        for _ in range(INITIAL_INFECTED):
            agent = Agent(state=Agent.INFECTED)
            self.agents.append(agent)
    
    def run(self):
        """Main simulation loop."""
        while self.running:
            clock.tick(FPS)
            self.handle_events()
            self.update_agents()
            self.track_history()
            self.render()
        
        pygame.quit()
    
    def handle_events(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    # Increase infection rate
                    self.infection_rate_multiplier += 0.1
                    global BASE_INFECTION_PROBABILITY
                    BASE_INFECTION_PROBABILITY *= 1.1
                elif event.key == pygame.K_k:
                    # Decrease infection rate
                    self.infection_rate_multiplier = max(0.1, 
                                                        self.infection_rate_multiplier - 0.1)
                    BASE_INFECTION_PROBABILITY *= 0.9
                elif event.key == pygame.K_r:
                    # Increase recovery rate
                    self.recovery_rate_multiplier += 0.1
                    global RECOVERY_PROBABILITY
                    RECOVERY_PROBABILITY = min(0.99, RECOVERY_PROBABILITY + 0.05)
                elif event.key == pygame.K_t:
                    # Decrease recovery rate
                    self.recovery_rate_multiplier = max(0.1,
                                                       self.recovery_rate_multiplier - 0.1)
                    RECOVERY_PROBABILITY = max(0.1, RECOVERY_PROBABILITY - 0.05)
                elif event.key == pygame.K_v:
                    # Increase vaccination rate
                    self.vaccination_rate = min(1.0, self.vaccination_rate + 0.1)
                elif event.key == pygame.K_b:
                    # Decrease vaccination rate
                    self.vaccination_rate = max(0.0, self.vaccination_rate - 0.1)
                elif event.key == pygame.K_q:
                    # Toggle quarantine
                    self.quarantine_enabled = not self.quarantine_enabled
                    if not self.quarantine_enabled:
                        # Release all from quarantine
                        for agent in self.agents:
                            agent.in_quarantine = False
                elif event.key == pygame.K_SPACE:
                    # Add new susceptible agent
                    self.agents.append(Agent(state=Agent.SUSCEPTIBLE))
    
    def update_agents(self):
        """Update all agents."""
        self.timestep += 1
        
        for agent in self.agents:
            agent.update(self.agents, self.quarantine_enabled)
    
    def track_history(self):
        """Track epidemic statistics over time."""
        if self.timestep % 10 == 0:  # Record every 10 frames
            # Count states
            susceptible = sum(1 for a in self.agents if a.state == Agent.SUSCEPTIBLE)
            infected = sum(1 for a in self.agents if a.state == Agent.INFECTED)
            recovered = sum(1 for a in self.agents if a.state == Agent.RECOVERED)
            dead = sum(1 for a in self.agents if a.state == Agent.DEAD)
            
            # Calculate rates
            new_infections = max(0, infected - self.prev_infected_count)
            new_recoveries = max(0, recovered - self.prev_recovered_count)
            
            self.prev_infected_count = infected
            self.prev_recovered_count = recovered
            
            # Record
            self.history['time'].append(self.timestep)
            self.history['susceptible'].append(susceptible)
            self.history['infected'].append(infected)
            self.history['recovered'].append(recovered)
            self.history['dead'].append(dead)
            self.history['new_infections'].append(new_infections)
            self.history['new_recoveries'].append(new_recoveries)
    
    def render(self):
        """Render the simulation."""
        screen.fill(BACKGROUND_COLOR)
        
        # Draw simulation area
        pygame.draw.rect(screen, (35, 35, 50),
                        (0, 0, SIMULATION_WIDTH, HEIGHT))
        
        # Draw quarantine zone
        if self.quarantine_enabled:
            pygame.draw.rect(screen, QUARANTINE_COLOR, QUARANTINE_ZONE, 2)
            quarantine_label = FONT_SMALL.render('QUARANTINE', True, QUARANTINE_COLOR)
            screen.blit(quarantine_label, (QUARANTINE_ZONE.left + 5, QUARANTINE_ZONE.top + 5))
        
        # Draw agents
        for agent in self.agents:
            agent.draw()
        
        # Draw UI
        self.draw_legend()
        self.draw_stats()
        self.draw_controls()
        self.draw_graphs()
        
        pygame.display.flip()
    
    def draw_legend(self):
        """Draw state legend."""
        y_offset = 10
        legends = [
            ('Susceptible (Blue)', SUSCEPTIBLE_COLOR),
            ('Infected (Red)', INFECTED_COLOR),
            ('Recovered (Green)', RECOVERED_COLOR),
            ('Dead (Gray)', DEAD_COLOR)
        ]
        for text, color in legends:
            rendered = FONT_SMALL.render(text, True, color)
            screen.blit(rendered, (10, y_offset))
            y_offset += 18
    
    def draw_stats(self):
        """Draw simulation statistics."""
        # Count states
        susceptible = sum(1 for a in self.agents if a.state == Agent.SUSCEPTIBLE)
        infected = sum(1 for a in self.agents if a.state == Agent.INFECTED)
        recovered = sum(1 for a in self.agents if a.state == Agent.RECOVERED)
        dead = sum(1 for a in self.agents if a.state == Agent.DEAD)
        vaccinated = sum(1 for a in self.agents if a.vaccinated)
        
        y_offset = HEIGHT - 180
        stats = [
            f'Timestep: {self.timestep}',
            f'Susceptible: {susceptible}',
            f'Infected: {infected}',
            f'Recovered: {recovered}',
            f'Dead: {dead}',
            f'Vaccinated: {vaccinated}',
            f'Quarantine: {"ON" if self.quarantine_enabled else "OFF"}',
            f'Infection Rate: {self.infection_rate_multiplier:.1f}x',
            f'Recovery Rate: {RECOVERY_PROBABILITY:.2f}',
            f'Vaccination: {self.vaccination_rate:.1%}'
        ]
        for stat in stats:
            rendered = FONT_SMALL.render(stat, True, TEXT_COLOR)
            screen.blit(rendered, (10, y_offset))
            y_offset += 18
    
    def draw_controls(self):
        """Draw control instructions."""
        y_offset = HEIGHT - 380
        controls = [
            'Controls:',
            'I/K: Infection Rate +/-',
            'R/T: Recovery Rate +/-',
            'V/B: Vaccination +/-',
            'Q: Toggle Quarantine',
            'SPACE: Add Agent'
        ]
        for control in controls:
            rendered = FONT_SMALL.render(control, True, TEXT_COLOR)
            screen.blit(rendered, (10, y_offset))
            y_offset += 18
    
    def draw_graphs(self):
        """Draw epidemic graphs."""
        if len(self.history['time']) < 2:
            return
        
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        
        # SIRD populations graph
        self.ax1.plot(self.history['time'], self.history['susceptible'],
                     'b-', label='Susceptible', linewidth=2)
        self.ax1.plot(self.history['time'], self.history['infected'],
                     'r-', label='Infected', linewidth=2)
        self.ax1.plot(self.history['time'], self.history['recovered'],
                     'g-', label='Recovered', linewidth=2)
        self.ax1.plot(self.history['time'], self.history['dead'],
                     color='gray', label='Dead', linewidth=2)
        self.ax1.set_ylabel('Population', color='white')
        self.ax1.set_title('SIRD Model Over Time', color='white')
        self.ax1.legend(loc='upper right', fontsize=8)
        self.ax1.set_facecolor('#28283a')
        self.ax1.tick_params(colors='white', labelsize=8)
        for spine in self.ax1.spines.values():
            spine.set_color('white')
        
        # Infection and recovery rates
        self.ax2.plot(self.history['time'], self.history['new_infections'],
                     'r-', label='New Infections', linewidth=2)
        self.ax2.plot(self.history['time'], self.history['new_recoveries'],
                     'g-', label='New Recoveries', linewidth=2)
        self.ax2.set_xlabel('Time', color='white')
        self.ax2.set_ylabel('Rate', color='white')
        self.ax2.set_title('Infection & Recovery Rates', color='white')
        self.ax2.legend(loc='upper right', fontsize=8)
        self.ax2.set_facecolor('#28283a')
        self.ax2.tick_params(colors='white', labelsize=8)
        for spine in self.ax2.spines.values():
            spine.set_color('white')
        
        # Render to pygame surface
        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.buffer_rgba()
        size = self.canvas.get_width_height()
        
        surf = pygame.image.frombuffer(raw_data, size, "RGBA")
        screen.blit(surf, (SIMULATION_WIDTH, 0))


def run_scenario_1():
    """Scenario 1: High infection, low recovery - extinction."""
    global BASE_INFECTION_PROBABILITY, RECOVERY_PROBABILITY, VACCINATION_RATE
    BASE_INFECTION_PROBABILITY = 0.005  # High infection
    RECOVERY_PROBABILITY = 0.3  # Low recovery
    VACCINATION_RATE = 0.1  # Low vaccination
    
    print("Running Scenario 1: Extinction (High infection, low recovery)")
    simulation = Simulation()
    simulation.run()


def run_scenario_2():
    """Scenario 2: Moderate infection, high recovery - survival."""
    global BASE_INFECTION_PROBABILITY, RECOVERY_PROBABILITY, VACCINATION_RATE
    BASE_INFECTION_PROBABILITY = 0.002  # Moderate infection
    RECOVERY_PROBABILITY = 0.85  # High recovery
    VACCINATION_RATE = 0.5  # High vaccination
    
    print("Running Scenario 2: Survival (Moderate infection, high recovery)")
    simulation = Simulation()
    simulation.run()


if __name__ == "__main__":
    # Default balanced scenario
    print("Running Epidemic Simulation - SIR Model")
    print("Adjust parameters with keyboard controls")
    print("\nTo run specific scenarios, uncomment in code:")
    print("  - run_scenario_1() for extinction scenario")
    print("  - run_scenario_2() for survival scenario")
    
    simulation = Simulation()
    # simulation.run()
    
    # Uncomment to run specific scenarios:
    run_scenario_1()
    # run_scenario_2()
