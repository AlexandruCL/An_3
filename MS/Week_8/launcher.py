"""
MS Lab 6 - Project Launcher
Launches both simulation projects with a menu interface
"""

import subprocess
import sys

def print_menu():
    print("\n" + "="*60)
    print("  MS LAB 6 - MODELING AND SIMULATION PROJECT")
    print("  Both Options Implemented for Extra Points")
    print("="*60)
    print("\n1. Advanced Predator-Prey Simulation")
    print("   - Reproduction, Energy, Food, Flocking, Obstacles")
    print("   - Population tracking and birth rates")
    print("   - Goal: Achieve stable ecosystem")
    print("\n2. Epidemic Simulation (SIR Model)")
    print("   - Infection, Recovery, Quarantine, Vaccination")
    print("   - Two scenarios: Extinction vs Survival")
    print("   - Goal: Observe epidemic dynamics")
    print("\n3. Install Requirements (pygame, matplotlib, numpy)")
    print("\n4. Exit")
    print("\n" + "="*60)

def install_requirements():
    print("\nInstalling required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n✅ Requirements installed successfully!")
    except Exception as e:
        print(f"\n❌ Error installing requirements: {e}")

def run_predator_prey():
    print("\n🦌 Launching Predator-Prey Simulation...")
    print("Controls: P=Add Prey, O=Add Predator, F=Food, B=Obstacle")
    print("          UP/DOWN=Reproduction, LEFT/RIGHT=Energy, SPACE=Flocking\n")
    try:
        subprocess.run([sys.executable, "project_option1_advanced_predator_prey.py"])
    except Exception as e:
        print(f"\n❌ Error: {e}")

def run_epidemic():
    print("\n🦠 Launching Epidemic Simulation...")
    print("Controls: S/I/R=Add Agents, V=Vaccinate, Q=Quarantine")
    print("          1=Extinction, 2=Survival, SPACE=Auto-Vaccinate\n")
    try:
        subprocess.run([sys.executable, "project_option2_epidemic_sir_model.py"])
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    while True:
        print_menu()
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            run_predator_prey()
        elif choice == '2':
            run_epidemic()
        elif choice == '3':
            install_requirements()
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    print("\n🎓 Student: Alexandru CL")
    print("📚 Course: Modeling and Simulation (Year 3)")
    print("📅 Date: November 23, 2025\n")
    main()
