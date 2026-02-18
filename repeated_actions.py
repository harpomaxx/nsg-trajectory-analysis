#!/usr/bin/env python3
"""
Analyze repeated actions in episodes.
A repeated action is when the exact same action (including parameters) is executed more than once.
"""

import csv
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

# Optional matplotlib import for plotting
try:
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def make_hashable(obj):
    """Recursively convert a JSON-like object to a hashable representation.

    Args:
        obj: Object to convert (dict, list, or primitive)

    Returns:
        Hashable representation (tuple for dicts/lists, primitive otherwise)
    """
    if isinstance(obj, dict):
        # Convert dict to sorted tuple of (key, hashable_value) pairs
        return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
    elif isinstance(obj, list):
        # Convert list to tuple of hashable elements
        return tuple(make_hashable(item) for item in obj)
    elif isinstance(obj, (str, int, float, bool, type(None))):
        # Primitives are already hashable
        return obj
    else:
        # Fallback: convert to string
        return str(obj)


def action_to_hashable(action):
    """Convert action dict to a hashable representation.

    Args:
        action: Action dictionary

    Returns:
        Tuple representation of the action that can be used as a dict key
    """
    return make_hashable(action)


def analyze_repeated_actions(filepaths):
    """Analyze repeated actions in episodes.

    Args:
        filepaths: List of JSONL files to analyze

    Returns:
        Dictionary with analysis results
    """

    all_episodes_repeats = []
    win_episodes_repeats = []
    loss_episodes_repeats = []

    all_episodes_total_reps = []
    win_episodes_total_reps = []
    loss_episodes_total_reps = []

    all_episodes_rep_rates = []
    win_episodes_rep_rates = []
    loss_episodes_rep_rates = []

    episode_details = []

    # Read all episodes from all files
    for filepath in filepaths:
        filepath = Path(filepath)

        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    episode = json.loads(line)
                    trajectory = episode.get('trajectory', {})
                    actions = trajectory.get('actions', [])
                    rewards = trajectory.get('rewards', [])

                    # Skip episodes with no actions
                    if len(actions) == 0:
                        continue

                    # Count action occurrences
                    action_counter = Counter()
                    for action in actions:
                        action_hash = action_to_hashable(action)
                        action_counter[action_hash] += 1

                    # Count how many actions were repeated (appeared more than once)
                    num_repeated_actions = sum(1 for count in action_counter.values() if count > 1)

                    # Count total repetitions (sum of extra occurrences)
                    total_repetitions = sum(count - 1 for count in action_counter.values() if count > 1)

                    # Calculate percentage
                    total_actions = len(actions)
                    repeat_percentage = (total_repetitions / total_actions * 100) if total_actions > 0 else 0

                    # Determine outcome
                    is_win = rewards and rewards[-1] >= 50

                    episode_info = {
                        'file': str(filepath),
                        'line': line_num,
                        'total_actions': total_actions,
                        'unique_actions': len(action_counter),
                        'num_repeated_actions': num_repeated_actions,
                        'total_repetitions': total_repetitions,
                        'repeat_percentage': repeat_percentage,
                        'is_win': is_win
                    }

                    episode_details.append(episode_info)
                    all_episodes_repeats.append(num_repeated_actions)
                    all_episodes_total_reps.append(total_repetitions)
                    all_episodes_rep_rates.append(repeat_percentage)

                    if is_win:
                        win_episodes_repeats.append(num_repeated_actions)
                        win_episodes_total_reps.append(total_repetitions)
                        win_episodes_rep_rates.append(repeat_percentage)
                    else:
                        loss_episodes_repeats.append(num_repeated_actions)
                        loss_episodes_total_reps.append(total_repetitions)
                        loss_episodes_rep_rates.append(repeat_percentage)

                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num} in {filepath}: {e}")
                except Exception as e:
                    print(f"Error processing line {line_num} in {filepath}: {e}")

    return {
        'all_episodes': all_episodes_repeats,
        'win_episodes': win_episodes_repeats,
        'loss_episodes': loss_episodes_repeats,
        'all_episodes_total_reps': all_episodes_total_reps,
        'win_episodes_total_reps': win_episodes_total_reps,
        'loss_episodes_total_reps': loss_episodes_total_reps,
        'all_episodes_rep_rates': all_episodes_rep_rates,
        'win_episodes_rep_rates': win_episodes_rep_rates,
        'loss_episodes_rep_rates': loss_episodes_rep_rates,
        'episode_details': episode_details
    }


