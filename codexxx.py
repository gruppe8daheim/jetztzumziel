# Grundlagen Informatik (HKA Verkehrssystemmanagement), WS 24/25
# Gruppe 8 (Nils und Janusz)
# Projekt: Bahnhofsanzeigetafel

from time import localtime, strftime
import datetime
import csv
import re

# MAIN
def main():
    collectAllStops()
    noResultsFoundForDepStation = True
    while noResultsFoundForDepStation == True:
        searchTermDep = getSearchTerm("dep")
        filterStops(searchTermDep)
        searchResultsDep = 0
        for stop in potentiallyWantedStops:
            # DEBUG: Liste die gefilterten Haltestellen mit ihrer Stop-ID auf
            # Später sollen die in einem Drop-Down-Menü in der GUI zur Auswahl stehen.
            # Generelles Problem: nur Direktverbindungen :/
            print(stop["stop_name"] + ", " + stop["stop_id"])
            searchResultsDep = searchResultsDep + 1
        if searchResultsDep == 0:
            print("Keine Ergebnisse gefunden.")
        else:
            noResultsFoundForDepStation = False
    departureStationMainID = input("Welche Stop-ID hat der Abfahrtsbahnhof? ")
    noResultsFoundForArrStation = True
    while noResultsFoundForArrStation == True:
        searchTermArr = getSearchTerm("arr")
        filterStops(searchTermArr)
        searchResultsArr = 0
        for stop in potentiallyWantedStops:
            # Liste die gefilterten Haltestellen mit ihrer Stop-ID auf
            print(stop["stop_name"] + ", " + stop["stop_id"])
            searchResultsArr = searchResultsArr + 1
        if searchResultsArr == 0:
            print("Keine Ergebnisse gefunden.")
        else:
            noResultsFoundForArrStation = False
    arrivalStationMainID = input("Welche Stop-ID hat der Ankunftsbahnhof? ")
    stopIDsOfDepartureStation = collectStopIDsOfStation(departureStationMainID)
 #   for a in stopIDsOfDepartureStation:    # debug
 #       print(a)
    stopIDsOfArrivalStation = collectStopIDsOfStation(arrivalStationMainID)
 #   for a in stopIDsOfArrivalStation:    # debug
 #       print(a)
    tripsAtDepStation = collectTripsAtDepartureStation(stopIDsOfDepartureStation)
 #   for trip in sorted(tripsAtDepStation, key=lambda trip: trip["departure_time"]):    # debug
 #       print(trip["departure_time"], trip["stop_id"], trip["trip_id"])
    # tripsAtDepStation is list of dictionaries
    # removing dictionaries (list items) is possible through tripsAtDepStation.pop(i)
    # i is index, will be identical to the ITERATOR of for loop for all trips in tripsAtDepStation
    # trips that don't go to ArrStation in stop_sequence > stop_sequence.here should be removed here or in separate function linked here
    tripsFromDepToArrStation = collectTripsFromDepToArrStation(tripsAtDepStation, stopIDsOfArrivalStation)
    time = getCurrentTime()
 #   time = "20:00:00"    # debug
    for trip in sorted(tripsFromDepToArrStation, key=lambda trip: trip["arrival_time"]):    # SCHNELLSTER ZUG zum Ziel (ab jetzt) wird zuerst angezeigt
        route = getTripName(trip["trip_id"])                                                # nicht der, der zuerst abfährt :)
        depTime, depPlatform = getDepInfos(trip["trip_id"], stopIDsOfDepartureStation)
        runningToday = checkIfRunsToday(trip["trip_id"])
        abfahrten = 0
        if abfahrten <= 10:    # "if if", da wenn if "and runningToday == yes" gelten würde, das Programm unnötigerweise weiterrechnen würde
            if runningToday == "yes":
                if time > depTime:
                    print("Zug übersprungen, da Abfahrt vor aktueller Uhrzeit")
                if time <= depTime:
                    print(route + ": Abfahrt um " + depTime + " von Gleis " + depPlatform + ", Ankunft um " + trip["arrival_time"])
                    abfahrten = abfahrten + 1
            if runningToday == "no":
                print("Zug übersprungen, da er heute nicht fährt")
    print("10 nächste Abfahrten angezeigt. Ende des Programms")

# Idee: automatisches Refresh-Feature ergänzen!
# Erstelle Variable mit Systemzeit
def getCurrentTime():
    currentTime = strftime("%H:%M:%S", localtime())
    return(currentTime)

