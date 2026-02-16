#!/usr/bin/env python3
"""
Episode Counter for JSONL Trajectory Files
Analyzes JSONL files to count episodes and provide statistics.
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def analyze_episode(episode_data):
    """Extract key statistics from an episode."""
    stats = {
        'num_states': 0,
        'num_actions': 0,
        'num_rewards': 0,
        'total_reward': 0,
        'controlled_hosts': set(),
        'known_hosts': set(),
        'known_networks': set(),
        'end_reason': episode_data.get('end_reason'),
        'agent_name': episode_data.get('agent_name'),
        'agent_role': episode_data.get('agent_role'),
        'outcome': 'unknown',
        'final_reward': None,
        'final_action': None,
    }

    trajectory = episode_data.get('trajectory', {})

    # Count states
    states = trajectory.get('states', [])
    stats['num_states'] = len(states)

    # Count actions
    actions = trajectory.get('actions', [])
    stats['num_actions'] = len(actions)

    # Count and sum rewards
    rewards = trajectory.get('rewards', [])
    stats['num_rewards'] = len(rewards)
    stats['total_reward'] = sum(rewards) if rewards else 0

    # Determine outcome based on final reward
    if rewards:
        stats['final_reward'] = rewards[-1]
        # Large positive reward (e.g., 99, 100) indicates success/win
        if rewards[-1] >= 50:
            stats['outcome'] = 'win'
        else:
            stats['outcome'] = 'loss'
    else:
        stats['outcome'] = 'no_action'

    # Get final action type
    if actions:
        stats['final_action'] = actions[-1].get('action_type', 'unknown')

    # Get final state information
    if states:
        final_state = states[-1]

        # Controlled hosts
        for host in final_state.get('controlled_hosts', []):
            stats['controlled_hosts'].add(host.get('ip'))

        # Known hosts
        for host in final_state.get('known_hosts', []):
            stats['known_hosts'].add(host.get('ip'))

        # Known networks
        for net in final_state.get('known_networks', []):
            net_str = f"{net.get('ip')}/{net.get('mask')}"
            stats['known_networks'].add(net_str)

    return stats


def analyze_jsonl_files(filepaths):
    """Analyze multiple JSONL files and count episodes."""

    results = {
        'total_episodes': 0,
        'files': {},
        'by_agent': defaultdict(int),
        'by_role': defaultdict(int),
        'by_end_reason': defaultdict(int),
        'by_outcome': defaultdict(int),
        'by_final_action': defaultdict(int),
        'episode_details': []
    }

    for filepath in filepaths:
        filepath = Path(filepath)

        if not filepath.exists():
            print(f"Warning: File not found: {filepath}")
            continue

        file_stats = {
            'episodes': 0,
            'total_actions': 0,
            'total_states': 0,
            'total_reward': 0,
            'size_bytes': filepath.stat().st_size,
        }

        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    episode_data = json.loads(line)

                    # Count episode
                    file_stats['episodes'] += 1
                    results['total_episodes'] += 1

                    # Analyze episode
                    episode_stats = analyze_episode(episode_data)

                    # Update aggregates
                    file_stats['total_actions'] += episode_stats['num_actions']
                    file_stats['total_states'] += episode_stats['num_states']
                    file_stats['total_reward'] += episode_stats['total_reward']

                    # Count by agent and role
                    results['by_agent'][episode_stats['agent_name']] += 1
                    results['by_role'][episode_stats['agent_role']] += 1
                    results['by_end_reason'][str(episode_stats['end_reason'])] += 1
                    results['by_outcome'][episode_stats['outcome']] += 1
                    if episode_stats['final_action']:
                        results['by_final_action'][episode_stats['final_action']] += 1

                    # Store episode details
                    episode_stats['file'] = filepath.name
                    episode_stats['line_num'] = line_num
                    episode_stats['num_controlled_hosts'] = len(episode_stats['controlled_hosts'])
                    episode_stats['num_known_hosts'] = len(episode_stats['known_hosts'])
                    episode_stats['num_known_networks'] = len(episode_stats['known_networks'])
                    results['episode_details'].append(episode_stats)

                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num} in {filepath}: {e}")
                except Exception as e:
                    print(f"Error processing line {line_num} in {filepath}: {e}")

        results['files'][str(filepath)] = file_stats

    return results


def format_bytes(bytes_val):
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"


def print_results(results):
    """Print analysis results in a formatted way."""

    print("\n" + "="*80)
    print("EPISODE ANALYSIS SUMMARY")
    print("="*80 + "\n")

    print(f"Total Episodes: {results['total_episodes']}")
    print(f"Total Files: {len(results['files'])}\n")

    # File breakdown
    print("-" * 80)
    print("BY FILE:")
    print("-" * 80)
    for filepath, stats in results['files'].items():
        filename = Path(filepath).name
        print(f"\n{filename}")
        print(f"  Episodes: {stats['episodes']}")
        print(f"  Total Actions: {stats['total_actions']}")
        print(f"  Total States: {stats['total_states']}")
        print(f"  Total Reward: {stats['total_reward']:.2f}")
        print(f"  File Size: {format_bytes(stats['size_bytes'])}")
        if stats['episodes'] > 0:
            print(f"  Avg Actions/Episode: {stats['total_actions'] / stats['episodes']:.1f}")
            print(f"  Avg States/Episode: {stats['total_states'] / stats['episodes']:.1f}")
            print(f"  Avg Reward/Episode: {stats['total_reward'] / stats['episodes']:.2f}")

    # Agent breakdown
    if results['by_agent']:
        print("\n" + "-" * 80)
        print("BY AGENT:")
        print("-" * 80)
        for agent, count in sorted(results['by_agent'].items()):
            print(f"  {agent}: {count} episodes")

    # Role breakdown
    if results['by_role']:
        print("\n" + "-" * 80)
        print("BY ROLE:")
        print("-" * 80)
        for role, count in sorted(results['by_role'].items()):
            print(f"  {role}: {count} episodes")

    # End reason breakdown
    if results['by_end_reason']:
        print("\n" + "-" * 80)
        print("BY END REASON:")
        print("-" * 80)
        for reason, count in sorted(results['by_end_reason'].items()):
            print(f"  {reason}: {count} episodes")

    # Outcome breakdown
    if results['by_outcome']:
        print("\n" + "-" * 80)
        print("BY OUTCOME:")
        print("-" * 80)
        for outcome, count in sorted(results['by_outcome'].items()):
            print(f"  {outcome}: {count} episodes")

    # Final action breakdown
    if results['by_final_action']:
        print("\n" + "-" * 80)
        print("BY FINAL ACTION (for completed episodes):")
        print("-" * 80)
        for action, count in sorted(results['by_final_action'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {action}: {count} episodes")

    # Episode details
    if results['episode_details']:
        print("\n" + "="*80)
        print("EPISODE DETAILS")
        print("="*80 + "\n")

        for i, episode in enumerate(results['episode_details'], 1):
            outcome_symbol = "✓" if episode['outcome'] == 'win' else "✗" if episode['outcome'] == 'loss' else "○"
            print(f"Episode {i} [{outcome_symbol} {episode['outcome'].upper()}] ({episode['file']}:L{episode['line_num']})")
            print(f"  Agent: {episode['agent_name']} ({episode['agent_role']})")
            print(f"  States: {episode['num_states']}, Actions: {episode['num_actions']}, Rewards: {episode['num_rewards']}")
            print(f"  Total Reward: {episode['total_reward']:.2f}, Final Reward: {episode['final_reward']}")
            print(f"  Final Action: {episode['final_action']}")
            print(f"  Controlled Hosts: {episode['num_controlled_hosts']}, Known Hosts: {episode['num_known_hosts']}, Known Networks: {episode['num_known_networks']}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description='Count and analyze episodes in JSONL trajectory files'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='JSONL files to analyze'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    results = analyze_jsonl_files(args.files)

    if args.json:
        # Convert sets to lists for JSON serialization
        for episode in results['episode_details']:
            episode['controlled_hosts'] = list(episode['controlled_hosts'])
            episode['known_hosts'] = list(episode['known_hosts'])
            episode['known_networks'] = list(episode['known_networks'])

        print(json.dumps(results, indent=2))
    else:
        print_results(results)


if __name__ == '__main__':
    main()
