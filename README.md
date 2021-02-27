# Climate analysis and app API using SQLAlchemy!

### Background

This challenge is designed to make a climate analysis on Honolulu, Hawaii, to help people plan for their trip. It includes two main parts:

## Step 1. Climate Analysis and Exploration

This activity uses a Python and SQLAlchemy to make climate analysis and data exploration of the climate database. All of the following analysis completed by using SQLAlchemy ORM queries, Pandas, and Matplotlib.

* Used SQLAlchemy ‘create_engine’ created to connect to the sqlite database. 

```
hawaii_database_path = "./Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{hawaii_database_path}")
connector = engine.connect()
```

* Used SQLAlchemy ‘automap_base()’ to reflect the tables into classes, and saved a reference to those classes called `Station` and `Measurement`.

```
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
```

* Linked Python to the database by creating an SQLAlchemy session.

```
session = Session(engine)

```

### Precipitation Analysis

* After finding the most recent date in the data set, a query is designed to retrieve the last 12 months of precipitation data, and to select only the `date` and `prcp` values.
    * Load the query results into a Pandas DataFrame and set the index to the date column.
    * Sort the DataFrame values by date.
    * Plot the results using the DataFrame plot method

```
session.query(Measurement.date).order_by(Measurement.date.desc()).first()

date_last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

prec_data = session.query(Measurement.date, Measurement.prcp).\
                  filter(Measurement.date >= date_last_year).all()

prec_data_df = pd.DataFrame(prec_data, columns=["date", "precipitation"])

prec_data_df.set_index(prec_data_df["date"], inplace=True)

prec_data_df = prec_data_df.sort_index(ascending=False)

prec_data_df.plot(title="Precipitation Analysis", rot=45, figsize=(15,10))
plt.xlabel('Date', fontsize=14)
plt.ylabel("Inches",fontsize=14)
plt.savefig("Images/last_year_precipitation.png", bbox_inches = "tight")

prec_data_df.describe()
```
![](https://github.com/poonam-ux/SQLAlchemy-challenge_Climate-analysis_App/blob/main/Images/last_year_precipitation_small.png)

![](https://github.com/poonam-ux/SQLAlchemy-challenge_Climate-analysis_App/blob/main/Images/summary_stats_precipitation.png)

### Station Analysis

* Designed a query to calculate the total number of stations in the data set.
```
station_count = session.query(func.count(Station.station)).all()
```

* Designed a query to find the most active stations.

```
active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
```
![](https://github.com/poonam-ux/SQLAlchemy-challenge_Climate-analysis_App/blob/main/Images/station_obsv_descending_order.png)

The most active station is `USC00519281` (It has the highest number of observations.)

* Calculated the lowest, highest, and average temperature using func.min, func.max, func.avg, and func.count for the most active station id.

```
session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),\
              func.avg(Measurement.tobs).filter(Measurement.station =='USC00519281')).all()
```

* Designed a query to retrieve the last 12 months of temperature observation data (TOBS) and filter by the most active station (station with the highest number of observations).

```
temp_obsv = session.query(Measurement.tobs).filter(Measurement.station =='USC00519281').\
             filter(Measurement.date >= date_last_year).all()
```

* Plotted the results as a histogram with bins=12.
![](https://github.com/poonam-ux/SQLAlchemy-challenge_Climate-analysis_App/blob/main/Images/temp_most_active_station_small.png)

## Step 2 - Climate App

After completing the initial analysis, designed a Flask API based on the queries that were developed earlier.
Used Flask to create the routes.

A separate climate app API file is created with the following routes:

* `/`

  * Home page.

  * List all routes that are available.

* `/api/v1.0/precipitation`

  * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.

  * Return the JSON representation of your dictionary.

* `/api/v1.0/stations`

  * Return a JSON list of stations from the dataset.

* `/api/v1.0/tobs`
  * Query the dates and temperature observations of the most active station for the last year of data.
  
  * Return a JSON list of temperature observations (TOBS) for the previous year.

* `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

  * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

  * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

  * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

## Bonus: Recommended Analyses

### Temperature Analysis I

Hawaii is reputed to enjoy mild weather all year. Using pandas, the average temperatures for June and December were identified.

```
june_temp = session.query(Measurement).\
                filter(extract('month', Measurement.date) == 6).all()
june_temp_list = [temp.tobs for temp in june_temp]

june_avg = np.mean(june_temp_list)
print(f"Average temperature for June: {june_avg}")

december_temp = session.query(Measurement).\
                filter(extract('month', Measurement.date) == 12).all()
december_temp_list = [temp.tobs for temp in december_temp]

december_avg = np.mean(december_temp_list)
print(f"Average temperature for December: {december_avg}")
```
* Average temperature for June: 74.94411764705882
* Average temperature for December: 71.04152933421226

### Analysis
* Using an unpaired t-test makes sense for this part of the analysis. Here, the means of June and December temperatures in Hawaii are compared (two different populations). The unpaired t-test is used to compare the means of two independent populations. The paired t-test (one sample t-test) is used to compare the sample to the population, which is not useful here.

### Temperature Analysis II

* Used the calc_temps function, to calculate the min, avg, and max temperatures for the trip using the matching dates from a previous year (i.e., from  “2017-08-01” to “2017-08-08”).

```
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

prev_year_start = dt.date(2018, 8, 1) - dt.timedelta(days=365)
prev_year_end = dt.date(2018, 8, 7) - dt.timedelta(days=365)

tmin, tavg, tmax = calc_temps(prev_year_start.strftime("%Y-%m-%d"), prev_year_end.strftime("%Y-%m-%d"))[0]
print(f"Previous year's min, avg, and max temperatures are : {tmin}, {tavg}, {tmax} respectively.")
```

* Ploted the min, avg, and max temperature from your previous query as a bar chart.

```
# Use the average temperature for bar height (y value)
# Use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)
fig, ax = plt.subplots(figsize=plt.figaspect(2.))
xpos = 1
yerr = tmax - tmin

bar = ax.bar(xpos, tmax, yerr=yerr, alpha=0.5, color='coral', align='center')
ax.set(xticks=range(xpos), xticklabels="a", title="Trip Avg Temp", ylabel="Temp (F)")
ax.margins(.2,.2)
plt.savefig("Images/Trip_Avg_Temp.png", bbox_inches = 'tight')
fig.tight_layout()
fig.show()
```
![](https://github.com/poonam-ux/SQLAlchemy-challenge_Climate-analysis_App/blob/main/Images/Trip_Avg_Temp.png)

### Daily Rainfall Average

* Calculated the rainfall per weather station, and sorted them in descending order of precipitation. Also calculated the daily normals using a function ‘daily_normals’ that calculates daily temperatures for a specific date range.

```
start_date = '2017-08-01'
end_date = '2017-08-07'

sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation, func.sum(Measurement.prcp)]

results = session.query(*sel).\
            filter(Measurement.station == Station.station).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).\
            group_by(Station.name).order_by(func.sum(Measurement.prcp).desc()).all()
print(results)
```
![](https://github.com/poonam-ux/SQLAlchemy-challenge_Climate-analysis_App/blob/main/Images/daily_rainfall_station_avg.png)

* Calculated daily normal for the desired trip dates(2018-08-01 to 2018-08-08)

```
# Set the start and end date of the trip
trip_start = '2018-08-01'
trip_end = '2018-08-08'

# Use the start and end date to create a range of dates
trip_dates = pd.date_range(trip_start, trip_end, freq='D')

# Strip off the year and save a list of strings in the format %m-%d
trip_month_day= trip_dates.strftime('%m-%d')

# Use the `daily_normals` function to calculate the normals for each date string 
# and append the results to a list called `normals`.
normals = []
for date in trip_month_day:
    normals.append(*daily_normals(date))
normals 
```
![](https://github.com/poonam-ux/SQLAlchemy-challenge_Climate-analysis_App/blob/main/Images/daily_normals_desired_trip_dates.png)

* Used Pandas to plot an area plot (stacked=False) for the daily normal.

```
fig, ax = plt.subplots(figsize=(12,8))
df.plot(kind="area",stacked=False, x_compat=True, alpha=0.2, ax=ax)
plt.title("Daily Normals",fontsize=15)
plt.ylabel("Temperature",fontsize=15)
plt.xlabel("Date",fontsize=15)
plt.savefig("./Images/daily_rainfall_avg.png", bbox_inches = "tight")
plt.tight_layout()
```
![](https://github.com/poonam-ux/SQLAlchemy-challenge_Climate-analysis_App/blob/main/Images/daily_rainfall_avg%20copy.png)