# Generiere Menge aus Haltestellen (oben stehen Fernverkehrshaltestellen,
# diese werden ja auch häufiger gesucht)
stops = []
def collectAllStops():
    with open("./Fernverkehr/stops.txt", encoding="utf8") as stopsFernFile:
        reader = csv.DictReader(stopsFernFile)
        for entry in reader:
            if entry["parent_station"] == "":
                stops.append({"stop_name": entry["stop_name"], "stop_id": entry["stop_id"]})
    with open("./Regionalverkehr/stops.txt", encoding="utf8") as stopsRegionalFile:
        reader = csv.DictReader(stopsRegionalFile)
        for entry in reader:
            if entry["parent_station"] == "":
                stops.append({"stop_name": entry["stop_name"], "stop_id": entry["stop_id"]})

# Erfahre Suchbegriff (Haltestelle) mit Bedingung (3+ Zeichen)
def getSearchTerm(s):    # s: scenario (dep/arr)
    searchTries = 0
    term = "x"
    while len(term) < 3:
        if searchTries > 0:
            print("Bitte mindestens 3 Zeichen eingeben.")
        if s == "dep":
            term = input("Welcher Abfahrtsbahnhof wird gesucht? ").strip()
        if s == "arr":
            term = input("Welcher Ankunftsbahnhof wird gesucht? ").strip()
        searchTries = searchTries + 1
    return term

# Filtere Haltestellen nach Suchbegriff (darf egal wo stehen, da der Karlsruher Hauptbahnhof auch
# "Hauptbahnhof, Karlsruhe" heißen kann etc., was ebenfalls zur Auswahl stehen soll)
potentiallyWantedStops = []
def filterStops(t):    # t: term
    potentiallyWantedStops.clear()
    for stop in stops:
        if re.search(t + ".*", stop["stop_name"]):
            if stop not in potentiallyWantedStops:
                potentiallyWantedStops.append({"stop_name": stop["stop_name"], "stop_id": stop["stop_id"]})

# Sammle alle Stop-IDs der ausgewählten Haltestelle in einer Liste
 # stopIDsOfStation = []    # FALSCH, Variable darf nicht global sein, da sonst beim
                            # 2. Durchlauf der Funktion die Liste der stopIDsOfDepartureStation
                            # überschrieben wird
def collectStopIDsOfStation(mainID):
    stopIDsOfStation = []
    stopIDsOfStation.clear()
    stopIDsOfStation.append(mainID)
    with open("./Fernverkehr/stops.txt", encoding="utf8") as stopsFernFile:
        reader = csv.DictReader(stopsFernFile)
        for entry in reader:
            if entry["parent_station"] == mainID:
                if entry["stop_id"] not in stopIDsOfStation:
                    stopIDsOfStation.append(entry["stop_id"])
    with open("./Regionalverkehr/stops.txt", encoding="utf8") as stopsRegionalFile:
        reader = csv.DictReader(stopsRegionalFile)
        for entry in reader:
            if entry["parent_station"] == mainID:
                if entry["stop_id"] not in stopIDsOfStation:
                    stopIDsOfStation.append(entry["stop_id"])
    return stopIDsOfStation

# Sammle alle Reisen/Trips von der ausgewählten Abfahrtshaltestelle (mit allen ihren IDs)
# in einem Wörterbuch mit ihren Abfahrtszeiten
# Hinweis: Die gleiche Zugverbindung (Route) kann mehrmals am Tag bedient werden und hat
#          dadurch verschiedene Trip-IDs
tripsAtDepartureStation = []
def collectTripsAtDepartureStation(depStopIDs):
    with open("./Fernverkehr/stop_times.txt", encoding="utf8") as stopTimesFernFile:
        reader = csv.DictReader(stopTimesFernFile)
        for entry in reader:
            if entry["stop_id"] in depStopIDs:
                tripsAtDepartureStation.append({"trip_id": entry["trip_id"], "departure_time": entry["departure_time"], "stop_sequence": entry["stop_sequence"], "stop_id": entry["stop_id"]})
               # tripIDsAtDepartureStation.append(entry["trip_id"])    # ehemalige Idee, bis gesehen wurde, dass noch die stop_sequence (zum gleichen Trip zugeordnet) gebraucht wird
    with open("./Regionalverkehr/stop_times.txt", encoding="utf8") as stopTimesRegionalFile:
        reader = csv.DictReader(stopTimesRegionalFile)
        for entry in reader:
            if entry["stop_id"] in depStopIDs:
                tripsAtDepartureStation.append({"trip_id": entry["trip_id"], "departure_time": entry["departure_time"], "stop_sequence": entry["stop_sequence"], "stop_id": entry["stop_id"]})
               # tripIDsAtDepartureStation.append(entry["trip_id"])    # s.o.
    return tripsAtDepartureStation

