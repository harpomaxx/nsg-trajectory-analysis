#!/usr/bin/env python3
"""
Investigate End Conditions in Episodes
Look for patterns that indicate win/loss conditions.
"""

import json
import argparse
from pathlib import Path


def investigate_episode(episode_data, episode_num):
    """Deep dive into an episode to find end condition indicators."""

    print(f"\n{'='*80}")
    print(f"EPISODE {episode_num}")
    print(f"{'='*80}\n")

    # Top level fields
    print("Top-level fields:")
    for key in sorted(episode_data.keys()):
        value = episode_data[key]
        if isinstance(value, (dict, list)):
            if isinstance(value, list):
                print(f"  {key}: [{len(value)} items]")
            else:
                print(f"  {key}: {{...}} with keys: {list(value.keys())}")
        else:
            print(f"  {key}: {value}")

    trajectory = episode_data.get('trajectory', {})

    # Check for any fields we might have missed
    print("\nTrajectory fields:")
    for key in sorted(trajectory.keys()):
        value = trajectory[key]
        if isinstance(value, list):
            print(f"  {key}: [{len(value)} items]")
        else:
            print(f"  {key}: {value}")

    states = trajectory.get('states', [])
    actions = trajectory.get('actions', [])
    rewards = trajectory.get('rewards', [])

    print(f"\nEpisode length: {len(states)} states, {len(actions)} actions")

    if len(rewards) > 0:
        print(f"Total reward: {sum(rewards)}")
        print(f"Reward distribution: min={min(rewards)}, max={max(rewards)}, avg={sum(rewards)/len(rewards):.2f}")

    # Check last state
    if states:
        print(f"\nFirst state:")
        first_state = states[0]
        print(f"  Known networks: {len(first_state.get('known_networks', []))}")
        print(f"  Known hosts: {len(first_state.get('known_hosts', []))}")
        print(f"  Controlled hosts: {len(first_state.get('controlled_hosts', []))}")
        print(f"  State keys: {list(first_state.keys())}")

        print(f"\nLast state:")
        last_state = states[-1]
        print(f"  Known networks: {len(last_state.get('known_networks', []))}")
        print(f"  Known hosts: {len(last_state.get('known_hosts', []))}")
        print(f"  Controlled hosts: {len(last_state.get('controlled_hosts', []))}")
        print(f"  State keys: {list(last_state.keys())}")

        # Check if there are any special fields
        for key in last_state.keys():
            if key not in ['known_networks', 'known_hosts', 'controlled_hosts', 'known_services', 'known_data', 'known_blocks']:
                print(f"  SPECIAL FIELD: {key} = {last_state[key]}")

    # Check last few actions
    if actions:
        print(f"\nLast 3 actions:")
        for i, action in enumerate(actions[-3:], len(actions)-2):
            print(f"  Action {i}: {action.get('action_type')}")
            if 'result' in action or 'success' in action or 'status' in action:
                print(f"    Special fields: {', '.join([k for k in action.keys() if k not in ['action_type', 'parameters']])}")

    # Check last few rewards
    if rewards:
        print(f"\nLast 5 rewards: {rewards[-5:]}")

    # Print full last state for inspection
    if states:
        print(f"\nFull last state:")
        print(json.dumps(last_state, indent=2))

    # Print full last action if exists
    if actions:
        print(f"\nFull last action:")
        print(json.dumps(actions[-1], indent=2))


def main():
    parser = argparse.ArgumentParser(
        description='Investigate end conditions in episode data'
    )
    parser.add_argument('file', help='JSONL file to investigate')
    parser.add_argument('--episodes', nargs='+', type=int,
                       help='Specific episode numbers to investigate (default: last 3)')
    parser.add_argument('--all', action='store_true',
                       help='Investigate all episodes')

    args = parser.parse_args()

    # Read all episodes
    episodes = []
    with open(args.file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                episodes.append(json.loads(line))

    print(f"Total episodes in file: {len(episodes)}")

    # Determine which episodes to investigate
    if args.all:
        episode_indices = range(len(episodes))
    elif args.episodes:
        episode_indices = [i-1 for i in args.episodes if 1 <= i <= len(episodes)]
    else:
        # Default: show episodes with positive rewards, negative rewards, and zero actions
        episode_indices = []

        # Find one with positive reward
        for i, ep in enumerate(episodes):
            rewards = ep.get('trajectory', {}).get('rewards', [])
            if rewards and sum(rewards) > 0:
                episode_indices.append(i)
                break

        # Find one with negative reward
        for i, ep in enumerate(episodes):
            rewards = ep.get('trajectory', {}).get('rewards', [])
            if rewards and sum(rewards) < 0:
                episode_indices.append(i)
                break

        # Find one with zero actions
        for i, ep in enumerate(episodes):
            actions = ep.get('trajectory', {}).get('actions', [])
            if len(actions) == 0:
                episode_indices.append(i)
                break

    for idx in episode_indices:
        investigate_episode(episodes[idx], idx + 1)


if __name__ == '__main__':
    main()
