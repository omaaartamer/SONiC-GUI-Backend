import pprint
from services.SSH_Services import parse_fan_output, parse_psu_output

# Sample Fan CLI output
cli_output_fans = """
Drawer    LED    FAN      Speed   Direction  Presence  Status  Timestamp
FanTray1  green  FAN-1F   40%     exhaust    Present   OK      20250815 14:29:02
FanTray1  green  FAN-1R   40%     exhaust    Present   OK      20250815 14:29:02
FanTray2  green  FAN-2F   40%     exhaust    Present   OK      20250815 14:29:02
N/A       green  PSU-1 FAN-1 14% exhaust    Present   OK      20250815 14:29:03
"""

# Sample PSU CLI output
cli_output_psus = """
PSU    Model    Serial               HW Rev  Voltage (V)  Current (A)  Power (W)  Status    LED
PSU 1  YM-1401A SA080V062146002274   N/A     11.74        6.34         79.00      OK        green
PSU 2  YM-1401A SA080V062146002222   N/A     0.00         0.00         0.00       NOT OK    red
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
