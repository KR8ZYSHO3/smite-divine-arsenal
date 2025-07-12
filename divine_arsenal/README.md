# Divine Arsenal

A comprehensive Smite 2 companion tool that enhances gameplay beyond basic stats tracking. Divine Arsenal provides advanced features like patch impact analysis, build optimization, and real-time game insights.

## Features

### MVP Phase
- **Patch Impact Tracker**
  - Automated scraping of Smite2.com patch notes
  - Historical patch data storage and analysis
  - Version comparison and impact assessment

- **Casual Player Companion**
  - Simplified god guides and tips
  - Basic build recommendations
  - Player statistics tracking

### Future Phases
- **Build Optimizer**
  - Meta build analysis
  - Counter-build suggestions
  - Item synergy recommendations

- **God Matchup Analyzer**
  - Detailed god-vs-god statistics
  - Counter-pick suggestions
  - Win rate analysis

- **Live Game Overlay**
  - Real-time build suggestions
  - Enemy player statistics
  - Objective timers

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/divine-arsenal.git
   cd divine-arsenal
   ```

2. Set up Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

4. Run the backend:
   ```bash
   cd backend
   python app.py
   ```

## API Endpoints

### Patches
- `GET /api/patches` - Get all stored patches
- `GET /api/patches/<version>` - Get specific patch
- `POST /api/patches/update` - Update patches from Smite2.com

### Player Stats
- `GET /api/player/<player_name>` - Get player statistics
- `GET /api/leaderboard` - Get leaderboard data

## Development Roadmap

### Phase 1: MVP (Current)
- [x] Basic project structure
- [x] Patch notes scraper
- [x] Player stats integration
- [ ] Basic API endpoints
- [ ] SQLite database setup

### Phase 2: Expansion
- [ ] Build optimizer implementation
- [ ] God matchup analysis
- [ ] Enhanced player statistics
- [ ] User preferences and settings

### Phase 3: Advanced Features
- [ ] Live game overlay
- [ ] Real-time build suggestions
- [ ] Advanced analytics
- [ ] Community features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Smite 2 community for inspiration
- Tracker.gg for data integration
- SmiteFire and other community resources
