"""
PWHL NEXUS
League Command Center

Live Data Engine
"""

import requests


class PWHLClient:
    def __init__(self):
        self.leaguestat_base = "https://lscluster.hockeytech.com/feed/"
        self.firebase_base = "https://leaguestat-b9523.firebaseio.com/"

    def test_connection(self):
        print("Testing PWHL data sources...")
        print("LeagueStat Base:", self.leaguestat_base)
        print("Firebase Base:", self.firebase_base)
        print("Connection test ready.")


if __name__ == "__main__":
    client = PWHLClient()
    client.test_connection()