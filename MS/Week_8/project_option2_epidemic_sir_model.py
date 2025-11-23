"""
PROJECT OPTION 2: Epidemic Simulation (SIR Model)
Author: Alexandru CL
Date: November 23, 2025

Features:
- SIR (Susceptible, Infected, Recovered) state model
- Probabilistic infection based on proximity and duration
- Recovery with probability (successful recovery or death)
- Quarantine zones for infected individuals
- Vaccination strategies with success probabilities
- Real-time tracking of infection and recovery rates
- Interactive parameter controls

Controls:
- S: Add susceptible agent
- I: Add infected agent
- R: Add recovered agent
- Q: Toggle quarantine zone (click to place/remove)
- V: Vaccinate random susceptible agents
- UP/DOWN: Adjust infection rate
- LEFT/RIGHT: Adjust recovery rate
- SPACE: Toggle vaccination auto-mode
- 1/2: Switch between scenarios
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
BACKGROUND_COLOR = (20, 20, 30)
SUSCEPTIBLE_COLOR = (100, 150, 255)
INFECTED_COLOR = (255, 50, 50)
RECOVERED_COLOR = (100, 255, 100)
QUARANTINE_COLOR = (150, 50, 150)
TEXT_COLOR = (200, 200, 200)

# Simulation parameters
FPS = 60
INITIAL_SUSCEPTIBLE = 80
INITIAL_INFECTED = 5
INITIAL_RECOVERED = 0

# Disease parameters
BASE_INFECTION_PROBABILITY = 0.002  # Per frame when in proximity
INFECTION_RADIUS = 30
PROXIMITY_INFECTION_MULTIPLIER = 0.1  # Increases per frame in proximity
RECOVERY_TIME_MIN = 300  # frames (5 seconds at 60 FPS)
RECOVERY_TIME_MAX = 600  # frames (10 seconds)
RECOVERY_PROBABILITY = 0.7  # Chance of recovery vs death
VACCINATION_SUCCESS_RATE = 0.85
VACCINATION_PROBABILITY = 0.3  # Chance agent decides to get vaccinated

# Agent parameters
AGENT_SPEED = 1.5
GROUPING_PROBABILITY = 0.3  # Chance to temporarily group with others

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Epidemic Simulation (SIR Model)")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 20)
TITLE_FONT = pygame.font.SysFont(None, 24)


class QuarantineZone:
    """Represents a quarantine area for infected agents."""
    def __init__(self, center, radius=80):
        self.center = pygame.math.Vector2(center)
        self.radius = radius
        self.active = True

    def contains(self, position):
        """Check if position is inside quarantine zone."""
        return self.center.distance_to(position) < self.radius

    def draw(self):
        """Draw quarantine zone."""
        if self.active:
            # Draw filled circle with alpha
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*QUARANTINE_COLOR, 50), 
                             (self.radius, self.radius), self.radius)
            screen.blit(s, (int(self.center.x - self.radius), 
                           int(self.center.y - self.radius)))
            
            # Draw border
            pygame.draw.circle(screen, QUARANTINE_COLOR, 
                             (int(self.center.x), int(self.center.y)), 
                             self.radius, 3)
            
            # Draw label
            label = FONT.render("QUARANTINE", True, QUARANTINE_COLOR)
            screen.blit(label, (int(self.center.x - 50), int(self.center.y)))


class Agent:
    """Base agent class with movement and state management."""
    def __init__(self, position=None, state='susceptible'):
        if position:
            self.position = pygame.math.Vector2(position)
        else:
            self.position = pygame.math.Vector2(
                random.uniform(50, WIDTH - GRAPH_WIDTH - 50),
                random.uniform(50, HEIGHT - 50)
            )
        
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.speed = AGENT_SPEED
        
        self.state = state  # 'susceptible', 'infected', 'recovered', 'dead'
        self.infection_timer = 0
        self.recovery_time = random.randint(RECOVERY_TIME_MIN, RECOVERY_TIME_MAX)
        self.proximity_counters = {}  # Track proximity duration with infected agents
        self.vaccinated = False
        self.quarantined = False
        
        # Social behavior
        self.group_timer = 0
        self.group_target = None
        
        # Trail for visualization
        self.trail = []
        self.max_trail_length = 20

    def update(self, other_agents, quarantine_zones, infection_rate):
        """Update agent state and position."""
        if self.state == 'dead':
            return
        
        # Update infection
        if self.state == 'infected':
            self.infection_timer += 1
            
            # Check if ready to attempt recovery
            if self.infection_timer >= self.recovery_time:
                if random.random() < RECOVERY_PROBABILITY:
                    self.state = 'recovered'
                else:
                    self.state = 'dead'
                return
        
        # Social grouping behavior
        if self.group_timer > 0:
            self.group_timer -= 1
            if self.group_target and self.group_target.state != 'dead':
                # Move towards group target
                direction = (self.group_target.position - self.position)
                if direction.length() > 0:
                    direction = direction.normalize()
                    self.velocity = (self.velocity * 0.8 + direction * 0.2).normalize()
        else:
            # Randomly decide to group
            if random.random() < GROUPING_PROBABILITY * 0.01:
                nearby = [a for a in other_agents 
                         if a != self and a.state != 'dead' 
                         and self.position.distance_to(a.position) < 100]
                if nearby:
                    self.group_target = random.choice(nearby)
                    self.group_timer = random.randint(60, 180)
        
        # Check for quarantine
        self.quarantined = False
        if self.state == 'infected':
            for zone in quarantine_zones:
                if zone.active and zone.contains(self.position):
                    self.quarantined = True
                    # Slow down in quarantine
                    self.speed = AGENT_SPEED * 0.3
                    break
        
        if not self.quarantined:
            self.speed = AGENT_SPEED
        
        # Move
        self.position += self.velocity * self.speed
        self._bounce_off_walls()
        self._update_trail()
        
        # Check for infection
        if self.state == 'susceptible' and not self.vaccinated:
            self.check_infection(other_agents, infection_rate)

    def check_infection(self, other_agents, infection_rate):
        """Check if agent gets infected through proximity."""
        for other in other_agents:
            if other.state != 'infected' or other == self:
                continue
            
            distance = self.position.distance_to(other.position)
            if distance < INFECTION_RADIUS:
                # Track proximity duration
                other_id = id(other)
                if other_id not in self.proximity_counters:
                    self.proximity_counters[other_id] = 0
                
                self.proximity_counters[other_id] += 1
                
                # Infection probability increases with proximity duration
                proximity_bonus = self.proximity_counters[other_id] * PROXIMITY_INFECTION_MULTIPLIER
                infection_prob = BASE_INFECTION_PROBABILITY * infection_rate + proximity_bonus * 0.0001
                
                if random.random() < infection_prob:
                    self.state = 'infected'
                    self.infection_timer = 0
                    self.proximity_counters.clear()
                    break
        
        # Clear old proximity counters
        current_infected_ids = {id(a) for a in other_agents if a.state == 'infected'}
        self.proximity_counters = {k: v for k, v in self.proximity_counters.items() 
                                  if k in current_infected_ids}

    def vaccinate(self):
        """Attempt to vaccinate the agent."""
        if self.state == 'susceptible' and not self.vaccinated:
            # Agent decides whether to get vaccinated
            if random.random() < VACCINATION_PROBABILITY:
                # Vaccination attempt
                if random.random() < VACCINATION_SUCCESS_RATE:
                    self.vaccinated = True
                    return True
        return False

    def _bounce_off_walls(self):
        """Bounce off screen edges."""
        if self.position.x < 10 or self.position.x > WIDTH - GRAPH_WIDTH - 10:
            self.velocity.x *= -1
        if self.position.y < 10 or self.position.y > HEIGHT - 10:
            self.velocity.y *= -1
        
        self.position.x = max(10, min(self.position.x, WIDTH - GRAPH_WIDTH - 10))
        self.position.y = max(10, min(self.position.y, HEIGHT - 10))

    def _update_trail(self):
        """Update movement trail."""
        self.trail.append(self.position.copy())
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    def draw(self):
        """Draw agent with appropriate color and indicators."""
        if self.state == 'dead':
            return
        
        # Determine color
        if self.state == 'susceptible':
            color = SUSCEPTIBLE_COLOR
        elif self.state == 'infected':
            color = INFECTED_COLOR
        elif self.state == 'recovered':
            color = RECOVERED_COLOR
        
        # Draw trail
        if len(self.trail) > 1:
            pygame.draw.lines(screen, color, False, 
                            [(int(p.x), int(p.y)) for p in self.trail], 1)
        
        # Draw agent
        radius = 6 if self.state == 'infected' else 5
        pygame.draw.circle(screen, color, 
                         (int(self.position.x), int(self.position.y)), radius)
        
        # Draw vaccination indicator
        if self.vaccinated:
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(self.position.x), int(self.position.y)), 
                             radius + 2, 1)
        
        # Draw infection radius for infected agents
        if self.state == 'infected' and not self.quarantined:
            s = pygame.Surface((INFECTION_RADIUS * 2, INFECTION_RADIUS * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*INFECTED_COLOR, 20), 
                             (INFECTION_RADIUS, INFECTION_RADIUS), INFECTION_RADIUS)
            screen.blit(s, (int(self.position.x - INFECTION_RADIUS), 
                           int(self.position.y - INFECTION_RADIUS)))


class EpidemicTracker:
    """Tracks and visualizes epidemic statistics."""
    def __init__(self, max_history=400):
        self.max_history = max_history
        self.time_steps = []
        self.susceptible_counts = []
        self.infected_counts = []
        self.recovered_counts = []
        self.dead_counts = []
        self.infection_rates = []
        self.recovery_rates = []
        self.current_time = 0
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(5, 6))
        self.fig.patch.set_facecolor('#14141e')
        self.canvas = FigureCanvasAgg(self.fig)

    def update(self, susceptible, infected, recovered, dead, 
               infection_rate=0, recovery_rate=0):
        """Update epidemic data."""
        self.current_time += 1
        self.time_steps.append(self.current_time)
        self.susceptible_counts.append(susceptible)
        self.infected_counts.append(infected)
        self.recovered_counts.append(recovered)
        self.dead_counts.append(dead)
        self.infection_rates.append(infection_rate)
        self.recovery_rates.append(recovery_rate)
        
        # Keep only recent history
        if len(self.time_steps) > self.max_history:
            self.time_steps.pop(0)
            self.susceptible_counts.pop(0)
            self.infected_counts.pop(0)
            self.recovered_counts.pop(0)
            self.dead_counts.pop(0)
            self.infection_rates.pop(0)
            self.recovery_rates.pop(0)

    def draw(self, screen, x_offset, y_offset):
        """Draw epidemic graphs."""
        if len(self.time_steps) < 2:
            return
        
        # Clear axes
        self.ax1.clear()
        self.ax2.clear()
        
        # Style configuration
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor('#24242e')
            ax.tick_params(colors='white', labelsize=8)
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        # Population graph
        self.ax1.plot(self.time_steps, self.susceptible_counts, 
                     color='#6496ff', label='Susceptible', linewidth=2)
        self.ax1.plot(self.time_steps, self.infected_counts, 
                     color='#ff3232', label='Infected', linewidth=2)
        self.ax1.plot(self.time_steps, self.recovered_counts, 
                     color='#64ff64', label='Recovered', linewidth=2)
        self.ax1.plot(self.time_steps, self.dead_counts, 
                     color='#808080', label='Dead', linewidth=2)
        self.ax1.set_ylabel('Population', color='white', fontsize=9)
        self.ax1.set_title('SIR Model - Population States', color='white', fontsize=10)
        self.ax1.legend(loc='upper right', fontsize=7, facecolor='#24242e', 
                       edgecolor='white', labelcolor='white')
        self.ax1.grid(True, alpha=0.2, color='white')
        
        # Rates graph
        self.ax2.plot(self.time_steps, self.infection_rates, 
                     color='#ff6432', label='Infection Rate', linewidth=2)
        self.ax2.plot(self.time_steps, self.recovery_rates, 
                     color='#64ffc8', label='Recovery Rate', linewidth=2)
        self.ax2.set_xlabel('Time', color='white', fontsize=9)
        self.ax2.set_ylabel('Rate (per 100 frames)', color='white', fontsize=9)
        self.ax2.set_title('Infection & Recovery Rates', color='white', fontsize=10)
        self.ax2.legend(loc='upper right', fontsize=8, facecolor='#24242e', 
                       edgecolor='white', labelcolor='white')
        self.ax2.grid(True, alpha=0.2, color='white')
        
        # Render to surface
        self.canvas.draw()
        raw_data = self.canvas.buffer_rgba()
        size = self.canvas.get_width_height()
        
        surf = pygame.image.frombuffer(raw_data, size, "RGBA")
        screen.blit(surf, (x_offset, y_offset))


class Simulation:
    """Main epidemic simulation manager."""
    def __init__(self, scenario='balanced'):
        self.scenario = scenario
        self.reset_simulation()

    def reset_simulation(self):
        """Reset simulation based on scenario."""
        if self.scenario == 'extinction':
            # Scenario 1: All agents die (high infection, low recovery)
            self.agents = [Agent(state='susceptible') 
                          for _ in range(INITIAL_SUSCEPTIBLE)]
            self.agents += [Agent(state='infected') 
                           for _ in range(INITIAL_INFECTED)]
            self.infection_rate = 2.5
            self.recovery_rate = 0.3
        else:  # 'survival'
            # Scenario 2: Some survive, virus disappears
            self.agents = [Agent(state='susceptible') 
                          for _ in range(INITIAL_SUSCEPTIBLE)]
            self.agents += [Agent(state='infected') 
                           for _ in range(INITIAL_INFECTED)]
            self.infection_rate = 1.0
            self.recovery_rate = 1.5
        
        self.quarantine_zones = []
        self.running = True
        self.auto_vaccinate = False
        
        self.tracker = EpidemicTracker()
        self.frame_count = 0
        
        # Rate tracking
        self.new_infections = 0
        self.new_recoveries = 0
        self.infection_window = []
        self.recovery_window = []
        
        # Add initial quarantine zone
        self.quarantine_zones.append(
            QuarantineZone((WIDTH - GRAPH_WIDTH - 200, HEIGHT - 150))
        )

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
                elif event.key == pygame.K_s:
                    self.agents.append(Agent(state='susceptible'))
                elif event.key == pygame.K_i:
                    self.agents.append(Agent(state='infected'))
                elif event.key == pygame.K_r:
                    self.agents.append(Agent(state='recovered'))
                elif event.key == pygame.K_q:
                    # Toggle quarantine zone at random location
                    if len(self.quarantine_zones) < 3:
                        pos = (random.uniform(150, WIDTH - GRAPH_WIDTH - 150),
                              random.uniform(150, HEIGHT - 150))
                        self.quarantine_zones.append(QuarantineZone(pos))
                    elif self.quarantine_zones:
                        self.quarantine_zones.pop()
                elif event.key == pygame.K_v:
                    # Vaccinate random susceptible agents
                    susceptible = [a for a in self.agents if a.state == 'susceptible']
                    for agent in random.sample(susceptible, 
                                             min(10, len(susceptible))):
                        agent.vaccinate()
                elif event.key == pygame.K_SPACE:
                    self.auto_vaccinate = not self.auto_vaccinate
                elif event.key == pygame.K_UP:
                    self.infection_rate = min(5.0, self.infection_rate + 0.1)
                elif event.key == pygame.K_DOWN:
                    self.infection_rate = max(0.1, self.infection_rate - 0.1)
                elif event.key == pygame.K_RIGHT:
                    self.recovery_rate = min(5.0, self.recovery_rate + 0.1)
                elif event.key == pygame.K_LEFT:
                    self.recovery_rate = max(0.1, self.recovery_rate - 0.1)
                elif event.key == pygame.K_1:
                    self.scenario = 'extinction'
                    self.reset_simulation()
                elif event.key == pygame.K_2:
                    self.scenario = 'survival'
                    self.reset_simulation()

    def update(self):
        """Update simulation state."""
        self.frame_count += 1
        
        # Track previous states
        prev_states = {id(a): a.state for a in self.agents}
        
        # Update agents
        for agent in self.agents:
            agent.update(self.agents, self.quarantine_zones, self.infection_rate)
        
        # Count state changes for rates
        new_infections_this_frame = 0
        new_recoveries_this_frame = 0
        
        for agent in self.agents:
            agent_id = id(agent)
            if agent_id in prev_states:
                if prev_states[agent_id] == 'susceptible' and agent.state == 'infected':
                    new_infections_this_frame += 1
                elif prev_states[agent_id] == 'infected' and agent.state in ['recovered', 'dead']:
                    new_recoveries_this_frame += 1
        
        self.infection_window.append(new_infections_this_frame)
        self.recovery_window.append(new_recoveries_this_frame)
        
        # Keep window of last 100 frames
        if len(self.infection_window) > 100:
            self.infection_window.pop(0)
        if len(self.recovery_window) > 100:
            self.recovery_window.pop(0)
        
        # Auto-vaccination
        if self.auto_vaccinate and self.frame_count % 60 == 0:
            susceptible = [a for a in self.agents if a.state == 'susceptible']
            for agent in random.sample(susceptible, min(5, len(susceptible))):
                agent.vaccinate()
        
        # Adjust recovery probability based on rate
        global RECOVERY_PROBABILITY
        RECOVERY_PROBABILITY = min(0.95, 0.5 + self.recovery_rate * 0.1)
        
        # Update tracker every 10 frames
        if self.frame_count % 10 == 0:
            counts = self.count_states()
            infection_rate = sum(self.infection_window)
            recovery_rate = sum(self.recovery_window)
            self.tracker.update(counts['susceptible'], counts['infected'],
                              counts['recovered'], counts['dead'],
                              infection_rate, recovery_rate)

    def count_states(self):
        """Count agents in each state."""
        counts = {
            'susceptible': 0,
            'infected': 0,
            'recovered': 0,
            'dead': 0
        }
        for agent in self.agents:
            counts[agent.state] += 1
        return counts

    def render(self):
        """Render all simulation elements."""
        screen.fill(BACKGROUND_COLOR)
        
        # Draw separator
        pygame.draw.line(screen, TEXT_COLOR, 
                        (WIDTH - GRAPH_WIDTH, 0), (WIDTH - GRAPH_WIDTH, HEIGHT), 2)
        
        # Draw quarantine zones
        for zone in self.quarantine_zones:
            zone.draw()
        
        # Draw agents
        for agent in self.agents:
            agent.draw()
        
        # Draw UI
        self.draw_ui()
        
        # Draw graphs
        self.tracker.draw(screen, WIDTH - GRAPH_WIDTH + 10, 100)
        
        pygame.display.flip()

    def draw_ui(self):
        """Draw user interface."""
        y_offset = 10
        line_height = 22
        
        # Title
        scenario_name = "EXTINCTION" if self.scenario == 'extinction' else "SURVIVAL"
        title = TITLE_FONT.render(f"EPIDEMIC SIR MODEL - {scenario_name} SCENARIO", 
                                 True, TEXT_COLOR)
        screen.blit(title, (10, y_offset))
        y_offset += line_height + 5
        
        # Statistics
        counts = self.count_states()
        vaccinated_count = sum(1 for a in self.agents if a.vaccinated)
        
        stats = [
            f"Susceptible: {counts['susceptible']} ({vaccinated_count} vaccinated)",
            f"Infected: {counts['infected']}",
            f"Recovered: {counts['recovered']}",
            f"Dead: {counts['dead']}",
            f"Total Alive: {len(self.agents) - counts['dead']}",
        ]
        
        for i, stat in enumerate(stats):
            if i == 0:
                color = SUSCEPTIBLE_COLOR
            elif i == 1:
                color = INFECTED_COLOR
            elif i == 2:
                color = RECOVERED_COLOR
            elif i == 3:
                color = (150, 150, 150)
            else:
                color = TEXT_COLOR
            
            text = FONT.render(stat, True, color)
            screen.blit(text, (10, y_offset))
            y_offset += line_height
        
        y_offset += 10
        
        # Parameters
        params = [
            f"Infection Rate: {self.infection_rate:.1f}x (UP/DOWN)",
            f"Recovery Rate: {self.recovery_rate:.1f}x (LEFT/RIGHT)",
            f"Recovery Chance: {RECOVERY_PROBABILITY:.0%}",
            f"Auto-Vaccinate: {'ON' if self.auto_vaccinate else 'OFF'} (SPACE)",
            f"Quarantine Zones: {len(self.quarantine_zones)}",
        ]
        
        for param in params:
            text = FONT.render(param, True, (150, 200, 255))
            screen.blit(text, (10, y_offset))
            y_offset += line_height
        
        y_offset += 10
        
        # Controls
        controls = [
            "Controls:",
            "S - Add Susceptible",
            "I - Add Infected",
            "R - Add Recovered",
            "V - Vaccinate (10 random)",
            "Q - Toggle Quarantine Zone",
            "1/2 - Switch Scenario",
            "ESC - Exit",
        ]
        
        for control in controls:
            text = FONT.render(control, True, (200, 200, 150))
            screen.blit(text, (10, y_offset))
            y_offset += line_height
        
        # Scenario outcomes
        y_offset += 10
        outcome_title = FONT.render("Scenario Goal:", True, (255, 200, 100))
        screen.blit(outcome_title, (10, y_offset))
        y_offset += line_height
        
        if self.scenario == 'extinction':
            outcome = FONT.render("All agents die (virus overwhelms)", True, (255, 100, 100))
        else:
            outcome = FONT.render("Some survive, virus disappears", True, (100, 255, 100))
        screen.blit(outcome, (10, y_offset))


if __name__ == "__main__":
    print("Starting Epidemic Simulation (SIR Model)...")
    print("\nScenario 1 (Press 1): Extinction - All agents die")
    print("Scenario 2 (Press 2): Survival - Some agents survive\n")
    print("Adjust parameters to observe different outcomes!\n")
    
    simulation = Simulation(scenario='survival')
    simulation.run()