def print_summary(results):
    """Print summary statistics about repeated actions."""

    all_repeats = results['all_episodes']
    win_repeats = results['win_episodes']
    loss_repeats = results['loss_episodes']

    all_total_reps = results['all_episodes_total_reps']
    win_total_reps = results['win_episodes_total_reps']
    loss_total_reps = results['loss_episodes_total_reps']

    all_rep_rates = results['all_episodes_rep_rates']
    win_rep_rates = results['win_episodes_rep_rates']
    loss_rep_rates = results['loss_episodes_rep_rates']

    details = results['episode_details']

    print("\n" + "="*80)
    print("REPEATED ACTIONS ANALYSIS")
    print("="*80 + "\n")

    print(f"Total Episodes Analyzed: {len(all_repeats)}")
    print(f"  Wins: {len(win_repeats)}")
    print(f"  Losses: {len(loss_repeats)}")

    print("\n" + "-"*80)
    print("OVERALL STATISTICS")
    print("-"*80 + "\n")

    if all_repeats:
        avg_repeats = sum(all_repeats) / len(all_repeats)
        min_repeats = min(all_repeats)
        max_repeats = max(all_repeats)
        avg_total_reps = sum(all_total_reps) / len(all_total_reps)
        min_total_reps = min(all_total_reps)
        max_total_reps = max(all_total_reps)
        avg_rep_rate = sum(all_rep_rates) / len(all_rep_rates)
        min_rep_rate = min(all_rep_rates)
        max_rep_rate = max(all_rep_rates)

        # Episodes with no repeats
        no_repeats = sum(1 for x in all_repeats if x == 0)

        print(f"Avg Distinct Repeated Actions per Episode: {avg_repeats:.2f}")
        print(f"Avg Total Repetitions per Episode: {avg_total_reps:.2f}")
        print(f"Avg Repetition Rate: {avg_rep_rate:.1f}%")
        print(f"Min Distinct Repeated Actions: {min_repeats}")
        print(f"Max Distinct Repeated Actions: {max_repeats}")
        print(f"Min Total Repetitions: {min_total_reps}")
        print(f"Max Total Repetitions: {max_total_reps}")
        print(f"Min Repetition Rate: {min_rep_rate:.1f}%")
        print(f"Max Repetition Rate: {max_rep_rate:.1f}%")
        print(f"Episodes with No Repeated Actions: {no_repeats} ({no_repeats/len(all_repeats)*100:.1f}%)")

    print("\n" + "-"*80)
    print("WINNING EPISODES")
    print("-"*80 + "\n")

    if win_repeats:
        avg_repeats = sum(win_repeats) / len(win_repeats)
        min_repeats = min(win_repeats)
        max_repeats = max(win_repeats)
        avg_total_reps = sum(win_total_reps) / len(win_total_reps)
        min_total_reps = min(win_total_reps)
        max_total_reps = max(win_total_reps)
        avg_rep_rate = sum(win_rep_rates) / len(win_rep_rates)
        min_rep_rate = min(win_rep_rates)
        max_rep_rate = max(win_rep_rates)
        no_repeats = sum(1 for x in win_repeats if x == 0)

        print(f"Avg Distinct Repeated Actions per Episode: {avg_repeats:.2f}")
        print(f"Avg Total Repetitions per Episode: {avg_total_reps:.2f}")
        print(f"Avg Repetition Rate: {avg_rep_rate:.1f}%")
        print(f"Min Distinct Repeated Actions: {min_repeats}")
        print(f"Max Distinct Repeated Actions: {max_repeats}")
        print(f"Min Total Repetitions: {min_total_reps}")
        print(f"Max Total Repetitions: {max_total_reps}")
        print(f"Min Repetition Rate: {min_rep_rate:.1f}%")
        print(f"Max Repetition Rate: {max_rep_rate:.1f}%")
        print(f"Episodes with No Repeated Actions: {no_repeats} ({no_repeats/len(win_repeats)*100:.1f}%)")

    print("\n" + "-"*80)
    print("LOSING EPISODES")
    print("-"*80 + "\n")

    if loss_repeats:
        avg_repeats = sum(loss_repeats) / len(loss_repeats)
        min_repeats = min(loss_repeats)
        max_repeats = max(loss_repeats)
        avg_total_reps = sum(loss_total_reps) / len(loss_total_reps)
        min_total_reps = min(loss_total_reps)
        max_total_reps = max(loss_total_reps)
        avg_rep_rate = sum(loss_rep_rates) / len(loss_rep_rates)
        min_rep_rate = min(loss_rep_rates)
        max_rep_rate = max(loss_rep_rates)
        no_repeats = sum(1 for x in loss_repeats if x == 0)

        print(f"Avg Distinct Repeated Actions per Episode: {avg_repeats:.2f}")
        print(f"Avg Total Repetitions per Episode: {avg_total_reps:.2f}")
        print(f"Avg Repetition Rate: {avg_rep_rate:.1f}%")
        print(f"Min Distinct Repeated Actions: {min_repeats}")
        print(f"Max Distinct Repeated Actions: {max_repeats}")
        print(f"Min Total Repetitions: {min_total_reps}")
        print(f"Max Total Repetitions: {max_total_reps}")
        print(f"Min Repetition Rate: {min_rep_rate:.1f}%")
        print(f"Max Repetition Rate: {max_rep_rate:.1f}%")
        print(f"Episodes with No Repeated Actions: {no_repeats} ({no_repeats/len(loss_repeats)*100:.1f}%)")

    print("\n" + "="*80 + "\n")


