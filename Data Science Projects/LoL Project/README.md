# Lol Rank Predictions (WORK IN PROGRESS)

While LoL may still be one of the greatest games to be ever made, it is also considered to one of the most 'toxic' games. A common theme that I have identified from personal experiences is that teammates 'flame' and blame everyone else but themselves. Hence, my goal here is to see if each player truly deserves to move up the ladder, or should be placed elsewhere lower. I will be employing methods such as Logistic Regression, Random Forest, XGBoosting, and possibly more to predict the ranks of each player. 

## Project Objective

1. Determine the distrbutions of each primary type, later with more breakdowns (by Attack, Defense, etc.)
2. Incorporate descriptive statistics to better understand the stats of each type
3. Investigate the relationship between each stat point with each other
4. Examine the outperforming types based on the avergage stats of each group
5. Identify (if any) of how certain columns impact the stat columns (based on domain) knowledge)

### Workflow

1. From Riot API, I call multiple requests to retrieve relevant data such as summonerId, puuid, x number most recent games, statistics of those games, etc.
2. I clean and aggregate all of these datasets pulled. For cleaning, I removed columns that does not contribute my goal for this project. For numerical columns spread out with individual stats, I group those together and create a ratio column, and for categorical, I either convert them into numerical via encoding methods, or concatenate similar colums together to reduce the dimensionality of the dataset.
3. I fit the cleaned data into each model and see identify which performed the best, and how I can improve the model. 
