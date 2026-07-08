from api.standings import get_standings

print()
print("PWHL NEXUS")
print("League Command Center")
print()

standings = get_standings()

for team in standings:
    print(f"{team['team']:15} {team['points']} pts")
