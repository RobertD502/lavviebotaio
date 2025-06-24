BASE_URL = 'https://api.purrsong.co/purrsong'

# Headers
ACCEPT = '*/*'
ACCEPT_ENCODING = 'gzip, deflate, br'
ACCEPT_LANGUAGE = 'en-US,en;q=0.9'
CONNECTION = 'keep-alive'
CONTENT_TYPE = 'application/json'
USER_AGENT = 'purrsongAppV3/1 CFNetwork/3826.500.131 Darwin/24.5.0'

# Payload
APP_VERSION = "3.23.11"
LANGUAGE = 'en'
TIME_ZONE = 'America/New_York'

TIMEOUT = 5 * 60

"""Query for refreshing token if cookie and token has already been obtained."""
AUTO_LOGIN_QUERY = """
mutation AutoLogin($data: AutoLoginArgs!) {
  autoLogin(data: $data) {
    userId
    userToken
    __typename
  }
}
"""

""" Query needed to obtain cookies. """
COOKIE_QUERY = "query CheckServerStatus($data: CheckServerStatusArgs!) {checkServerStatus(data: $data)}"

""" Query needed to obtain user token. """
TOKEN_QUERY = "mutation Login($data: LoginArgs!) {login(data: $data) {userId userToken hasCat __typename}}"

""" Query to discover litter boxes"""
DISCOVER_DEVICES = '''query PurrsongTabLocations {getLocations {...LocationInfo getIots
                 {id lavviebot {nickname __typename} lavvieTag {id nickname __typename}
                 lavvieScanner {nickname __typename} pet {id cat {catMainPhoto nickname __typename} __typename} __typename} __typename}}
                 fragment LocationInfo on Location {id nickname locationRole hasUnknownCat __typename}'''

""" Query to discover cats """

DISCOVER_CATS = """
query CatMain($locationId: Int!, $showUnknown: Boolean!, $includeLavvieTag: Boolean = true, $includeDetailCatInfo: Boolean = true, $includeLocation: Boolean = true) {
  getPets(data: {locationId: $locationId}) {
    ...PetList
    __typename
  }
  purrsongUnknownPetMain(data: {locationId: $locationId}) @include(if: $showUnknown) {
    ...UnknownCatMainInfo
    __typename
  }
  getPetMainUnknownHealthData(data: {locationId: $locationId}) @include(if: $showUnknown) {
    ...UnknownHealthData
    __typename
  }
}
fragment PetList on Pet {
  id
  petCode
  lavvieTag @include(if: $includeLavvieTag) {
    id
    lavvieTagUid
    iotId
    __typename
  }
  cat {
    id
    nickname
    catSpecies
    catMainPhoto
    catAge @include(if: $includeDetailCatInfo)
    catSex @include(if: $includeDetailCatInfo)
    catLifeStage @include(if: $includeDetailCatInfo)
    catBirthDate @include(if: $includeDetailCatInfo)
    catBirthDateCertainty @include(if: $includeDetailCatInfo)
    __typename
  }
  locationId @include(if: $includeLocation)
  __typename
}
fragment UnknownCatMainInfo on PurrsongUnknownPetMainResponse {
  location {
    id
    nickname
    hasUnknownCat
    hasLavviebot
    locationRole
    otherLocations {
      ...LocationInfo
      __typename
    }
    __typename
  }
  conditionScore
  hourlyData {
    poopCount
    __typename
  }
  __typename
}
fragment LocationInfo on Location {
  id
  nickname
  locationRole
  hasLavvieBox
  hasLavviebot
  hasUnknownCat
  overseaSubscription {
    ...OverseaSubscription
    __typename
  }
  getIots {
    ...IotMainIot
    __typename
  }
  __typename
}
fragment OverseaSubscription on LocationOverseasSubscription {
  id
  status
  petIds
  creationTime
  currentSubscription {
    productId
    startDate
    __typename
  }
  __typename
}
fragment IotMainIot on Iot {
  id
  latestFirmwareVersion
  iotCodeTail
  activeDomesticLavvieCare {
    id
    status
    creationTime
    dueDate
    __typename
  }
  recentIotErrorLog {
    ...IotErrorLog
    __typename
  }
  lavviebot {
    id
    nickname
    routerSSID
    wifiStatus
    macAddress
    recentLavviebotLog {
      motorState
      topLitterStatus
      wasteDrawerStatus
      currentFirmwareVersion
      __typename
    }
    __typename
  }
  lavvieScanner {
    id
    nickname
    wifiStatus
    recentLavvieScannerLog {
      currentFirmwareVersion
      __typename
    }
    __typename
  }
  lavvieTag {
    id
    nickname
    currentFirmwareVersion
    battery
    recentConnectionTime
    lavvieTagUid
    recentLavvieTagLog {
      id
      __typename
    }
    __typename
  }
  lavvieBox {
    id
    nickname
    routerSSID
    wifiStatus
    lavvieBoxLitterReplSchedule {
      id
      litterReplPoopCount
      isActivate
      __typename
    }
    cumulativePoopCount
    recentLavvieBoxLog {
      currentFirmwareVersion
      __typename
    }
    hasInvalidWeight
    purchaseType
    __typename
  }
  iotSchedules {
    ...IotScheduleManage
    __typename
  }
  pet {
    id
    cat {
      id
      nickname
      catMainPhoto
      __typename
    }
    __typename
  }
  __typename
}
fragment IotErrorLog on IotErrorLog {
  id
  status
  creationTime
  __typename
}
fragment IotScheduleManage on IotSchedule {
  id
  item
  cycle
  criteriaDate
  scheduleDDay
  isIotScheduleDone
  iotId
  __typename
}
fragment UnknownHealthData on GetPetMainUnknownHealthDataResponse {
  bowelData {
    graphType
    difference
    value
    __typename
  }
  __typename
}
"""