def create_histogram(results, output_file=None, title=None, bins=20):
    """Create histogram of repeated actions distribution.

    Args:
        results: Results dictionary from analyze_repeated_actions
        output_file: Output file path (if None, display interactively)
        title: Plot title
        bins: Number of bins for histogram
    """

    if not HAS_MATPLOTLIB:
        print("Error: matplotlib is required for plotting. Install with: pip install matplotlib")
        return

    all_repeats = results['all_episodes']
    win_repeats = results['win_episodes']
    loss_repeats = results['loss_episodes']

    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    mpl.rcParams['font.size'] = 12

    # Create figure with subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Define colors
    colors = ['#3498db', '#2ecc71', '#e74c3c']  # Blue, Green, Red
    datasets = [
        (all_repeats, 'All Episodes', colors[0]),
        (win_repeats, 'Wins', colors[1]),
        (loss_repeats, 'Losses', colors[2])
    ]

    for ax, (data, label, color) in zip(axes, datasets):
        if data:
            ax.hist(data, bins=bins, alpha=0.7, color=color, edgecolor='black')
            ax.set_xlabel('Number of Repeated Actions')
            ax.set_ylabel('Number of Episodes')
            ax.set_title(f'{label} (n={len(data)})')
            ax.grid(True, alpha=0.3)

            # Add mean line
            mean_val = sum(data) / len(data)
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
            ax.legend()

    if title:
        fig.suptitle(title, fontsize=16, y=1.02)
    else:
        fig.suptitle('Distribution of Repeated Actions per Episode', fontsize=16, y=1.02)

    plt.tight_layout()

    # Save or show
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Histogram saved to {output_file}")
    else:
        plt.show()

    plt.close()


def create_boxplot(results, output_file=None, title=None):
    """Create boxplot of repeated actions distribution.

    Args:
        results: Results dictionary from analyze_repeated_actions
        output_file: Output file path (if None, display interactively)
        title: Plot title
    """

    if not HAS_MATPLOTLIB:
        print("Error: matplotlib is required for plotting. Install with: pip install matplotlib")
        return

    all_repeats = results['all_episodes']
    win_repeats = results['win_episodes']
    loss_repeats = results['loss_episodes']

    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    mpl.rcParams['font.size'] = 12

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Prepare data
    data = [all_repeats, win_repeats, loss_repeats]
    labels = ['All Episodes', 'Wins', 'Losses']

    # Create boxplot
    bp = ax.boxplot(data, labels=labels, patch_artist=True, showmeans=True,
                     meanprops=dict(marker='D', markerfacecolor='red', markeredgecolor='red', markersize=8))

    # Customize colors
    colors = ['#3498db', '#2ecc71', '#e74c3c']  # Blue, Green, Red
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    # Labels and title
    ax.set_ylabel('Number of Repeated Actions')
    ax.set_xlabel('Episode Category')
    if title:
        ax.set_title(title)
    else:
        ax.set_title('Distribution of Repeated Actions by Episode Outcome')

    # Grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Add count annotations
    for i, (data_points, label) in enumerate(zip(data, labels), 1):
        count = len(data_points)
        ax.text(i, ax.get_ylim()[1] * 0.95, f'n={count}',
                ha='center', va='top', fontsize=10, fontweight='bold')

    plt.tight_layout()

    # Save or show
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Boxplot saved to {output_file}")
    else:
        plt.show()

    plt.close()


