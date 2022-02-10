def set_data():
    with urlopen('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json') as response:
        counties = json.load(response)
    all_df = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
                         ,dtype={"iso_code": str})
    all_df.rename({'iso_code': 'id'}, axis=1, inplace=True)
    all_df['date'] = pd.to_datetime(all_df['date'])
    return all_df, counties