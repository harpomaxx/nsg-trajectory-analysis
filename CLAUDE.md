# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This directory contains trajectory analysis tools for NetSecGame episodes stored in JSONL format. Each JSONL file contains episodes where an AI agent (attacker) attempts to navigate a network security game environment.

## Analysis Tools

### Quick Analysis Commands

```bash
# Get summary statistics (win rate, avg reward, avg steps to win)
python3 summary.py *.jsonl

# Detailed episode breakdown with win/loss indicators
python3 count_episodes.py *.jsonl

# Inspect JSONL structure and schema
python3 analyze_jsonl.py <file.jsonl> --max-lines 100

# Deep dive into specific episodes
python3 investigate_end_condition.py <file.jsonl> --episodes 1 5 10
```

### Tool Descriptions

- **summary.py**: Primary tool for quick performance metrics (excludes no-action episodes)
- **count_episodes.py**: Comprehensive episode counter with detailed per-episode breakdowns
- **analyze_jsonl.py**: Schema analyzer for understanding JSONL structure
- **investigate_end_condition.py**: Deep inspector for examining individual episode details

All scripts support `--json` flag for programmatic output.

## Episode Data Structure

### JSONL Format
Each line = one episode with structure:
```json
{
  "agent_name": "BaseAgent",
  "agent_role": "Attacker",
  "end_reason": null,
  "trajectory": {
    "states": [...],    // Array of game states (length N+1)
    "actions": [...],   // Array of actions taken (length N)
    "rewards": [...]    // Array of rewards received (length N)
  }
}
```

### Win/Loss Detection
- **Win**: Final reward >= 50 (typically 99 for successful data exfiltration)
- **Loss**: Final reward = -1 (hit step limit or failed objective)
- **No Action**: Empty actions array (invalid episodes, should be excluded from analysis)

### Action Types
- `ScanNetwork`: Discover hosts on a network
- `FindServices`: Enumerate services on a host
- `ExploitService`: Gain control of a host
- `FindData`: Search for data on a controlled host
- `ExfiltrateData`: Extract data to win (only wins if correct data)

### State Fields
- `known_networks`: Discovered networks (IP/mask)
- `known_hosts`: Discovered hosts (IP)
- `controlled_hosts`: Hosts under attacker control
- `known_services`: Services indexed by host IP
- `known_data`: Data objects indexed by host IP
- `known_blocks`: Network blocks

## Key Metrics

From current dataset analysis:
- Win rate: ~31% (excluding no-action episodes)
- Average steps to win: ~33 actions
- Average steps in loss: ~72 actions (near step limit)
- All wins end with `ExfiltrateData` action
- Step penalty: -1 per action
- Win reward: +99

## Development Notes

### Adding New Analysis Tools
- Use JSON parsing with error handling for malformed lines
- Always skip episodes with `len(actions) == 0` for performance metrics
- Episode outcome determined by `rewards[-1]` value
- Use defaultdict for aggregating statistics across episodes

### Common Patterns
```python
# Skip no-action episodes
if len(actions) == 0:
    continue

# Detect outcome
if rewards and rewards[-1] >= 50:
    outcome = 'win'
else:
    outcome = 'loss'

# Read JSONL
with open(filepath, 'r') as f:
    for line in f:
        episode = json.loads(line.strip())
```
