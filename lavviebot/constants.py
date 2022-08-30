BASE_URL = 'https://api.purrsong.co/purrsong'

# Headers
ACCEPT = '*/*'
ACCEPT_ENCODING = 'gzip, deflate, br'
ACCEPT_LANGUAGE = 'en-US,en;q=0.9'
CONNECTION = 'keep-alive'
CONTENT_TYPE = 'application/json'
USER_AGENT = 'purrsongAppV3/2 CFNetwork/1325.0.1 Darwin/21.1.0'

# Payload
APP_VERSION = "3.8.3"
LANGUAGE = 'en'
TIME_ZONE = 'America/New_York'

TIMEOUT = 5 * 60

""" Query needed to obtain cookies. """
COOKIE_QUERY = "query CheckServerStatus($data: CheckServerStatusArgs!) {checkServerStatus(data: $data)}"

""" Query needed to obtain user token. """
TOKEN_QUERY = "mutation Login($data: LoginArgs!) {login(data: $data) {userId userToken hasCat __typename}}"

""" Query to discover litter boxes"""
DISCOVER_LB = '''query PurrsongTabLocations {getLocations {...LocationInfo getIots
                 {id lavviebot {nickname __typename} lavvieTag {id nickname __typename}
                 lavvieScanner {nickname __typename} pet {id cat {catMainPhoto nickname __typename} __typename} __typename} __typename}}
                 fragment LocationInfo on Location {id nickname locationRole __typename}'''

""" Query to discover cats """
DISCOVER_CATS = "query PetMain($data: PurrsongPetMainArgs!) " \
                "{purrsongPetMain(data: $data) {location" \
                "{id nickname hasUnknownCat hasLavviebot hasLavvieBox locationRole otherLocations" \
                "{...LocationInfo __typename} __typename} selectedPet {...SelectedPet hasLavvieTag petClips" \
                "{isDetectedOutlier __typename} __typename } otherPets {...OtherPetsForPetMain __typename } conditionScore dailyTotal" \
                "{poopCount rest grooming walk run woodadaCount __typename} hourlyData" \
                "{poopCount rest grooming walk run woodadaCount mainData __typename} __typename}} fragment LocationInfo on Location" \
                "{id nickname locationRole __typename} fragment SelectedPet on Pet {id petType petCode cat" \
                "{id nickname catSex catMainPhoto catAge catBirthDate catBirthDateCertainty __typename} dog" \
                "{id nickname dogSex dogMainPhoto dogAge __typename} __typename} fragment OtherPetsForPetMain on Pet" \
                "{id petType hasLavvieTag cat {id nickname catSex catMainPhoto catAge __typename} dog" \
                "{id nickname dogSex dogMainPhoto __typename} petClips {isDetectedOutlier __typename} __typename}"

""" Query to get status of specific litter box """
LB_STATUS = "query GetLavviebotDetails($data: IotIdArgs!) {getIotDetail(data: $data) " \
            "{id iotCodeTail latestFirmwareVersion lavviebot {id nickname routerSSID lavviebotLitters" \
            "{litterName userLitterType __typename} minBottomWeight beaconBattery recentLavviebotLog " \
            "{currentFirmwareVersion motorState topLitterStatus wasteDrawerStatus waitTime litterType " \
            "litterBottomAmount humidity temperature creationTime __typename} __typename} __typename}}"

""" Query to get cat log associated with a specific litter box"""
LB_CAT_LOG = "query GetLavviebotPoopRecord($data: GetIotCatRecordArgs!) {getLavviebotPoopRecord(data: $data) " \
             "{mostUsedCat {count catMainPhoto nickname __typename} catUsageHistory " \
             "{petId nickname catMainPhoto duration creationTime __typename} nextCursor __typename}}"

""" Query to get the most recent status for Unknown cat if one is present on the account"""
UNKNOWN_STATUS = "query GetUnknownPoopData($data: GetUnknownPoopDataArgs!) " \
                 "{getUnknownPoopData(data: $data) {...GraphData __typename}} fragment GraphData on PoopGraphDataResponse" \
                 "{timezone graphType period today avg30days avgTerm graphData __typename}"

""" Query to get most recent status for individual cat """
CAT_STATUS = "query GetPoopData($data: GetPoopGraphDataArgs!) " \
             "{getPoopData(data: $data) {...GraphData __typename}} fragment GraphData on PoopGraphDataResponse" \
             "{timezone graphType period today avg30days avgTerm graphData __typename}"


