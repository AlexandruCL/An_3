import pygame
import numpy as np
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Simulation parameters
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)


class Obstacle:
    """Static or dynamic obstacle in the simulation."""
    def __init__(self, position: np.ndarray, radius: float, velocity: np.ndarray = None):
        self.position = np.array(position, dtype='float64')
        self.radius = radius
        self.velocity = np.array(velocity, dtype='float64') if velocity is not None else np.zeros(2)
        self.is_dynamic = velocity is not None
    
    def update(self, width: int, height: int):
        """Update obstacle position if dynamic."""
        if self.is_dynamic:
            self.position += self.velocity
            # Bounce off walls
            if self.position[0] < self.radius or self.position[0] > width - self.radius:
                self.velocity[0] *= -1
            if self.position[1] < self.radius or self.position[1] > height - self.radius:
                self.velocity[1] *= -1
    
    def draw(self, surface):
        """Draw the obstacle."""
        color = RED if self.is_dynamic else YELLOW
        pygame.draw.circle(surface, color, self.position.astype(int), int(self.radius))


class EnhancedBoid:
    """Enhanced Boid with leader capability and obstacle avoidance."""
    def __init__(self, position: np.ndarray, velocity: np.ndarray, is_leader: bool = False):
        self.position = np.array(position, dtype='float64')
        self.velocity = np.array(velocity, dtype='float64')
        self.is_leader = is_leader
        self.max_speed = 4.0 if is_leader else 2.0
        self.min_speed = 0.5
    
    def separation(self, boids: List, separation_distance: float = 25):
        """Calculate separation steering vector."""
        steer = np.zeros(2)
        count = 0
        for other in boids:
            distance = np.linalg.norm(self.position - other.position)
            if 0 < distance < separation_distance:
                diff = self.position - other.position
                diff /= distance  # Weight by distance
                steer += diff
                count += 1
        if count > 0:
            steer /= count
        return steer
    
    def alignment(self, boids: List, neighbor_distance: float = 50):
        """Calculate alignment steering vector."""
        avg_velocity = np.zeros(2)
        count = 0
        for other in boids:
            distance = np.linalg.norm(self.position - other.position)
            if 0 < distance < neighbor_distance:
                avg_velocity += other.velocity
                count += 1
        if count > 0:
            avg_velocity /= count
            return avg_velocity - self.velocity
        return np.zeros(2)
    
    def cohesion(self, boids: List, neighbor_distance: float = 50):
        """Calculate cohesion steering vector."""
        center_of_mass = np.zeros(2)
        count = 0
        for other in boids:
            distance = np.linalg.norm(self.position - other.position)
            if 0 < distance < neighbor_distance:
                center_of_mass += other.position
                count += 1
        if count > 0:
            center_of_mass /= count
            return center_of_mass - self.position
        return np.zeros(2)
    
    def avoid_obstacles(self, obstacles: List[Obstacle], avoidance_distance: float = 80):
        """Calculate obstacle avoidance steering vector."""
        steer = np.zeros(2)
        for obstacle in obstacles:
            distance = np.linalg.norm(self.position - obstacle.position) - obstacle.radius
            if distance < avoidance_distance:
                diff = self.position - obstacle.position
                if np.linalg.norm(diff) > 0:
                    diff = diff / np.linalg.norm(diff)
                    # Stronger avoidance when closer
                    strength = (avoidance_distance - distance) / avoidance_distance
                    steer += diff * strength * 2
        return steer
    
    def follow_leader(self, leader, follow_distance: float = 100):
        """Follow a leader boid."""
        if leader and not self.is_leader:
            distance = np.linalg.norm(self.position - leader.position)
            if distance > follow_distance:
                return (leader.position - self.position) * 0.5
        return np.zeros(2)
    
    def apply_behaviors(self, boids: List, obstacles: List[Obstacle] = None, 
                       leader = None, separation_weight: float = 1.5,
                       alignment_weight: float = 1.0, cohesion_weight: float = 1.0,
                       obstacle_weight: float = 2.5, leader_weight: float = 0.8):
        """Apply all flocking behaviors with adjustable weights."""
        sep = self.separation(boids) * separation_weight
        ali = self.alignment(boids) * alignment_weight
        coh = self.cohesion(boids) * cohesion_weight
        
        # Add obstacle avoidance
        obs = np.zeros(2)
        if obstacles:
            obs = self.avoid_obstacles(obstacles) * obstacle_weight
        
        # Add leader following
        lead = np.zeros(2)
        if leader:
            lead = self.follow_leader(leader) * leader_weight
        
        # Apply all forces
        self.velocity += sep + ali + coh + obs + lead
        
        # Variable speed based on local density
        local_density = self.calculate_local_density(boids)
        dynamic_max_speed = self.max_speed * (1.5 - local_density)
        
        self.limit_speed(dynamic_max_speed)
    
    def calculate_local_density(self, boids: List, radius: float = 50) -> float:
        """Calculate local flock density (0 to 1)."""
        count = sum(1 for other in boids 
                   if 0 < np.linalg.norm(self.position - other.position) < radius)
        return min(count / 10.0, 1.0)
    
    def limit_speed(self, max_speed: float):
        """Limit speed with minimum threshold."""
        speed = np.linalg.norm(self.velocity)
        if speed > max_speed:
            self.velocity = (self.velocity / speed) * max_speed
        elif speed < self.min_speed and speed > 0:
            self.velocity = (self.velocity / speed) * self.min_speed
    
    def update_position(self, width: int, height: int, radius: int = 3):
        """Update position with boundary bouncing."""
        self.position += self.velocity
        
        if self.position[0] < radius:
            self.position[0] = radius
            self.velocity[0] *= -1
        elif self.position[0] > width - radius:
            self.position[0] = width - radius
            self.velocity[0] *= -1
        
        if self.position[1] < radius:
            self.position[1] = radius
            self.velocity[1] *= -1
        elif self.position[1] > height - radius:
            self.position[1] = height - radius
            self.velocity[1] *= -1
    
    def draw(self, surface):
        """Draw the boid with color based on speed or leader status."""
        if self.is_leader:
            color = GREEN
            radius = 6
        else:
            # Color by speed (blue = slow, red = fast)
            speed = np.linalg.norm(self.velocity)
            speed_ratio = min(speed / self.max_speed, 1.0)
            red = int(255 * speed_ratio)
            blue = int(255 * (1 - speed_ratio))
            color = (red, 0, blue)
            radius = 4
        
        pygame.draw.circle(surface, color, self.position.astype(int), radius)


