import discord
from discord import app_commands
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

TOKEN = "MTQ2MTAxMTYyNjI5MDQ0NjQxOQ.G4_UJS.FctQ9OX1wxj-FtO2KyGOODx4yqTl7J4CrdkTL0"

DATA_FILE = "points.json"
SUBMISSIONS_FILE = "submissions.json"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

points = load_json(DATA_FILE)
submissions = load_json(SUBMISSIONS_FILE)

difficulty_points = {
    "easy": 1,
    "normal": 2,
    "hard": 3,
    "harder": 4,
    "insane": 5,
    "demon": 10
}

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

@tree.command(name="submit", description="Submit a level completion")
@app_commands.describe(difficulty="Difficulty", amount="How many levels", level_name="Optional level name")
async def submit(interaction: discord.Interaction, difficulty: str, amount: int, level_name: str = "Unknown"):

    difficulty = difficulty.lower()

    if difficulty not in difficulty_points:
        await interaction.response.send_message("Invalid difficulty.")
        return

    user = str(interaction.user.id)

    gained = difficulty_points[difficulty] * amount

    points[user] = points.get(user, 0) + gained

    today = datetime.now().strftime("%Y-%m-%d")

    if today not in submissions:
        submissions[today] = {}

    submissions[today][user] = points[user]

    save_json(DATA_FILE, points)
    save_json(SUBMISSIONS_FILE, submissions)

    await interaction.response.send_message(
        f"✅ {interaction.user.name} gained {gained} points for beating {amount} {difficulty} level(s)."
    )
@tree.command(name="leaderboard", description="Show leaderboard")
async def leaderboard(interaction: discord.Interaction):

    if not points:
        await interaction.response.send_message("Leaderboard empty.")
        return

    sorted_users = sorted(points.items(), key=lambda x: x[1], reverse=True)

    text = ""

    for i, (user_id, score) in enumerate(sorted_users[:10], start=1):
        user = await client.fetch_user(int(user_id))
        text += f"{i}. {user.name} — {score} points\n"

    await interaction.response.send_message(text)

@tree.command(name="graph", description="Show points graph")
async def graph(interaction: discord.Interaction):

    if not submissions:
        await interaction.response.send_message("Not enough data yet.")
        return

    dates = []
    totals = []

    for date, users in submissions.items():
        total = sum(users.values())
        dates.append(date)
        totals.append(total)

    plt.figure()
    plt.plot(dates, totals, marker="o")

    plt.title("Server Points Over Time")
    plt.xlabel("Date")
    plt.ylabel("Total Points")

    plt.xticks(rotation=45)

    plt.tight_layout()

    filename = "graph.png"
    plt.savefig(filename)
    plt.close()

    await interaction.response.send_message(file=discord.File(filename))

client.run(TOKEN)