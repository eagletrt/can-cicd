NETWORK_VERSION = 1.2

# TOPIC BROADCAST
TOPIC_BROADCAST_MASK = 0b00000011111
TOPIC_BROADCAST_FILTER = 0b00000000000
ID_TIMESTAMP = 0b11000000000

# TOPIC STEER
TOPIC_STEER_MASK = 0b00000011111
TOPIC_STEER_FILTER = 0b00000000001
ID_TLM_STATUS = 0b00100000001
ID_CAR_STATUS = 0b00000000001

# TOPIC TLM
TOPIC_TLM_MASK = 0b00000011111
TOPIC_TLM_FILTER = 0b00000000010
ID_SET_TLM_STATUS = 0b00100000010

# TOPIC ACUnSTEERnCART
TOPIC_ACUnSTEERnCART_MASK = 0b00000011111
TOPIC_ACUnSTEERnCART_FILTER = 0b00000000011
ID_HV_VOLTAGE = 0b01100000011
ID_HV_CURRENT = 0b01100100011
ID_HV_TEMP = 0b01101000011
ID_HV_ERRORS = 0b00100000011
ID_TS_STATUS = 0b00000000011

# TOPIC BMS_HV
TOPIC_BMS_HV_MASK = 0b00000011111
TOPIC_BMS_HV_FILTER = 0b00000000100
ID_SET_TS_STATUS = 0b00000000100

# TOPIC ACU
TOPIC_ACU_MASK = 0b00000011111
TOPIC_ACU_FILTER = 0b00000000101
ID_STEER_STATUS = 0b00000000101
ID_SET_CAR_STATUS = 0b00000100101
ID_GET_CAR_STATUS = 0b00001000101

# TOPIC ACUnSTEER
TOPIC_ACUnSTEER_MASK = 0b00000011111
TOPIC_ACUnSTEER_FILTER = 0b00000000110
ID_LV_CURRENT = 0b01100000110
ID_LV_VOLTAGE = 0b01100100110
ID_LV_TEMPERATURE = 0b01101000110
ID_COOLING_STATUS = 0b01101100110

# TOPIC HANDCART
TOPIC_HANDCART_MASK = 0b00000011111
TOPIC_HANDCART_FILTER = 0b00000000111
ID_HV_CELLS_VOLTAGE = 0b01000000111
ID_HV_CELLS_TEMP = 0b01000100111
ID_SET_CHG_POWER = 0b00100000111
ID_CHG_STATUS = 0b00000000111
ID_SET_CHG_STATUS = 0b00000100111
ID_CHG_SETTINGS = 0b00001000111


