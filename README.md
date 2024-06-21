# MLBDiscrepancyBot
Discrepancy bot to find discrepancies between MLB lines on PrizePicks and DraftKings

Introduction
In the world of sports betting, many set out to create algorithms to predict player performance. However, I wanted to take a different approach. Instead of creating my own algorithm, I aimed to leverage the highly accurate models already developed by sportsbooks like DraftKings to find discrepancies.

How It Works
American odds are assigned to each over and under of a prop, and the more negative the odds, the more likely the event is to occur. Using this information, I developed a Discord bot that allows users to type the name of a player and instantly see their prop line on PrizePicks and DraftKings, along with the corresponding odds.

Key Features
Player Prop Lookup: Users can enter the name of a player to view their prop lines and the odds for these on both PrizePicks and DraftKings.
EV Plays: The EV plays command provides users with all the props that are -135 or less. Based on my research, lines at -135 or more are very profitable.
Discrepancy Detection: The bot identifies discrepancies between the two sites. This occurs when a player is either under-projected on PrizePicks but favored to go over on DraftKings, or over-projected on PrizePicks and favored to go under on DraftKings.
Expected Value (EV)
Expected Value (EV) is a critical concept in statistics and betting, representing the average outcome of a given bet if the same scenario were played out repeatedly. It helps bettors understand the potential profitability of their bets in the long run. In the context of my Discord bot, EV plays highlight prop bets that are likely to be profitable based on the provided odds. By focusing on bets where the odds are -135 or more, users can make more informed decisions and potentially increase their winnings.

How This Was Created
This bot was created using a trial key from OpticOdds, a service that provides access to real-time sports betting data and odds. OpticOdds allowed me to integrate accurate and up-to-date odds from DraftKings into my Discord bot, ensuring that users receive reliable and current information for their betting decisions. The trial key provided an excellent opportunity to explore and utilize OpticOdds' API for developing this project.

Why Use This Bot?
This Discord bot is designed to offer users an easy and comfortable way to research and find profitable betting opportunities. Instead of manually comparing prop lines and odds on different sites, users can simply interact with the bot to get all the necessary information in one place. This streamlined process not only saves time but also helps users make more informed bets based on reliable sportsbook models.
