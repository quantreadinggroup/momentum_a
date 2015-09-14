from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.broker import Broker

# a modified version of the moving average strategy found here: 
#http://gbeced.github.io/pyalgotrade/docs/v0.17/html/tutorial.html
#uses Ford stock price data from the yahoofeed. returns are about 12%. 


class ThisStrategy(strategy.BacktestingStrategy):

	def __init__(self, feed, instrument, smaPeriod):

		#the portfolio starts with 1000 dollars initially
		strategy.BacktestingStrategy.__init__(self, feed, 1000)
		self.__position = None
		self.__instrument = instrument 

		self.cash = 1000 # keeping track of amount of cash
		self.numbershares = 0 # keeping track of number of shares currently held. 

		# we use adjusted closing values
		self.setUseAdjustedValues(True)
		self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), smaPeriod)


	def onEnterOk(self, position):
		execInfo = position.getEntryOrder().getExecutionInfo()
		self.info("BUY at $%.2f" % (execInfo.getPrice()))


	def onEnterCanceled(self, position):
		self.__position = None


	def onExitOk(self, position):
		execInfo = position.getExitOrder().getExecutionInfo()
		self.info("Sell at $%.2f" % (execInfo.getPrice()))
		self.__position = None

		#if an exit is cancelled, try to exit again. 
	def onExitCanceled(self, position):
		self.__position.exitMarket()



	def onBars(self, bars):
		if self.__sma[-1] is None:
			return

		bar = bars[self.__instrument]

		# If we don't have a position, see if we should enter a long position.
		# we enter the position by buying as many shares as possible.
		if self.__position is None:
			if bar.getPrice() > self.__sma[-1]:
				currentcash = self.cash
				number = round(currentcash/bar.getPrice())
				self.cash = currentcash - number*bar.getPrice()
				self.numbershares = number 
				self.__position = self.enterLong(self.__instrument, number, True)

		# See if we need to liquidate our long position
		# We liquidate entirely. 
		elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():
			currentcash = self.cash
			self.cash = currentcash + self.numbershares * bar.getPrice()
			self.numbershares = 0
			self.__position.exitMarket()



def run_strategy(smaPeriod):
	# Load in Yahoo feed data from CSV
	feed = yahoofeed.Feed()
	feed.addBarsFromCSV("f", "f-2000.csv")

	#Evaluate strategy/execute strategy for ford in the year 2000. 
	myStrategy = ThisStrategy(feed, "f", smaPeriod)
	myStrategy.run()
	print "Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity()

# we use a 25 day moving average. 
run_strategy(25)







