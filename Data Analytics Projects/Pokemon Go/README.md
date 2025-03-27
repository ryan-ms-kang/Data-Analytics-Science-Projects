# Pokemon Go Analysis

In this fun project, I wanted to explore the dataset from one of my favroite mobile games, Pokemon Go, and identify which Pokemon types I should focus on catching in order to create the strongest team. One thing to note is that due to the limitations of the dataset, I have decided to make several assumptions based on domain knowledge. For example, Pokemon fans understand that there are type advantages, where Water beats Fire, Fire beats Grass, and so on. In addition, despite the primary and secondary (if any) types of certain Pokemons, they can learn movesets not restricted to their respective types. Hence, I shifted my main focus to be on the types only. 

## Project Objective

1. Determine the distrbutions of each primary type, later with more breakdowns (by Attack, Defense, etc.)
2. Incorporate descriptive statistics to better understand the stats of each type
3. Investigate the relationship between each stat point with each other
4. Examine the outperforming types based on the avergage stats of each group
5. Identify (if any) of how certain columns impact the staat columns (based on domain) knowledge)

### Workflow

I initially create a database in MySQL and implement various data constraints within a new table to ensure data reliability and accuracy. Once I finish inserting every row from a CSV file into the table, I employ SQL queries (CTE, window functions, aggregations, etc.) to extract the information that I deem relevant. 