# Sammle alle Reisen von vorher, allerdings NUR falls sie an der Zielhaltestelle halten,
# und das auch NUR, wenn die Zielhaltestelle bei der jeweiligen Reise NACH der
# Abfahrtshaltestelle kommt -- alles mit den Ankunftszeiten am Ankunftsbahnhof
tripsFromDepToArrStation = []
def collectTripsFromDepToArrStation(trips, arrStopIDs):
    with open("./Fernverkehr/stop_times.txt", encoding="utf8") as stopTimesFernFile:
        reader = csv.DictReader(stopTimesFernFile)
        for entry in reader:
            if entry["stop_id"] in arrStopIDs:
                for trip in trips:
                    if entry["trip_id"] == trip["trip_id"]:
                        if int(entry["stop_sequence"]) > int(trip["stop_sequence"]):
                            tripsFromDepToArrStation.append({"trip_id": entry["trip_id"], "arrival_time": entry["arrival_time"], "stop_sequence": entry["stop_sequence"], "stop_id": entry["stop_id"]})
    with open("./Regionalverkehr/stop_times.txt", encoding="utf8") as stopTimesRegionalFile:
        reader = csv.DictReader(stopTimesRegionalFile)
        for entry in reader:
            if entry["stop_id"] in arrStopIDs:
                for trip in trips:
                    if entry["trip_id"] == trip["trip_id"]:
                      #  print(type(entry["stop_sequence"]), entry["departure_time"], entry["stop_id"], entry["trip_id"], entry["stop_sequence"])    # debug
                      #  print(type(trip["stop_sequence"]), trip["departure_time"], trip["stop_id"], trip["trip_id"], trip["stop_sequence"])
                        if int(entry["stop_sequence"]) > int(trip["stop_sequence"]):
                            tripsFromDepToArrStation.append({"trip_id": entry["trip_id"], "arrival_time": entry["arrival_time"], "stop_sequence": entry["stop_sequence"], "stop_id": entry["stop_id"]})
    return tripsFromDepToArrStation

# Erhalte Zugname ("RE73" etc.)
def getTripName(tripID):
    tripName = "N/A"    # falls tripName nicht vorhanden, damit trotzdem eine Ausgabe erfolgt (Platzhalter)
    routeIDfern = 0
    routeIDregional = 0
    with open("./Fernverkehr/trips.txt", encoding="utf8") as tripsFernFile:
        reader = csv.DictReader(tripsFernFile)
        for entry in reader:
            if entry["trip_id"] == tripID:
                routeIDfern = entry["route_id"]
    with open("./Regionalverkehr/trips.txt", encoding="utf8") as tripsRegionalFile:
        reader = csv.DictReader(tripsRegionalFile)
        for entry in reader:
            if entry["trip_id"] == tripID:
                routeIDregional = entry["route_id"]
    if routeIDfern != 0:
        with open("./Fernverkehr/routes.txt", encoding="utf8") as routesFernFile:
            reader = csv.DictReader(routesFernFile)
            for entry in reader:
                if entry["route_id"] == routeIDfern:
                    tripName = entry["route_short_name"]
    if routeIDregional != 0:
        with open("./Regionalverkehr/routes.txt", encoding="utf8") as routesRegionalFile:
            reader = csv.DictReader(routesRegionalFile)
            for entry in reader:
                if entry["route_id"] == routeIDregional:
                    tripName = entry["route_short_name"]
    return tripName

# Erhalte Abfahrtszeit und Gleis (theoretisch) an Abfahrtshaltestelle
def getDepInfos(tripID, depStopIDs):
    with open("./Fernverkehr/stop_times.txt", encoding="utf8") as stopTimesFernFile:
        reader = csv.DictReader(stopTimesFernFile)
        for entry in reader:
            if entry["trip_id"] == tripID:
                if entry["stop_id"] in depStopIDs:
                    departureTime = entry["departure_time"]
                    departurePlatform = entry["stop_id"]
    with open("./Regionalverkehr/stop_times.txt", encoding="utf8") as stopTimesRegionalFile:
        reader = csv.DictReader(stopTimesRegionalFile)
        for entry in reader:
            if entry["trip_id"] == tripID:
                if entry["stop_id"] in depStopIDs:
                    departureTime = entry["departure_time"]
                    departurePlatform = entry["stop_id"]
    if departurePlatform == "178847":    # Karlsruhe-Durlach als Modell für Gleisausgabe nach Koordinaten aus GTFS
        departurePlatform = "5b"         # vermutet aus OpenStreetMap-Infos
    if departurePlatform == "268744":
        departurePlatform = "5a"
    if departurePlatform == "353094":
        departurePlatform = "2b"
    if departurePlatform == "358136":
        departurePlatform = "6a"
    if departurePlatform == "53533":
        departurePlatform = "2a"
    if departurePlatform == "654320":
        departurePlatform = "1a"
    if departurePlatform == "661862":
        departurePlatform = "6b"
    if departurePlatform == "41947":
        departurePlatform = "5a-b"
    if departurePlatform == "575876":
        departurePlatform = "6a-b"
    if departurePlatform == "606642":
        departurePlatform = "2a-b"
    return departureTime, departurePlatform

