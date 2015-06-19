from yahoo_finance import Share
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint
import email, json

"""
Script to Process Financial API Data  
By Karl Brown ( thekarlbrown ) 18 Jun 2015

Combines a series of financial equations, both personally created and already derived,
with the Yahoo Finance API to convieniently obtain technical market analysis.
"""


"""
Core Method (JSON) for each instance of stock pricing analysis

stockAbbrev Stock Exchange abbreviation of company
historicalDate Target date (RFC822 date format)
timePeriod Number of days to we back at to grab historic data
"""
def historicalAnalysisJSON (stockAbbrev,historicalDate, timePeriod):
	
	# Import date, then convert to datetime format
	articleTime = datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(historicalDate)))

	# Use relativedelta to safely adjust dates
	historicStart= articleTime - relativedelta (days=+timePeriod)

	# Obtain the market data for that period of time
	yahooAPITarget = Share(stockAbbrev)
	JSONStockData = yahooAPITarget.get_historical(historicStart.strftime("%Y-%m-%d"), articleTime.strftime("%Y-%m-%d"))

	# Create the JSON array
	result = {}
	result['Stock'] = stockAbbrev
	result['StartDate'] = historicStart.strftime("%Y-%m-%d")
	result['EndDate'] = articleTime.strftime("%Y-%m-%d")
	result['psScore'] = psScore(JSONStockData,float(JSONStockData[0]['Close']))
	result['RSI'] = relativeStrengthIndex(JSONStockData,10)
	result['OBV'] = onBalanceVolume (JSONStockData)

	return json.dumps(result, indent=4)


"""
Placement Strength Score (ps-Score) derived by Karl Brown (thekarlbrown)

Over a historic prior period, you get the percentage the stock is above or below average
Result is returned on a scale of 1 to -1 (Highest Point vs Lowest Point)
So given 90 day high of $60, 90 day low of $50, and current value of $54 would be -20% below average

historicalJSONData Historical Data from the Yahoo API in JSON Format
currentValue Current value of stock
RETURN pecentage of ps-Score as float between  1.00 to -1.00
"""
def psScore (historicalJSONData, currentValue):
	historicHigh = 0.0
	historicLow = 2000000.0

	# Find the high and low over the period obtained
	for day in historicalJSONData:
		if historicLow > float(day['Low']):
			historicLow = float(day['Low'])
		if historicHigh < float(day['High']):
			historicHigh = float(day['High']) 
			
	return (2*currentValue - historicHigh - historicLow)/(historicHigh - historicLow)


"""
Relative Strength Index (RSI): Momentum indicator measuring speed and change of price
http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:relative_strength_index_rsi

historicalJSONData Historical Data from the Yahoo API in JSON Format
timePeriod Time period to average
RETURN RSI for historic period
"""
def relativeStrengthIndex (historicalJSONData,timePeriod):
	timePeriodDivisible=float(timePeriod)
	day=0
	averageGain=0.0
	averageLoss=0.0
	listOverTime=[]
	# Calculate for the first time period
	while(day<timePeriod):
		change = float(historicalJSONData[day]['Open'])-float(historicalJSONData[day]['Close'])
		if change<0:
			averageLoss-=change
		else:
			averageGain+=change
		day+=1	

	# Obtain First true average gain/loss
	averageGain = averageGain/timePeriodDivisible
	averageLoss = averageLoss/timePeriodDivisible
	historicalDataLength = len(historicalJSONData)

	# Obtain average gain/loss for remainder of time period
	timePeriodLess = timePeriodDivisible-1.0
	while(day<historicalDataLength):
		change = float(historicalJSONData[day]['Open'])-float(historicalJSONData[day]['Close'])
		if change<0:
			averageGain=(averageGain*timePeriodLess)/timePeriodDivisible
			averageLoss=((averageLoss*timePeriodLess)-change)/timePeriodDivisible
			listOverTime.append(averageGain/averageLoss)
		else:
			averageLoss=(averageLoss*timePeriodLess)/timePeriodDivisible
			averageGain=((averageGain*timePeriodLess)+change)/timePeriodDivisible
		day+=1

	# Return the RSI
	return (100.0 - (100.0/(1.0 + (averageGain/averageLoss))))


"""
On Balance Volume(OBV): Cumulative volume traded
http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:on_balance_volume_obv

historicalJSONData Historical Data from the Yahoo API in JSON Format
RETURN OBV for historic period
"""
def onBalanceVolume (historicalJSONData):

	#Set up initial conditions
	lastClosing = float(historicalJSONData[0]['Close'])
	day = 1
	OBV = 0
	historicalDataLength = len(historicalJSONData)

	#Loop through remaining days
	while (day<historicalDataLength):
		currentClose=float(historicalJSONData[day]['Close'])
		currentVolume=int(historicalJSONData[day]['Volume'])
		if (currentClose<lastClosing):
			OBV=-currentVolume 
		elif (currentClose>lastClosing):
			OBV=+currentVolume
		lastClosing=currentClose
		day+=1

	return OBV

"""
Exponential Moving averages: Smooth price data for period of historic time
http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_averages

historicalJSONData Historical Data from the Yahoo API in JSON Format
timePeriod Time period to average
RETURN (JSON) EMA's for historic period
"""
def exponentialMovingAverage (historicalJSONData, timePeriod):
	return -1

# Example markets and times
print ( historicalAnalysisJSON('IBM','Wed, 17 Jun 2015 09:41:15 -0700',90) )
print ( historicalAnalysisJSON('AAPL','Wed, 1 May 2015 07:41:15 -0500',120) ) 
print ( historicalAnalysisJSON('MSFT','Mon, 1 Feb 2013 10:41:15 -0500',100) )
print ( historicalAnalysisJSON('WMT','Wed, 1 May 2015 07:41:15 -0500',45) ) 

