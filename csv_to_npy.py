import datetime
import numpy as np

np.set_printoptions(suppress=True, formatter={ 'float_kind' : '{:0.2f}'.format })


ROUND         = 0
END_TIME      = 1
GAMEMODE      = 2
BEATMAPSET_ID = 3
TOPIC_ID      = 4
NUM_YES       = 5
NUM_NO        = 6


def datetime_to_int(txt):
    txt = txt.decode('utf-8')
    date_i = datetime.datetime(1970, 1, 1)
    date_f = datetime.datetime.strptime(txt.split('+')[0], '%Y-%m-%dT%H:%M:%S')
    return (date_f - date_i).total_seconds()


usecols = (ROUND, END_TIME, GAMEMODE, BEATMAPSET_ID, TOPIC_ID, NUM_YES, NUM_NO,)
converters = {
    END_TIME: datetime_to_int
}

data = np.genfromtxt('data/poll_history.csv', delimiter=',', skip_header=1, usecols=usecols, converters=converters)

## Save as npy
with open('data/player_skills.npy', 'wb') as f:
    np.save(f, data)

print(data)