def export_csv(results, output_file):
    """Export episode details to a flat CSV file.

    Args:
        results: Results dictionary from analyze_repeated_actions
        output_file: Output CSV file path
    """
    fieldnames = [
        'episode', 'outcome', 'total_actions', 'unique_actions',
        'num_repeated_actions', 'total_repetitions', 'repeat_percentage'
    ]
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, ep in enumerate(results['episode_details'], 1):
            writer.writerow({
                'episode': i,
                'outcome': 'win' if ep['is_win'] else 'loss',
                'total_actions': ep['total_actions'],
                'unique_actions': ep['unique_actions'],
                'num_repeated_actions': ep['num_repeated_actions'],
                'total_repetitions': ep['total_repetitions'],
                'repeat_percentage': round(ep['repeat_percentage'], 4),
            })
    print(f"CSV exported to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze repeated actions in episodes'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='JSONL files to analyze'
    )
    parser.add_argument(
        '--histogram',
        type=str,
        help='Generate histogram and save to file (e.g., histogram.png)'
    )
    parser.add_argument(
        '--boxplot',
        type=str,
        help='Generate boxplot and save to file (e.g., boxplot.png)'
    )
    parser.add_argument(
        '--title',
        type=str,
        help='Plot title'
    )
    parser.add_argument(
        '--bins',
        type=int,
        default=20,
        help='Number of bins for histogram (default: 20)'
    )
    parser.add_argument(
        '--csv',
        type=str,
        metavar='OUTPUT_CSV',
        help='Export per-episode data to a CSV file'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output detailed results as JSON'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Print detailed per-episode information'
    )

    args = parser.parse_args()

    # Analyze episodes
    results = analyze_repeated_actions(args.files)

    if not results['all_episodes']:
        print("No episodes found in the provided files.")
        return

    if args.json:
        import json as json_module
        def _avg(lst): return sum(lst) / len(lst) if lst else 0
        output = {
            'summary': {
                'total_episodes': len(results['all_episodes']),
                'wins': len(results['win_episodes']),
                'losses': len(results['loss_episodes']),
                'all_avg_distinct_repeated': _avg(results['all_episodes']),
                'all_avg_total_reps': _avg(results['all_episodes_total_reps']),
                'all_avg_repetition_rate_pct': _avg(results['all_episodes_rep_rates']),
                'win_avg_distinct_repeated': _avg(results['win_episodes']),
                'win_avg_total_reps': _avg(results['win_episodes_total_reps']),
                'win_avg_repetition_rate_pct': _avg(results['win_episodes_rep_rates']),
                'loss_avg_distinct_repeated': _avg(results['loss_episodes']),
                'loss_avg_total_reps': _avg(results['loss_episodes_total_reps']),
                'loss_avg_repetition_rate_pct': _avg(results['loss_episodes_rep_rates']),
            },
            'episode_details': results['episode_details']
        }
        print(json_module.dumps(output, indent=2))
    else:
        print_summary(results)

        if args.detailed:
            print("\n" + "="*80)
            print("DETAILED EPISODE INFORMATION")
            print("="*80 + "\n")

            for i, ep in enumerate(results['episode_details'], 1):
                outcome = "WIN" if ep['is_win'] else "LOSS"
                print(f"Episode {i} [{outcome}]:")
                print(f"  File: {ep['file']}:{ep['line']}")
                print(f"  Total Actions: {ep['total_actions']}")
                print(f"  Unique Actions: {ep['unique_actions']}")
                print(f"  Repeated Actions: {ep['num_repeated_actions']}")
                print(f"  Total Repetitions: {ep['total_repetitions']}")
                print(f"  Repeat Percentage: {ep['repeat_percentage']:.1f}%")
                print()

    # Export CSV if requested
    if args.csv:
        export_csv(results, args.csv)

    # Generate plots if requested
    if args.histogram:
        create_histogram(results, output_file=args.histogram, title=args.title, bins=args.bins)

    if args.boxplot:
        create_boxplot(results, output_file=args.boxplot, title=args.title)


if __name__ == '__main__':
    main()
