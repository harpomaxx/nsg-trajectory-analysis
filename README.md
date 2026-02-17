# Episode Analysis Tools

This directory contains tools for analyzing JSONL trajectory files from the NetSecGame.

## Analysis Scripts

### 1. `analyze_jsonl.py` - Structure Analyzer
Analyzes the schema and structure of JSONL files.

**Usage:**
```bash
python3 analyze_jsonl.py <file.jsonl> [--max-lines N]
```

**Features:**
- Extracts field types and nested structures
- Shows sample records
- Displays example values

### 2. `count_episodes.py` - Episode Counter
Counts episodes and provides detailed statistics including win/loss outcomes.

**Usage:**
```bash
# Basic analysis
python3 count_episodes.py *.jsonl

# JSON output
python3 count_episodes.py *.jsonl --json
```

**Features:**
- Episode count by file, agent, and role
- Win/loss detection based on final reward
- Final action analysis
- Detailed per-episode statistics

### 3. `investigate_end_condition.py` - Deep Episode Inspector
Deep dive into specific episodes to investigate end conditions.

**Usage:**
```bash
# Investigate sample episodes (default)
python3 investigate_end_condition.py <file.jsonl>

# Investigate specific episodes
python3 investigate_end_condition.py <file.jsonl> --episodes 1 5 10

# Investigate all episodes
python3 investigate_end_condition.py <file.jsonl> --all
```

### 4. `repeated_actions.py` - Repeated Action Analyzer
Detects and quantifies actions executed more than once within an episode.

**Usage:**
```bash
python3 repeated_actions.py *.jsonl
python3 repeated_actions.py *.jsonl --csv repeated_actions.csv   # export CSV for R plots
python3 repeated_actions.py *.jsonl --json                        # JSON output
```

**Features:**
- Counts distinct repeated actions and total extra executions per episode
- Splits statistics by outcome (win/loss)
- Exports a flat CSV for downstream plotting

### 5. `repeated_actions_plots.R` / `plot_repeated_actions.rmd` - R Visualizations
Two R-based plotting tools that consume the CSV produced by `repeated_actions.py --csv`.

| File | Type | Output |
|---|---|---|
| `repeated_actions_plots.R` | Standalone script | 4 PNG files (300 dpi) |
| `plot_repeated_actions.rmd` | R Notebook | Interactive HTML |

**Usage (`repeated_actions_plots.R`):**
```bash
python3 repeated_actions.py *.jsonl --csv repeated_actions.csv
Rscript repeated_actions_plots.R repeated_actions.csv [output_prefix]
```

Plots generated: boxplot of total repetitions by outcome, boxplot of distinct repeated actions by outcome, histogram of total repetitions faceted by outcome, scatter of total actions vs. repetitions coloured by outcome.

## Current Dataset Summary

**Total Episodes: 35**
- 34 episodes in `2025-09-26_BaseAgent_Attacker.jsonl`
- 1 episode in `2025-09-27_BaseAgent_Attacker.jsonl`

### Win/Loss Breakdown
- **Wins: 9 episodes (25.7%)**
- **Losses: 20 episodes (57.1%)**
- **No Action: 6 episodes (17.1%)**

### Key Findings

1. **Win Condition**: Episodes end with a **reward of 99** when the agent successfully exfiltrates data
   - All 9 winning episodes end with `ActionType.ExfiltrateData`
   - Win reward is always 99

2. **Loss Condition**: Episodes end with a **reward of -1** when:
   - Agent hits step limit (typically 80-100 steps)
   - Agent fails to exfiltrate the correct data

3. **No Action**: 6 episodes where the agent took 0 actions (initial state only)

### Performance Metrics

**Winning Episodes:**
- Average steps to win: 29.1 actions
- Fastest win: 16 actions (Episode 31)
- Slowest win: 78 actions (Episode 34)
- Average total reward: 71.3

**Losing Episodes:**
- Average steps: 70.9 actions
- All losses hit or nearly hit the step limit
- Average total reward: -72.9

### Final Action Distribution

For episodes with actions (29 episodes):
- **ExfiltrateData**: 14 episodes (9 wins, 5 losses)
- **FindData**: 11 episodes (all losses)
- **ScanNetwork**: 3 episodes (all losses)
- **FindServices**: 1 episode (loss)

**Insight**: Exfiltrating data is the most common final action, but doesn't guarantee success. Successful exfiltration requires the *correct* data.

## Data Structure

### Episode Format
Each line in the JSONL file represents one episode:

```json
{
  "agent_name": "BaseAgent",
  "agent_role": "Attacker",
  "end_reason": null,
  "trajectory": {
    "states": [...],
    "actions": [...],
    "rewards": [...]
  }
}
```

### State Structure
Each state contains:
- `known_networks`: Networks discovered
- `known_hosts`: Hosts discovered
- `controlled_hosts`: Hosts under attacker control
- `known_services`: Services discovered (indexed by host IP)
- `known_data`: Data found (indexed by host IP)
- `known_blocks`: Network blocks

### Action Structure
Each action contains:
- `action_type`: Type of action (ScanNetwork, FindServices, ExploitService, FindData, ExfiltrateData)
- `parameters`: Action-specific parameters (source_host, target_host, target_network, target_service, data)

### Rewards
- Each action receives a reward
- Default reward per step: -1 (time penalty)
- Successful exfiltration: +99
- Total reward = sum of all step rewards
