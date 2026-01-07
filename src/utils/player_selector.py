import json
import random
from datetime import datetime


class PlayerSelector:
    def __init__(self):
        with open('src/data/players.json', 'r') as f:
            self.players_data = json.load(f)

        self.selected_history = []
        self.max_history = 50

    def select_player(self, gender):
        """Select random player based on gender"""
        if gender == 'male':
            pool = self.players_data['male_players']
        elif gender == 'female':
            pool = self.players_data['female_players']
        else:
            # If gender unknown, use both
            pool = self.players_data['male_players'] + self.players_data['female_players']

        # Remove recently selected players
        available = [p for p in pool if p['id'] not in self.selected_history]

        if not available:
            available = pool  # Reset if all have been selected
            self.selected_history = []

        selected = random.choice(available)

        # Update history
        self.selected_history.append(selected['id'])
        if len(self.selected_history) > self.max_history:
            self.selected_history.pop(0)

        return selected

    def generate_stats(self, base_stats):
        """Generate random stats based on base stats"""
        stats = {}
        for stat, value in base_stats.items():
            # Add random variation (-3 to +3)
            variation = random.randint(-3, 3)
            new_value = max(1, min(99, value + variation))
            stats[stat] = new_value

        # Calculate overall rating
        if 'DIV' in stats: # Goalkeeper stats
            weights = {'DIV': 0.2, 'HAN': 0.2, 'KIC': 0.15,
                       'REF': 0.2, 'SPD': 0.05, 'POS': 0.2}
        else: # Outfielder stats
            weights = {'PAC': 0.1, 'SHO': 0.2, 'PAS': 0.15,
                       'DRI': 0.2, 'DEF': 0.15, 'PHY': 0.2}

        overall = sum(stats.get(s, 0) * weights.get(s, 0) for s in weights)
        stats['OVR'] = int(round(overall))

        return stats
