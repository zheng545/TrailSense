from machine import I2C

def read_u8(dev, i2c, address):
  BUFFER = bytearray(1)
  BUFFER[0] = address & 0xFF
  i2c.writeto(dev, BUFFER, False)
  i2c.readfrom_into(19, BUFFER, True)
  return BUFFER[0]
  
def read_u16BE(dev, i2c, address):
  BUFFER = bytearray(1)
  BUFFER[0] = address & 0xFF
  BUFFER2 = bytearray(2)
  BUFFER2[0] = address & 0xFF
  
  i2c.writeto(dev, BUFFER, False)
  i2c.readfrom_into(19, BUFFER2, True)
  return (BUFFER2[0] << 8) | BUFFER2[1]
  
def write_u8(dev, i2c, address,val):
  BUFFER = bytearray(2)
  BUFFER[0] = address & 0xFF
  BUFFER[1] = val & 0xFF
  i2c.writeto(dev, BUFFER, False)

#i2c addresses
VCNL4010_I2CADDR_DEFAULT   = const(0x13)
VCNL4010_COMMAND           = const(0x80)
VCNL4010_PRODUCTID         = const(0x81)
VCNL4010_PROXRATE          = const(0x82)
VCNL4010_IRLED             = const(0x83)
VCNL4010_AMBIENTPARAMETER  = const(0x84)
VCNL4010_AMBIENTDATA       = const(0x85)
VCNL4010_PROXIMITYDATA     = const(0x87)
VCNL4010_INTCONTROL        = const(0x89)
VCNL4010_PROXINITYADJUST   = const(0x8A)
VCNL4010_INTSTAT           = const(0x8E)
VCNL4010_MODTIMING         = const(0x8F)
VCNL4010_MEASUREAMBIENT    = const(0x10)
VCNL4010_MEASUREPROXIMITY  = const(0x08)
VCNL4010_AMBIENTREADY      = const(0x40)
VCNL4010_PROXIMITYREADY    = const(0x20)

#frequencies
VCNL4010_1_95    = 0
VCNL4010_3_90625 = 1
VCNL4010_7_8125  = 2
VCNL4010_16_625  = 3
VCNL4010_31_25   = 4
VCNL4010_62_5    = 5
VCNL4010_125     = 6
VCNL4010_250 = 7

VCNL4010_AMBIENT_LUX_SCALE = 0.25 # Lux value per 16-bit result value.

class VCNL4010:
  def __init__(self,i2c):
    self.i2cInterface = i2c
    
  def startup(self, address = VCNL4010_I2CADDR_DEFAULT):
    self.address = address
    data = read_u8(self.address, self.i2cInterface, VCNL4010_PRODUCTID)
    self.setLEDcurrent(20)
    self.setFrequency(VCNL4010_16_625)
    write_u8(self.address, self.i2cInterface, VCNL4010_INTCONTROL, 0x08)
    return (data & 0xF0) == 0x20
    
  def setFrequency(self, freq):
    write_u8(self.address, self.i2cInterface, VCNL4010_MODTIMING, freq)
    
  def setLEDcurrent(self, current_10mA):
    if current_10mA > 20 :
      current_10mA = 20
    write_u8(self.address, self.i2cInterface, VCNL4010_IRLED, current_10mA)
    
  def getLEDcurrent(self, current_10mA):
    return read_u8(self.address, self.i2cInterface, VCNL4010_IRLED)
    
  def readAmbientLux(self):
    status = read_u8(self.address, self.i2cInterface, VCNL4010_INTSTAT)
    status &= ~0x80
    write_u8(self.address, self.i2cInterface, VCNL4010_INTSTAT, status)
    # Grab an ambient light measurement.
    write_u8(self.address, self.i2cInterface, VCNL4010_COMMAND, VCNL4010_MEASUREAMBIENT)
    # Wait for result, then read and return the 16-bit value.
    while True:
      result = read_u8(self.address, self.i2cInterface, VCNL4010_COMMAND)
      if result & VCNL4010_AMBIENTREADY:
        return read_u16BE(self.address, self.i2cInterface, VCNL4010_AMBIENTDATA)
    
  def readProximity(self):
    status = read_u8(self.address, self.i2cInterface, VCNL4010_INTSTAT)
    status &= ~0x80
    write_u8(self.address, self.i2cInterface, VCNL4010_INTSTAT, status)
    # Grab a proximity measurement.
    write_u8(self.address, self.i2cInterface, VCNL4010_COMMAND, VCNL4010_MEASUREPROXIMITY)
    # Wait for result, then read and return the 16-bit value.
    while True:
      result = read_u8(self.address, self.i2cInterface, VCNL4010_COMMAND)
      if result & VCNL4010_PROXIMITYREADY:
        return read_u16BE(self.address, self.i2cInterface, VCNL4010_PROXIMITYDATA)