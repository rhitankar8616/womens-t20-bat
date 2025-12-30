# Women's T20s: Batting Analysis

A comprehensive Streamlit web application for analyzing ball-by-ball batting data in women's T20 cricket matches.

## Features

- **Line-Length wise Analysis**: Pitchmaps and statistics broken down by bowling line and length
- **Bowler wise Performance**: Detailed performance metrics against each bowler
- **Shots Analysis**: Breakdown of all shot types with effectiveness metrics
- **Shot Areas**: Analysis by fielding position/zone
- **Ball Type Specific**: Statistics by ball variation, detailed ball types, and bowler types
- **Wagon Wheels**: Coming soon!
- **Innings Progression**: Rolling window analysis of batting performance through an innings
- **Feet Movement**: Analysis of footwork patterns and their effectiveness
- **Dismissals**: Breakdown of dismissal types by variation and bowler

## Structure

```
wt20-bat/
├── main.py                     # Main Streamlit entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── config/
│   ├── __init__.py
│   └── settings.py             # App-wide settings and configurations
├── data/
│   ├── README.md               # Data folder instructions
│   └── wt20.csv                # Your data file (place here)
├── utils/
│   ├── __init__.py
│   ├── data_loader.py          # Data loading and caching functions
│   ├── filters.py              # Filter widget creation and application
│   └── calculations.py         # Statistical calculations and metrics
├── components/
│   ├── __init__.py
│   ├── header.py               # Header and navigation components
│   ├── sidebar.py              # Sidebar with batter selection and filters
│   ├── footer.py               # Footer with developer info and social links
│   ├── tables.py               # Table rendering components
│   └── pitchmap.py             # Pitchmap visualization component
├── pages/
│   ├── __init__.py
│   ├── home.py                 # Introductory/home page
│   ├── line_length.py          # Line-Length wise analysis
│   ├── bowler_wise.py          # Bowler wise performance
│   ├── shots_analysis.py       # Shots analysis breakdown
│   ├── shot_areas.py           # Shot areas/fielding positions
│   ├── ball_type.py            # Ball type specific analysis
│   ├── wagon_wheels.py         # Wagon wheels (coming soon)
│   ├── innings_progression.py  # Innings progression analysis
│   ├── feet_movement.py        # Feet movement analysis
│   └── dismissals.py           # Dismissals analysis
└── assets/
    └── style.css               # Custom CSS for dark theme
```

## Installation

1. Clone or download this repository
2. Navigate to the project folder:
   ```bash
   cd wt20-bat
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Place your `wt20.csv` data file in the `data/` folder

## Data Requirements

Your CSV file should contain the following columns:
- `fixtureId`, `matchDate`, `ground`, `country`
- `inns`, `battingTeam`, `bowlingTeam`
- `batsman`, `bowler`, `batsmanHand`, `bowlerHand`, `bowlerType`, `bowlingAngle`
- `over`, `ball`, `dismissalType`
- `parsed_length`, `parsed_line`, `parsed_control`, `control`
- `elevation`, `variation`, `parsed_len.var`
- `shot_type`, `shot_angle`, `shot_magnitude`, `fielding_position`
- `foot`, `runs_scored`, `is_wicket`
- `timestamp`, `competition`

## Key Metrics

- **eSR (Effective Strike Rate)**: Batter's SR compared to average batter in selected matches
- **eControl (Effective Control)**: Batter's control % compared to average batter
- **eAerial (Effective Aerial %)**: Batter's aerial shot % compared to average batter

Positive values (shown in green) indicate better than average performance.
Negative values (shown in red) indicate below average performance.
