# Message codes by name
MESSAGE_TYPE_DICT = {
    'vlogInformatie': [4],
    'detectie': [5,6],
    'overigeIngangen': [7,8],
    'interneFaseCyclus': [9,10],
    'overigeUitgangenGUS': [11,12],
    'externeSignaalgroep': [13,14],
    'overigeUitgangenWUS': [15,16],
    'gewensteProgrammaStatus': [17,18],
    'werkelijkeProgrammaStatus': [19,20],
    'thermometer': [23,24],
    'instructieVariabelen': [32],
    'OVHulpdienstInformatie': [34]
}
# The below message types only exist for the timestamp of their creation
WIPED_MESSAGES = ['instructieVariabelen', 'OVHulpdienstInformatie']