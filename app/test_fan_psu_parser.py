import pprint
from services.SSH_Services import parse_fan_output, parse_psu_output, parse_temperature_output

# Sample Fan CLI output
cli_output_fans = """
Drawer    LED    FAN      Speed   Direction  Presence  Status  Timestamp
----------------------------------------------------------------------------------
FanTray1  green  FAN-1F   40%     exhaust    Present   OK      20250815 14:29:02
FanTray1  green  FAN-1R   40%     exhaust    Present   OK      20250815 14:29:02
FanTray2  green  FAN-2F   40%     exhaust    Present   OK      20250815 14:29:02
N/A       green  PSU-1 FAN-1 14% exhaust    Present   OK      20250815 14:29:03
"""

# Sample PSU CLI output
cli_output_psus = """
PSU    Model    Serial               HW Rev  Voltage (V)  Current (A)  Power (W)  Status    LED
----------------------------------------------------------------------------------------------------
PSU 1  YM-1401A SA080V062146002274   N/A     11.74        6.34         79.00      OK        green
PSU 2  YM-1401A SA080V062146002222   N/A     0.00         0.00         0.00       NOT OK    red
"""
# Sample Temperature CLI output
cli_output_temperature = """
Sensor       Location       Temperature (C)    Threshold (C)     Status      Timestamp
------------------------------------------------------------------------------------
Temp Sensor 1  CPU            45                 75                OK          2023-10-27 10:30:00
Temp Sensor 2  GPU            55                 85                WARNING     2023-10-27 10:30:01
Temp Sensor 3  Mainboard      38                 60                OK          2023-10-27 10:30:02
"""


# Test Fan Parser
parsed_fans = parse_fan_output(cli_output_fans)
print("✅ Parsed Fans:")
pprint.pprint(parsed_fans)

print("\n----------------------------------\n")

# Test PSU Parser
parsed_psus = parse_psu_output(cli_output_psus)
print("🔌 Parsed PSUs:")
pprint.pprint(parsed_psus)

# Test Temperature Parser
print("🌡️ Parsed Temperatures:")
pprint.pprint(parse_temperature_output(cli_output_temperature))
