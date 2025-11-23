# 🎓 MS Lab 6 - Quick Start Guide

## ⚡ Fast Setup (3 Steps)

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Run Projects

**Option A: Use the Launcher (Recommended)**
```bash
python launcher.py
```

**Option B: Run Directly**
```bash
# Predator-Prey Simulation
python project_option1_advanced_predator_prey.py

# Epidemic Simulation
python project_option2_epidemic_sir_model.py
```

---

## 🎮 Controls Cheat Sheet

### Predator-Prey Simulation
| Key | Action |
|-----|--------|
| `P` | Add prey |
| `O` | Add predator |
| `F` | Add food |
| `B` | Add obstacle |
| `↑↓` | Adjust reproduction rate |
| `←→` | Adjust energy consumption |
| `SPACE` | Toggle flocking |
| `ESC` | Exit |

**Goal:** Achieve stable population where both species survive!

---

### Epidemic Simulation
| Key | Action |
|-----|--------|
| `S` | Add susceptible agent |
| `I` | Add infected agent |
| `R` | Add recovered agent |
| `V` | Vaccinate 10 agents |
| `Q` | Add quarantine zone |
| `↑↓` | Adjust infection rate |
| `←→` | Adjust recovery rate |
| `SPACE` | Auto-vaccinate mode |
| `1` | Extinction scenario |
| `2` | Survival scenario |
| `ESC` | Exit |

**Goal:** Observe both extinction and survival outcomes!

---

## 📊 What to Observe

### Predator-Prey
- ✅ Population cycles (peaks and valleys)
- ✅ Predator-prey lag (predators peak after prey)
- ✅ Flocking improves prey survival
- ✅ Energy system creates natural limits
- ✅ Stable equilibrium at balanced parameters

**Stable Settings:**
- Reproduction: 1.0-1.2x
- Energy consumption: 0.8-1.0x
- Flocking: ON

### Epidemic
- ✅ Classic SIR curve (S drops, I peaks, R rises)
- ✅ Quarantine flattens infection curve
- ✅ Vaccination prevents epidemic
- ✅ Herd immunity threshold
- ✅ Extinction vs survival based on parameters

**Extinction Settings (Scenario 1):**
- Infection: 2.5x
- Recovery: 0.3x
- Result: All die

**Survival Settings (Scenario 2):**
- Infection: 1.0x
- Recovery: 1.5x
- Vaccination: ON
- Result: Some survive, virus disappears

---

## 🏆 Extra Points Features Checklist

### Both Projects ✅
- [x] Clean, documented code
- [x] Object-oriented design
- [x] Real-time visualization
- [x] Interactive controls (3+)
- [x] Population tracking
- [x] Professional graphs

### Predator-Prey ✅
- [x] Reproduction mechanics
- [x] Energy system
- [x] Food resources
- [x] Flocking behavior
- [x] Obstacle avoidance
- [x] Birth rate tracking
- [x] 7 interactive controls

### Epidemic ✅
- [x] SIR state model
- [x] Probabilistic infection
- [x] Recovery/death outcomes
- [x] Quarantine zones
- [x] Vaccination strategy
- [x] Infection/recovery rate tracking
- [x] Two scenarios (extinction/survival)
- [x] 10 interactive controls

---

## 💡 Tips for Best Results

1. **Let it run!** Systems need time to reach equilibrium
2. **Experiment!** Try extreme parameters to see what breaks
3. **Watch graphs!** They reveal hidden patterns
4. **Find balance!** Stable systems are most interesting
5. **Compare scenarios!** See how small changes create big effects

---

## 🐛 Troubleshooting

**Simulation runs slow?**
- Close other programs
- Reduce initial agent counts in code

**Graphs not showing?**
- Ensure matplotlib is installed: `pip install matplotlib`

**Import errors?**
- Run: `pip install -r requirements.txt`

**Window too small?**
- Simulation needs 1200x800 minimum resolution

---

## 📚 Files in This Project

```
Week_8/
├── launcher.py                              # Menu launcher (start here!)
├── project_option1_advanced_predator_prey.py  # Option 1 implementation
├── project_option2_epidemic_sir_model.py      # Option 2 implementation
├── requirements.txt                         # Dependencies
├── PROJECT_README.md                        # Full documentation
├── QUICKSTART.md                           # This file
├── MS_Lab_6.ipynb                          # Original lab notebook
└── 01-05_*.py                              # Lab progression files
```

---

## 🎯 Academic Goals Demonstrated

1. **Agent-Based Modeling** - Emergent complexity from simple rules
2. **State Machines** - SIR states, energy levels, reproduction
3. **Probability Theory** - Infection chances, recovery outcomes
4. **System Dynamics** - Population cycles, epidemic curves
5. **Data Visualization** - Real-time graphs and statistics
6. **Software Engineering** - Clean OOP design, documentation

---

## 🚀 Ready to Run?

```bash
python launcher.py
```

**Choose wisely:**
- Want to see nature's balance? → Predator-Prey
- Want to model disease spread? → Epidemic

**Or run both and compare emergent behaviors!**

---

**Good luck and enjoy exploring complex systems! 🧪📊🎮**
