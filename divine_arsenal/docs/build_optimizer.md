# Build Optimizer Documentation

## Overview
The Build Optimizer is a sophisticated tool designed to analyze and optimize item builds for Smite gods. It takes into account various factors including role-specific requirements, enemy composition, item synergy, and power spikes to provide optimal build recommendations.

## Core Components

### ItemStats Class
A specialized class for handling item statistics with dictionary-like behavior.

```python
class ItemStats:
    def __init__(self, stats_dict: Dict[str, float])
    def __getattr__(self, name: str) -> float
    def __getitem__(self, key: str) -> float
    def to_dict(self) -> Dict[str, float]
```

### Build Class
Represents a complete item build with items and their combined statistics.

```python
class Build:
    def __init__(self, items: List[Item], total_cost: float)
    def __post_init__(self)
    @property
    def stats_summary(self) -> ItemStats
```

### BuildOptimizer Class
The main class responsible for build analysis and optimization.

## Key Features

### 1. Role-Based Analysis
The optimizer considers role-specific requirements using predefined weights for different stats:
- Warrior: Balanced physical power, protections, and health
- Guardian: High protections and health
- Mage: High magical power and penetration
- Hunter: High physical power and attack speed
- Assassin: High physical power and penetration

### 2. Enemy Composition Countering
The optimizer analyzes enemy team composition to recommend counter items:
- Calculates counter scores based on enemy damage types
- Suggests appropriate protections and utility items
- Considers both physical and magical threats

### 3. Item Synergy Analysis
Evaluates how well items work together:
- Checks for complementary stats
- Considers shared categories and tags
- Calculates overall build synergy score

### 4. Power Spike Analysis
Analyzes build power progression:
- Early game power (first 2 items)
- Mid game power (items 3-4)
- Late game power (items 5-6)
- Weighted scoring based on timing

### 5. Cost Efficiency
Evaluates build cost-effectiveness:
- Calculates total stats per gold spent
- Considers item cost-to-stat ratios
- Helps optimize gold efficiency

## Usage Examples

### Basic Build Analysis
```python
optimizer = BuildOptimizer()
build = Build([item1, item2, item3], total_cost=5400)
analysis = optimizer.analyze_build(build, "Thor", "Assassin")
```

### Getting Optimal Build
```python
optimal_build = optimizer.get_optimal_build(
    god_name="Thor",
    role="Assassin",
    enemy_comp=["Mage", "Hunter", "Guardian", "Warrior", "Assassin"]
)
```

### Saving and Loading Builds
```python
# Save a build
optimizer.save_build(build, "Thor", "Assassin")

# Load a build
saved_build = optimizer.get_saved_build("Thor", "Assassin")
```

## Analysis Output
The `analyze_build` method returns a dictionary with the following metrics:
- `role_fit`: How well the build fits the god's role (0.0-1.0)
- `counter_score`: Effectiveness against enemy composition (0.0-1.0)
- `synergy_score`: How well items work together (0.0-1.0)
- `power_spike`: Build's power progression (0.0-1.0)
- `cost_efficiency`: Gold efficiency of the build (0.0-1.0)
- `total_cost`: Total gold cost of the build

## Best Practices
1. Always consider enemy composition when building
2. Balance early and late game power spikes
3. Ensure proper item synergy
4. Maintain cost efficiency
5. Adapt builds to specific matchups

## Limitations
1. Build optimization is based on statistical analysis and may not account for all situational factors
2. Some god-specific mechanics may require specialized builds
3. Meta changes may affect optimal builds
4. Team composition and strategy may influence build choices

## Future Improvements
1. Add support for situational item recommendations
2. Implement meta-based build adjustments
3. Add support for team composition synergy
4. Include god-specific build templates
5. Add support for counter-building against specific gods 