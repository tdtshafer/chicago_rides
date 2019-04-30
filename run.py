import requests
import csv
from pprint import pprint
from dateutil import parser

APP_TOKEN = 'SdJhpwypjkvrFvsyDdbubi6L4'
TOTAL_RESULTS_TO_FETCH = 2000
BATCH_LIMIT = 1000
INTIAL_OFFSET = 0

RIDES_URL = ('https://data.cityofchicago.org/resource/m6dm-c72p.json?'
		'$limit={}'
		'&$order=:id'
		'&$$app_token={}'
		'&$offset=').format(BATCH_LIMIT, APP_TOKEN)

def main():
    """
	{
		'additional_charges': '2.5',
		'fare': '15',
		'pickup_centroid_latitude': '41.8502663663',
		'pickup_centroid_location': {
			'coordinates': [-87.667569312, 41.8502663663],
		    'type': 'Point'
		},
		'pickup_centroid_longitude': '-87.667569312',
		'pickup_community_area': '31',
		'shared_trip_authorized': False,
		'tip': '0',
		'trip_end_timestamp': '2018-11-01T09:45:00.000',
		'trip_id': '8a5c8e6fa8d4a7fd5656eae6ad9f49ba25fd99e7',
		'trip_miles': '10.67366381696',
		'trip_seconds': '1024',
		'trip_start_timestamp': '2018-11-01T09:30:00.000',
	    'trip_total': '17.5',
		'trips_pooled': '1'
	},
    """
    
    all_rides = get_all_rides()

    # with open("Transportation_Network_Providers_-_Trips.csv", "rt") as file:
    # 	rows = csv.reader(file)
    # 	for row in rows:
    # 		try:
	   #  		trip_id, \
	   #  		trip_start_timestamp, \
	   #  		trip_end_timestamp, \
	   #  		trip_seconds, \
	   #  		trip_miles, \
	   #  		pickup_census_tract, \
	   #  		dropoff_census_tract, \
	   #  		pickup_community_area, \
	   #  		dropoff_community_area, \
	   #  		fare, \
	   #  		tip, \
	   #  		additional_charge, \
	   #  		trip_total, \
	   #  		shared_trip_authorized, \
	   #  		trips_pooled, \
	   #  		pickup_centroid_latitude, \
	   #  		pickup_centroid_longitude, \
	   #  		pickup_centroid_location, \
	   #  		dropoff_centroid_latitude, \
	   #  		dropoff_centroid_longitude, \
	   #  		dropoff_centroid_location = row
	   #  	except ValueError as e:
	   #  		print(e)
	   #  		print(row)
	   #  		continue
    # 		print(tip)
    print("Processing {} records...".format(TOTAL_RESULTS_TO_FETCH))

    tips = []
    tip_percent_of_ride_list = []
    trip_totals = []
    fares = []
    additional_charges = []
    distances = []
    durations = []
    speeds_in_mph = []
    pickup_times = []
    pickup_months = []
    pickup_hours = []
    pickup_weekdays = []
    trips_pooled_list = []

    for ride in all_rides:
    	
    	tip = float(ride.get('tip') or 0)
    	trip_total = float(ride.get('trip_total') or 1)
    	fare = float(ride.get('fare') or 0)
    	additional_charge = float(ride.get('additional_charges') or 0)
    	distance = float(ride.get('trip_miles') or 0)
    	duration = max(float(ride.get('trip_seconds') or 1), 1)
    	speed_in_mph = distance/(duration/3600) #duration comes in seconds
    	pickup_time = parser.parse(ride.get('trip_start_timestamp') or 0)
    	pickup_month = pickup_time.month
    	pickup_hour = pickup_time.hour
    	pickup_weekday =pickup_time.weekday()
    	is_pool = ride.get('shared_trip_authorized')
    	trips_pooled = float(ride.get('trips_pooled') or 1)


    	distances.append(distance)
    	durations.append(duration)
    	speeds_in_mph.append(speed_in_mph)
    	trip_totals.append(trip_total)
    	fares.append(fare)
    	pickup_times.append(pickup_time)
    	pickup_months.append(pickup_month)
    	pickup_hours.append(pickup_hour)
    	pickup_weekdays.append(pickup_weekday)

    	if tip>0:
    		tips.append(tip)
    		tip_percent_of_ride_list.append(tip/trip_total)

    	if additional_charge>0:
    		additional_charges.append(additional_charge)

    	if is_pool:
    		trips_pooled_list.append(trips_pooled)


    print(':::::::::::::::::::::::::::::::::::::::::::::::')

    #TIPPING
    percent_tipping = 100*len(tips)/float(len(all_rides))
    print("Percentage of people leaving a tip: {:.2f}%".format(percent_tipping))
    
    average_tip_percent_of_ride = 100*average(tip_percent_of_ride_list)
    average_tip_percent_of_ride_all_riders = 100*average(tip_percent_of_ride_list, all_rides)
    print("Average tip percentage left (only tippers): {:.2f}%".format(average_tip_percent_of_ride))
    print("Average tip percentage left (all riders): {:.2f}%".format(average_tip_percent_of_ride_all_riders))

    average_tip_value = average(tips)
    average_tip_value_all_riders = average(tips, all_rides)
    print("Average tip value (only tippers): ${:.2f}".format(average_tip_value))
    print("Average tip value (all riders): ${:.2f}".format(average_tip_value_all_riders))

    max_tip_value = max(tips)
    max_tip_percent = 100*max(tip_percent_of_ride_list)
    print("Maximum tip value: ${:.2f}".format(max_tip_value))
    print("Maximum tip percent: {:.2f}%".format(max_tip_percent))

    #FARES/ADDITIONAL CHARGES/TOTAL PRICE
    average_fare = average(fares)
    print("\nAverage fare value: ${:.2f}".format(average_fare))

    max_fare = max(fares)
    print("Maximum fare value: ${:.2f}".format(max_fare))

    min_fare = min(fares)
    print("Minimum fare value: ${:.2f}".format(min_fare))

    average_additional_charge = average(additional_charges)
    average_additional_charge_all_riders = average(additional_charges, all_rides)
    print("Average additional charge (only those receiving charges): ${:.2f}".format(average_additional_charge))
    print("Average additional charge (all riders): ${:.2f}".format(average_additional_charge_all_riders))

    max_additional_charge = max(additional_charges)
    print("Maximum additional charge: ${:.2f}".format(max_additional_charge))

    average_total_cost = average(trip_totals)
    print("Average total cost (fare + additional charges + tip): ${:.2f}".format(average_total_cost))

    max_total_cost = max(trip_totals)
    print("Maximum total cost (fare + additional charges + tip): ${:.2f}".format(max_fare))

    min_total_cost = min(trip_totals)
    print("Minimum total cost(fare + additional charges + tip): ${:.2f}".format(min_total_cost))

    #DISTANCE
    average_distance = average(distances)
    print("\nAverage trip distance: {:.2f} miles".format(average_distance))

    max_distance = max(distances)
    print("Maximum trip distance: {:.2f} miles".format(max_distance))

    min_distance = min(distances)
    print("Minimum trip distance: {:.2f} miles".format(min_distance))

    #DURATION
    average_duration = average(durations)
    print("\nAverage trip time: {:.2f} minutes".format(average_duration/60))

    max_duration = max(durations)
    print("Maximum trip time: {:.2f} minutes".format(max_duration/60))

    min_duration = min(durations)
    print("Minimum trip time: {:.2f} minutes".format(min_duration/60))

    #SPEED
    average_average_speed = average(speeds_in_mph)
    print("\nAverage average speed (questionable numbers): {:.2f} mph".format(average_average_speed))

    max_average_speed = max(speeds_in_mph)
    print("Maximum average speed (questionable numbers): {:.2f} mph".format(max_average_speed))

    min_average_speed = min(speeds_in_mph)
    print("Minimum average speed (questionable numbers): {:.2f} mph".format(min_average_speed))

    #TIME OF DAY
    quad1 = []
    quad2 = []
    quad3 = []
    quad4 = []

    for hour in pickup_hours:
    	if hour < 6:
    		quad1.append(hour)
    	elif hour < 12:
    		quad2.append(hour)
    	elif hour < 18:
    		quad3.append(hour)
    	else:
    		quad4.append(hour)

    print("\nTrip count by time of day (at pickup):")
    print("- Midnight to 6am: {} trips".format(len(quad1)))
    print("- 6am to Noon: {} trips".format(len(quad2)))
    print("- Noon to 6pm: {} trips".format(len(quad3)))
    print("- 6pm to Midngiht: {} trips".format(len(quad4)))

    #DAY OF WEEK

    print("\nTrip count by day of the week:")
    print("- Monday: {}".format(pickup_weekdays.count(0)))
    print("- Tuesday: {}".format(pickup_weekdays.count(1)))
    print("- Wednesday: {}".format(pickup_weekdays.count(2)))
    print("- Thursday: {}".format(pickup_weekdays.count(3)))
    print("- Friday: {}".format(pickup_weekdays.count(4)))
    print("- Saturday: {}".format(pickup_weekdays.count(5)))
    print("- Sunday: {}".format(pickup_weekdays.count(6)))

    #TIME OF YEAR
    q1 = []
    q2 = []
    q3 = []
    q4 = []

    for month in pickup_months:
    	if month <= 3:
    		q1.append(month)
    	elif month <= 6:
    		q2.append(month)
    	elif month <= 9:
    		q3.append(month)
    	else:
    		q4.append(month)

    print("\nTrip count by time of year:")
    print("- Q1 (Jan, Feb, March): {}".format(len(q1)))
    print("- Q2 (April, May, June): {}".format(len(q2)))
    print("- Q3 (July, August, Sept): {}".format(len(q3)))
    print("- Q4 (Oct, Nov, Dec): {}".format(len(q4)))

    #POOLING
    percentage_of_trips_pooled = 100*len(trips_pooled_list)/len(all_rides)
    print("\nPercentage of trips authorized as pool: {:.2f}%".format(percentage_of_trips_pooled))

    percentage_actually_pooled = 100*len([x for x in trips_pooled_list if x>1])/len(trips_pooled_list)
    print("Percentage of pool-authorized trips that were actually pooled%: {:.2f}".format(percentage_actually_pooled))


    print(':::::::::::::::::::::::::::::::::::::::::::::::')

def get_all_rides():
	print("Fetching ride data...")
	offset = INTIAL_OFFSET

	all_rides = requests.get(RIDES_URL+str(offset)).json()

	while len(all_rides) < TOTAL_RESULTS_TO_FETCH:
		print("{}/{}".format(len(all_rides), TOTAL_RESULTS_TO_FETCH))
		offset += BATCH_LIMIT
		more_all_rides = requests.get(RIDES_URL+str(offset)).json()
		all_rides += more_all_rides

	print("{}/{}".format(TOTAL_RESULTS_TO_FETCH, TOTAL_RESULTS_TO_FETCH))
	return all_rides

def average(l1, l2=None):
	denom = l2 or l1
	return sum(l1)/len(denom)

main()