""" Query to get status of specific litter box """
LB_STATUS = "query GetLavviebotDetails($data: IotIdArgs!) {getIotDetail(data: $data) " \
            "{id iotCodeTail latestFirmwareVersion lavviebot {id nickname routerSSID lavviebotLitters" \
            "{litterName userLitterType __typename} minBottomWeight beaconBattery recentLavviebotLog " \
            "{currentFirmwareVersion motorState topLitterStatus wasteDrawerStatus waitTime litterType " \
            "litterBottomAmount humidity temperature creationTime __typename} __typename} __typename}}"

""" Query to get cat log associated with a specific litter box"""
LB_CAT_LOG = """
query GetIotPoopRecord($data: GetIotPoopRecordArgs!) {
  getIotPoopRecord(data: $data) {
    mostUsedCat {
      count
      catMainPhoto
      nickname
      __typename
    }
    catUsageHistory {
      petId
      nickname
      catMainPhoto
      duration
      creationTime
      __typename
    }
    nextCursor
    __typename
  }
}
"""

""" Query to get the error log for a litter boc """
LB_ERROR_LOG = "query GetIotErrorLog($data: GetIotErrorLogArgs!) { getIotErrorLog(data: $data) { errorLogs { id status creationTime __typename } cursor hasMore __typename }}"

""" Query to get the most recent status for Unknown cat if one is present on the account"""

UNKNOWN_STATUS = """
query GetUnknownPoopData($locationId: Int!, $days: String!, $weight: String!, $poopCount: String!, $poopDuration: String!) {
  weightData: getUnknownPoopData(data: {locationId: $locationId, graphType: $weight, period: $days}) {
    timezone
    graphType
    period
    today
    avg30days
    avgTerm
    graphData
    __typename
  }
  poopCount: getUnknownPoopData(data: {locationId: $locationId, graphType: $poopCount, period: $days}) {
    timezone
    graphType
    period
    today
    avg30days
    avgTerm
    graphData
    __typename
  }
  poopDuration: getUnknownPoopData(data: {locationId: $locationId, graphType: $poopDuration, period: $days}) {
    timezone
    graphType
    period
    today
    avg30days
    avgTerm
    graphData
    __typename
  }
}
"""

