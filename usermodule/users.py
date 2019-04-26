from pandas import read_csv, DataFrame


class Users(object):
    def __init__(self):
        self.csv_path='data/users.csv'

    def load(self):
        try:
            user_df = read_csv('users.csv', sep=';', index_col='ID', encoding='utf8')
        except:
            user_df = DataFrame(columns=['User', 'PayID', 'Patterns', 'Mail'])

        user_df.sort_values(by=['User'], inplace=True)
        user_df.fillna('', inplace=True)