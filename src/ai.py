import pandas as pd
from sklearn import linear_model

df = pd.read_csv('ai_bum_list.csv')

model = linear_model.LinearRegression()
# model.fit(df[['ppPoints', 'gamesPlayed', 'ppUnit', 'avgPowerplayToi']], df.merit_rating)
model.fit(df[['ppPoints', 'gamesPlayed']], df.rating)

# Prediction
player = {
    'ppPoints': 0,
    'gamesPlayed': 20,
}

prediction = model.predict([[player['ppPoints'], player['gamesPlayed']]])

print('Player: ' + str(player))
print('Prediction: ' + str(round(prediction[0], 2)))