""" Query to get most recent status for individual cat """

CAT_STATUS = """
query GetCatHealthInfo($locationId: Int!, $petId: Int!, $days: String!, $weight: String!, $poopCount: String!, $poopDuration: String!, $date: String) {
  getPetContents(data: {petId: $petId}) {
    petId
    calorieAnalysis {
      todayRecommendCalorieUntilSyncTime
      todayCalorieUntilSyncTime {
        value
        status
        __typename
      }
      todayLastSyncHour
      recommendPlayTime
      yesterdayRecommendCalorie
      yesterdayCalorie {
        value
        status
        __typename
      }
      __typename
    }
    bcs {
      inputCatWeight
      inputBcs
      beforeCatWeight
      beforeBcs
      afterCatWeight
      afterBcs
      afterBcsLogCreationTime
      canUpdate
      hasNewUserInput
      plannerSubCategories
      __typename
    }
    biologicalAge {
      catAge
      expectedWaitingTime
      biologicalAgeStatus
      biologicalAge
      recentBioLogicalAgeDate
      __typename
    }
    activityRank {
      expectedWaitingTime
      recentActivityRankWeek
      activityRank
      canUpdate
      __typename
    }
    __typename
  }
  getPetMainBowelData(data: {locationId: $locationId, petId: $petId}) {
    id
    bowelData {
      graphType
      difference
      value
      __typename
    }
    __typename
  }
  getPetMainActivityData(data: {petId: $petId}) {
    id
    recentLavvieTagSyncTime
    sleeping {
      id
      value
      difference
      __typename
    }
    activity {
      id
      value
      difference
      __typename
    }
    activityScore {
      id
      value
      difference
      __typename
    }
    resting
    walking
    running
    zoomies
    __typename
  }
  getYesterdayActivityScoreData(data: {petId: $petId}) {
    data
    __typename
  }
  weightData: getPoopData(data: {petId: $petId, graphType: $weight, period: $days}) {
    timezone
    graphType
    period
    today
    avg30days
    avgTerm
    graphData
    __typename
  }
  poopCount: getPoopData(data: {petId: $petId, graphType: $poopCount, period: $days}) {
    timezone
    graphType
    period
    today
    avg30days
    avgTerm
    graphData
    __typename
  }
  poopDuration: getPoopData(data: {petId: $petId, graphType: $poopDuration, period: $days}) {
    timezone
    graphType
    period
    today
    avg30days
    avgTerm
    graphData
    __typename
  }
  todayActivity: getCatHourlyData(data: {petId: $petId, date: $date}) {
    rest
    grooming
    walk
    run
    woodadaCount
    charging
    mainData
    id
    __typename
  }
}
"""

""" Query to get most recent status for individual LavvieScanner """

LAVVIE_SCANNER_STATUS = """
query GetLavvieScannerDetails($data: IotIdArgs!) {
  getIotDetail(data: $data) {
    id
    iotCodeTail
    latestFirmwareVersion
    lavvieScanner {
      id
      nickname
      wifiStatus
      routerSSID
      recentLavvieScannerLog {
        currentFirmwareVersion
        creationTime
        __typename
      }
      __typename
    }
    __typename
  }
}
"""

""" Query to get most recent status for individual LavvieTag """

LAVVIE_TAG_STATUS = """
query GetLavvieTagDetails($data: IotIdArgs!) {
  getIotDetail(data: $data) {
    id
    iotCodeTail
    latestFirmwareVersion
    pet {
      id
      cat {
        nickname
        catMainPhoto
        __typename
      }
      __typename
    }
    lavvieTag {
      nickname
      currentFirmwareVersion
      battery
      lavvieTagUid
      recentConnectionTime
      convulsionPushNoti
      recentLavvieTagLog {
        id
        __typename
      }
      __typename
    }
    __typename
  }
}
"""
