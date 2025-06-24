# https://pypi.org/project/pwntools/
import pwn
import re

# https://github.com/sebastianotronto/nissy-classic
nissy = pwn.process("stdbuf -i0 -o0 -e0 /path/to/nissy", shell=True)

cache = {}
def find_optimal(scramble):
    if scramble in cache:
        return cache[scramble]
    nissy.sendlineafter(b"nissy-# ", f"solve optimal {scramble}".encode())
    result = nissy.recvline().decode()
    optimal = int(re.search(r"\((\d+)\)", result)[1])
    cache[scramble] = optimal
    return optimal

# https://www.worldcubeassociation.org/export/results
competitions = {}
for l in open("WCA_export_Competitions.tsv"):
    id, name, information, external_website, venue, latitude, longitude, cityName, countryId, venueAddress, venueDetails, cellName, cancelled, eventSpecs, wcaDelegate, organiser, year, month, day, endMonth, endDay = l.split("\t")
    if id=="id":
        continue
    competitions[id] = (name, f"{int(year):04d}/{int(month):02d}/{int(day):02d}")

roundTypes = {}
for l in open("WCA_export_RoundTypes.tsv"):
    id, final, name, rank, cellName = l.split("\t")
    if id=="id":
        continue
    roundTypes[id] = name

scrambles = {}
ambiguous = set()
for l in open("WCA_export_Scrambles.tsv"):
    scramble, competitionId, eventId, groupId, isExtra, roundTypeId, scrambleId, scrambleNum = l.split("\t")
    if scramble=="scramble":
        continue
    if eventId=="333fm":
        if groupId!="A" or isExtra!="0":
            ambiguous.add((competitionId, roundTypeId))
            continue
        scrambles[(competitionId, roundTypeId, int(scrambleNum)-1)] = scramble

for l in open("WCA_export_Results.tsv"):
    pos, best, average, value1, value2, value3, value4, value5, competitionId, eventId, roundTypeId, personName, personId, formatId, regionalSingleRecord, regionalAverageRecord, personCountryId = l.split("\t")
    if pos=="pos":
        continue
    if eventId=="333fm":
        values = [value1, value2, value3, value4, value5]
        values = list(map(int, values))
        for attempt in range(5):
            if 1<=values[attempt]<=20:
                compName, compDate = competitions[competitionId]
                roundType = roundTypes[roundTypeId]
                if (competitionId, roundTypeId, attempt) not in scrambles:
                    scramble = "No scramble"
                    optimal = "-"
                    diff = "-"
                elif (competitionId, roundTypeId) in ambiguous:
                    scramble = "Ambiguous scramble"
                    optimal = "-"
                    diff = "-"
                else:
                    scramble = scrambles[(competitionId, roundTypeId, attempt)]
                    optimal = find_optimal(scramble)
                    diff = values[attempt]-optimal
                print(f"|{compDate}|{compName}|{roundType}|{attempt+1}|{personName}|{personId}|{values[attempt]}|{optimal}|{diff}|{scramble}|")