# Überprüfe, ob Zug heute überhaupt fährt
def checkIfRunsToday(tripID):
    date = strftime("%Y%m%d", localtime())
    today = datetime.datetime.today()
    weekday = today.weekday()
    runsToday = "no"
    serviceIDfern = 0
    serviceIDregional = 0
    with open("./Fernverkehr/trips.txt", encoding="utf8") as tripsFernFile:
        reader = csv.DictReader(tripsFernFile)
        for entry in reader:
            if entry["trip_id"] == tripID:
                serviceIDfern = entry["service_id"]
    with open("./Regionalverkehr/trips.txt", encoding="utf8") as tripsRegionalFile:
        reader = csv.DictReader(tripsRegionalFile)
        for entry in reader:
            if entry["trip_id"] == tripID:
                serviceIDregional = entry["service_id"]
 #  print(serviceIDfern, serviceIDregional, weekday, date)    # debug
    if serviceIDfern != 0:
        with open("./Fernverkehr/calendar.txt", encoding="utf8") as calendarFernFile:
            reader = csv.DictReader(calendarFernFile)
            for entry in reader:
                if entry["service_id"] == serviceIDfern:
                    if int(entry["start_date"]) <= int(date) and int(entry["end_date"]) >= int(date):
                        if weekday == 0:
                            if entry["monday"] == "1":
                                runsToday = "yes"
                        if weekday == 1:
                            if entry["tuesday"] == "1":
                                runsToday = "yes"
                        if weekday == 2:
                            if entry["wednesday"] == "1":
                                runsToday = "yes"
                        if weekday == 3:
                            if entry["thursday"] == "1":
                                runsToday = "yes"
                        if weekday == 4:
                            if entry["friday"] == "1":
                                runsToday = "yes"
                        if weekday == 5:
                            if entry["saturday"] == "1":
                                runsToday = "yes"
                        if weekday == 6:
                            if entry["sunday"] == "1":
                                runsToday = "yes"
        with open("./Fernverkehr/calendar_dates.txt", encoding="utf8") as calendarDatesFernFile:
            reader = csv.DictReader(calendarDatesFernFile)
            for entry in reader:
                if entry["service_id"] == serviceIDfern:
                    if int(entry["date"]) == int(date):
                        if entry["exception_type"] == "1":    # siehe GTFS-Dokumentation (fährt an diesem Tag ausnahmsweise)
                            runsToday = "yes"
                        if entry["exception_type"] == "2":    # (fährt an diesem Tag ausnahmsweise nicht)
                            runsToday = "no"
        return runsToday
    if serviceIDregional != 0:
        with open("./Regionalverkehr/calendar.txt", encoding="utf8") as calendarRegionalFile:
            reader = csv.DictReader(calendarRegionalFile)
            for entry in reader:
                if entry["service_id"] == serviceIDregional:
                    if int(entry["start_date"]) <= int(date) and int(entry["end_date"]) >= int(date):
                        if weekday == 0:
                            if entry["monday"] == "1":
                                runsToday = "yes"
                        if weekday == 1:
                            if entry["tuesday"] == "1":
                                runsToday = "yes"
                        if weekday == 2:
                            if entry["wednesday"] == "1":
                                runsToday = "yes"
                        if weekday == 3:
                            if entry["thursday"] == "1":
                                runsToday = "yes"
                        if weekday == 4:
                            if entry["friday"] == "1":
                                runsToday = "yes"
                        if weekday == 5:
                            if entry["saturday"] == "1":
                                runsToday = "yes"
                        if weekday == 6:
                            if entry["sunday"] == "1":
                                runsToday = "yes"
        with open("./Regionalverkehr/calendar_dates.txt", encoding="utf8") as calendarDatesRegionalFile:
            reader = csv.DictReader(calendarDatesRegionalFile)
            for entry in reader:
                if entry["service_id"] == serviceIDregional:
                    if int(entry["date"]) == int(date):
                        if entry["exception_type"] == "1":    # s.o.
                            runsToday = "yes"
                        if entry["exception_type"] == "2":    # ...
                            runsToday = "no"
        return runsToday

# Main ausführen!
if __name__ == "__main__":
    main()
