#coding:utf-8
import sys
from mako.template import Template
from xml.etree.ElementTree import *
from instInfo import constructInstInfo

class Config:
  """This is a proxy for XML config file."""

  def __init__(self, xmlFile):
    self.xmlroot = parse(xmlFile).getroot()

  def getInst(self, type):
    inst = self.xmlroot.find("./instructions/" + type)
    assert inst is not None, "inst is None(" + type + ")"
    return inst
  
  def getName(self, type):
    name = self.getInst(type).get("name")
    name is not None, "name is None(" + type + ")"
    return name
  
  def isUse(self, type):
    use = self.getInst(type).get("use", "true")
    return use != "false"
  
  def assertAvailable(self, type):
    assert self.isUse(type), 'Instruction %s must be supported.' % (getName(type))
    
  # attributes of <binary>
  def direction(self):
    self.binaryAttribute("direction")

  def endian(self):
    self.binaryAttribute("endian")

  def endian(self):
    self.binaryAttribute("endian")

  def constTableType(self):
    self.binaryAttribute("const_table_type")

  def tag(self):
    self.binaryAttribute("tag")

  def addressing(self):
    self.binaryAttribute("addressing")

  def romAddressing(self):
    self.binaryAttribute("rom_addressing")

  def endian(self):
    self.binaryAttribute("endian")

  def binaryAttribute(self, attr):
    attr = self.xmlroot.find(".//binary").get(attr)
    assert attr is not None, 'Binary attribute %s is None' % (attr)
    attr

config = Config(sys.argv[1])

# GUI が要求している命令が使えることを確認
for inst in ['ADD', 'SUB', 'SETLO', 'SETHI', 'SLLI', 'SRAI', 'FMOV', 'FNEG',
             'FADD', 'FSUB', 'FMUL', 'FDIV', 'FSQRT', 'LDI', 'STI', 'FLDI',
             'FSTI', 'BEQ', 'BLT', 'FBEQ', 'FBLT', 'BRANCH', 'JMPREG',
             'INPUTBYTE', 'OUTPUTBYTE', 'HALT']:
  config.assertAvailable(inst)

t = Template(filename=sys.argv[2], input_encoding="utf-8", output_encoding="utf-8", encoding_errors="replace")
print t.render(xmlroot=xmlroot, instInfo = constructInstInfo(config))

