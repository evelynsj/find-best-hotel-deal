import sys
import csv
import datetime

NO_DEAL = 'No deal available.'
REBATE_3_PLUS = 'rebate_3plus'
REBATE = 'rebate'
PCT = 'pct'


class Deal:
    def __init__(self, promoTxt, value, type, start, end):
        self.text = promoTxt
        self.value = float(value)
        self.type = type
        self.start = start
        self.end = end


class Hotel:
    def __init__(self, args):
        self.name = args[0]
        self.rate = float(args[1])
        self.deals = set()
        self.startDates = set()
        self.endDates = set()
        self.dateMapping = set()
        self.addDeal(args[2:])

    def addDeal(self, args):
        start = args[3]
        end = args[4]
        self.deals.add(Deal(args[0], args[1], args[2], start, end))
        self.startDates.add(start)
        self.endDates.add(end)
        self.dateMapping.add((start, end))


class BestHotelDeal:
    def __init__(self, args, hotelList):  # assumes valid input
        hotelName = args[0]
        self.checkIn = args[1]
        self.duration = int(args[2])
        self.hotel = ''
        for h in hotelList:
            if h.name == hotelName:
                self.hotel = h
                break

    def getDeal(self):
        possibleStartDates = self.getPossibleStartDates()
        possibleEndDates = self.getPossibleEndDates()
        if possibleStartDates == None or possibleEndDates == None:
            return NO_DEAL
        possibleMappings = self.getPossibleMappings(
            possibleStartDates, possibleEndDates)
        if len(possibleMappings) == 0:
            return NO_DEAL

        currBest = 0
        currBestPromo = NO_DEAL
        for date in possibleMappings:
            for deal in self.hotel.deals:
                if date == (deal.start, deal.end):
                    calculatedDeal = self.calculateDeal(deal.type, deal.value)
                    if currBest <= calculatedDeal:
                        continue
                    else:
                        currBest = calculatedDeal
                        currBestPromo = deal.text
        return currBestPromo

    def calculateDeal(self, type, value):
        if type == REBATE_3_PLUS and self.duration >= 3 or type == REBATE:
            return float(value)
        elif type == PCT:
            return (self.hotel.rate * self.duration) * (value / 100)

        return 0

    def getPossibleMappings(self, possibleStartDates, possibleEndDates):
        possibleMappings = set()

        for start in possibleStartDates:
            for end in possibleEndDates:
                if (start, end) in self.hotel.dateMapping:
                    possibleMappings.add((start, end))

        return possibleMappings

    def formatDate(self, date):
        return datetime.datetime.strptime(date, "%Y-%m-%d")

    def getPossibleEndDates(self):
        sortedEnd = sorted(self.hotel.endDates, reverse=True)
        j = len(sortedEnd) - 1
        checkIn = self.formatDate(self.checkIn)
        firstDate = self.formatDate(sortedEnd[0])
        if firstDate < checkIn:
            return None
        else:
            while j >= 0 and self.formatDate(sortedEnd[j]) < checkIn:
                j -= 1

        possible = set(sortedEnd[:j+1])
        return possible

    def getPossibleStartDates(self):
        sortedStart = sorted(self.hotel.startDates)
        j = len(sortedStart) - 1
        checkIn = self.formatDate(self.checkIn)
        firstDate = self.formatDate(sortedStart[0])
        if firstDate > checkIn:
            return None
        else:
            while j >= 0 and self.formatDate(sortedStart[j]) > checkIn:
                j -= 1

        possible = set(sortedStart[:j+1])

        return possible


def createHotelList(path):
    filePath = path
    hotels = set()
    with open(filePath) as csvfile:
        CSV = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(CSV):
            if i == 0:
                continue
            hotelName = row[0]
            # https://stackoverflow.com/questions/9371114/check-if-list-of-objects-contain-an-object-with-a-certain-attribute-value
            if not (any(hotel.name == hotelName for hotel in hotels)):
                hotels.add(Hotel(row))
            else:
                for hotel in hotels:
                    if hotel.name == hotelName:
                        hotel.addDeal(row[2:])

    return hotels


hotelList = createHotelList(sys.argv[1])
deal = BestHotelDeal(sys.argv[2:], hotelList)
print(deal.getDeal())