class BoidSimulation:
    """Main simulation class with interactive controls."""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Enhanced Boids Simulation - Use Arrow Keys for Controls')
        self.clock = pygame.time.Clock()
        
        # Simulation parameters (adjustable)
        self.separation_weight = 1.5
        self.alignment_weight = 0.5
        self.cohesion_weight = 0.5
        self.obstacle_weight = 2.5
        
        # Initialize boids
        num_boids = 40
        self.boids = []
        for i in range(num_boids):
            is_leader = i == 0  # First boid is leader
            boid = EnhancedBoid(
                position=np.random.rand(2) * [WINDOW_WIDTH, WINDOW_HEIGHT],
                velocity=np.random.rand(2) * 2 - 1,
                is_leader=is_leader
            )
            self.boids.append(boid)
        
        # Initialize obstacles
        self.obstacles = [
            Obstacle([300, 300], 40),  # Static obstacle
            Obstacle([600, 400], 30),  # Static obstacle
            Obstacle([500, 200], 25, velocity=np.array([0.5, 0.3]))  # Dynamic obstacle
        ]
        
        self.running = True
        self.paused = False
    
    def handle_events(self):
        """Handle keyboard and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_UP:
                    self.separation_weight += 0.1
                elif event.key == pygame.K_DOWN:
                    self.separation_weight = max(0, self.separation_weight - 0.1)
                elif event.key == pygame.K_RIGHT:
                    self.alignment_weight += 0.1
                elif event.key == pygame.K_LEFT:
                    self.alignment_weight = max(0, self.alignment_weight - 0.1)
                elif event.key == pygame.K_w:
                    self.cohesion_weight += 0.1
                elif event.key == pygame.K_s:
                    self.cohesion_weight = max(0, self.cohesion_weight - 0.1)
    
    def update(self):
        """Update simulation state."""
        if not self.paused:
            leader = self.boids[0] if self.boids else None
            
            for boid in self.boids:
                boid.apply_behaviors(
                    self.boids, 
                    self.obstacles,
                    leader if not boid.is_leader else None,
                    self.separation_weight,
                    self.alignment_weight,
                    self.cohesion_weight,
                    self.obstacle_weight
                )
                boid.update_position(WINDOW_WIDTH, WINDOW_HEIGHT)
            
            for obstacle in self.obstacles:
                obstacle.update(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    def draw(self):
        """Draw all simulation elements."""
        self.screen.fill(BLACK)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw boids
        for boid in self.boids:
            boid.draw(self.screen)
        
        # Draw UI text
        font = pygame.font.Font(None, 24)
        info_text = [
            f"Separation: {self.separation_weight:.1f} (↑↓)",
            f"Alignment: {self.alignment_weight:.1f} (←→)",
            f"Cohesion: {self.cohesion_weight:.1f} (W/S)",
            "SPACE: Pause/Resume"
        ]
        
        y_offset = 10
        for text in info_text:
            surface = font.render(text, True, WHITE)
            self.screen.blit(surface, (10, y_offset))
            y_offset += 25
        
        if self.paused:
            pause_text = font.render("PAUSED", True, RED)
            self.screen.blit(pause_text, (WINDOW_WIDTH // 2 - 40, 10))
        
        pygame.display.flip()
    
    def run(self):
        """Main simulation loop."""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()


if __name__ == "__main__":
    simulation = BoidSimulation()
    simulation.run()