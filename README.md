# valocity

A website using machine learning models and the Valorant API to provide analysis and unique insights into the Valorant meta and the theory behind it.

[\[Live Demo\]](https://valocity.app)

## Description

There are too many variables to rely on simple statistics like win rates if you want to figure out ideal economy round buys in Valorant. To address this problem, I trained a neural network on matches, accessed via the Valorant API, to predict the outcome of Valorant rounds based on all available parameters. This python tool was made public via a frontend programmed with React, Vite and Tailwind. With the frontend already in place and the backend having access to the Valorant API, I also created pages that allow users to filter all agents and weapons and gain unique insights into their usage that existing websites do not provide. For example, valocity allows you to filter weapon statistics by agent used and average rank in the game, and shows weapon statistics for different opponent loadouts.

## Note on Running Locally

This repository is provided for portfolio demonstration purposes. The backend requires a restricted Riot Games/Valorant API key which is not publicly available, so the application will not function locally without it. Please visit https://valocity.app to see the project in action.