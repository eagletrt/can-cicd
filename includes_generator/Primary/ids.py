NETWORK_VERSION = 1.2

# TOPIC PEDALS
TOPIC_PEDALS_MASK = 0b00000011111
TOPIC_PEDALS_FILTER = 0b00000000000
"""
Syncronization message from Steering Wheel or ECU to PCU for calibration purpose.
Message semantic: sets (max|min) value for accelerator pedal the moment PCU receives the message with the current read value.
"""
ID_SET_ACCELERATOR_RANGE = 0b10000000000
"""
This message contains accelarator ADC raw values used by PCU to set 0->255 range when sending accelerator value. This value is either sent by ECU or by PCU
"""
ID_PEDALS_ADC_RANGES = 0b10000100000
"""
Accelerator Pedal potentiometer Value. Average of 2 sensors normalized from 0 to 255, linear, 8bit total, unsigned.
"""
ID_ACCELERATOR_PEDAL_VAL = 0b00100000000
"""
Brake Pedal pressure sensor Value. Normalized from 0 to 255, linear, 8bit total, unsigned.
"""
ID_BRAKE_PEDAL_VAL = 0b00100100000
"""
PCU current status. Warnings and errors.
"""
ID_PCU_STATUS = 0b01000000000

# TOPIC BROADCAST
TOPIC_BROADCAST_MASK = 0b00000011111
TOPIC_BROADCAST_FILTER = 0b00000000001
ID_TIMESTAMP = 0b11000000001

# TOPIC STEER
TOPIC_STEER_MASK = 0b00000011111
TOPIC_STEER_FILTER = 0b00000000010
ID_TLM_STATUS = 0b00100000010
ID_CAR_STATUS = 0b00000000010

# TOPIC TLM
TOPIC_TLM_MASK = 0b00000011111
TOPIC_TLM_FILTER = 0b00000000011
ID_SET_TLM_STATUS = 0b00100000011

# TOPIC ECUnSTEERnCART
TOPIC_ECUnSTEERnCART_MASK = 0b00000011111
TOPIC_ECUnSTEERnCART_FILTER = 0b00000000100
ID_HV_VOLTAGE = 0b01100000100
ID_HV_CURRENT = 0b01100100100
ID_HV_TEMP = 0b01101000100
ID_HV_ERRORS = 0b00100000100
ID_TS_STATUS = 0b00000000100

# TOPIC BMS_HV
TOPIC_BMS_HV_MASK = 0b00000011111
TOPIC_BMS_HV_FILTER = 0b00000000101
ID_SET_TS_STATUS = 0b00000000101

# TOPIC ECU
TOPIC_ECU_MASK = 0b00000011111
TOPIC_ECU_FILTER = 0b00000000110
ID_STEER_STATUS = 0b00000000110
ID_SET_CAR_STATUS = 0b00000100110
ID_GET_CAR_STATUS = 0b00001000110

# TOPIC ECUnSTEER
TOPIC_ECUnSTEER_MASK = 0b00000011111
TOPIC_ECUnSTEER_FILTER = 0b00000000111
ID_LV_CURRENT = 0b01100000111
ID_LV_VOLTAGE = 0b01100100111
ID_LV_TEMPERATURE = 0b01101000111
ID_COOLING_STATUS = 0b01101100111

# TOPIC HANDCART
TOPIC_HANDCART_MASK = 0b00000011111
TOPIC_HANDCART_FILTER = 0b00000001000
ID_HV_CELLS_VOLTAGE = 0b01000001000
ID_HV_CELLS_TEMP = 0b01000101000
ID_SET_CHG_POWER = 0b00100001000
ID_CHG_STATUS = 0b00000001000
ID_SET_CHG_STATUS = 0b00000101000
ID_CHG_SETTINGS = 0b00001001000


