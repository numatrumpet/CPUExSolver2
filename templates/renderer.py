#coding:utf-8
import sys
from mako.template import Template
from xml.etree.ElementTree import *
from instInfo import constructInstInfo

class Config:
  """This is a proxy for XML config file."""

  def __init__(self, xmlFile):
    self.xmlroot = parse(xmlFile).getroot()

    self.comment        = self.xmlroot.find(".//comment").get("text").strip()
    self.romSize        = self.xmlroot.find(".//RAM").get("size")
    self.mnemonics      = self.xmlroot.find(".//mnemonics")
    self.constFloatRegs = self.xmlroot.find(".//constFloatRegs").get("num")
    self.constOps       = self.xmlroot.find(".//CONST")

    self.intRegsNum    = self.xmlroot.find(".//intRegs").get("num")
    self.intRegsPrefix = self.xmlroot.find(".//intRegs").get("prefix")
    # %% を % に変換
    self.r = self.intRegsPrefix % ()

    self.floatRegsNum    = self.xmlroot.find(".//floatRegs").get("num")
    self.floatRegsPrefix = self.xmlroot.find(".//floatRegs").get("prefix")
    # %% を % に変換
    self.f = self.floatRegsPrefix % ()

    self.binaryFileType = self.xmlroot.find(".//binary").get('file-type', 'binary')

    self.setRegisters()
    self.setBinaryAttributes()

  def getInst(self, type):
    inst = self.xmlroot.find(".//" + type)
    assert inst is not None, "inst is None(" + type + ")"
    return inst

  def getName(self, type):
    name = self.getInst(type).get("name")
    name is not None, "name is None(" + type + ")"
    return name

  def getOp(self, type):
    op = self.getInst(type).get("op")
    op is not None, "op is None(" + type + ")"
    return op

  def getFunct(self, type):
    return self.getInst(type).get("funct")

  def isUse(self, type):
    use = self.getInst(type).get("use", "true")
    return use != "false"

  def assertAvailable(self, type):
    assert self.isUse(type), 'Instruction %s must be supported.' % (getName(type))

  # setup register constants
  def setRegisters(self):
    self.zeroRegNumber     = self.reservedRegister("zeroReg")
    self.frameRegNumber    = self.reservedRegister("frameReg")
    self.heapRegNumber     = self.reservedRegister("heapReg")
    self.oneRegNumber      = self.reservedRegister('oneReg')
    self.minusOneRegNumber = self.reservedRegister('minusOneReg')

    self.zeroReg     = self.r + self.zeroRegNumber
    self.frameReg    = self.r + self.frameRegNumber
    self.heapReg     = self.r + self.heapRegNumber
    self.oneReg      = self.r + self.oneRegNumber
    self.minusOneReg = self.r + self.minusOneRegNumber

    # リンクレジスタのindexが整数でないときは専用レジスタを使用する
    linkReg = self.xmlroot.find(".//linkReg").get("index")
    assert linkReg is not None, "LinkReg is None"
    self.linkRegNumber = linkReg
    if linkReg == "":
      self.linkReg = ""
      self.useLinkReg = False
    else:
      self.linkReg = self.r + linkReg
      self.useLinkReg = True

  def reservedRegister(self, name, strict=True):
    reg = self.xmlroot.find(".//" + name).get("index")
    assert reg is not None, "Register %s is None" % (name)
    if strict:
      assert reg.isdigit(), "Register %s is not digit" % (name)
    return reg

  # attributes of <binary>
  def setBinaryAttributes(self):
    self.direction             = self.binaryAttribute("direction")
    self.constTableType        = self.binaryAttribute("const-table-type")
    self.tag                   = self.binaryAttribute("tag", "0xffFFffFF")
    self.addressing            = self.binaryAttribute("addressing")
    self.romAddressing         = self.binaryAttribute("rom-addressing")
    self.endian                = self.binaryAttribute("endian")
    self.relativeAddressOffset = self.binaryAttribute("relative-address-offset", "0")
    self.isByteAddressing      = self.addressing == "byte"
    self.romIsByteAddressing   = self.romAddressing == "byte"
    self.isToBig               = self.direction == "toBig"
    self.addressingUnit        = 4 if self.isByteAddressing else 1

  def binaryAttribute(self, attr, default=None):
    val = self.xmlroot.find(".//binary").get(attr, default)
    assert val is not None, 'Binary attribute %s is None' % (attr)
    return val.strip()

if __name__ == '__main__':
  config = Config(sys.argv[1])

  # GUI が要求している命令が使えることを確認
  for inst in ['ADD', 'SUB', 'SETLO', 'SETHI', 'SLLI', 'SRAI', 'FMOV', 'FNEG',
               'FADD', 'FSUB', 'FMUL', 'FDIV', 'FSQRT', 'LDI', 'STI', 'FLDI',
               'FSTI', 'BEQ', 'BLT', 'FBEQ', 'FBLT', 'BRANCH', 'JMPREG',
               'INPUTBYTE', 'OUTPUTBYTE', 'HALT']:
    config.assertAvailable(inst)

  t = Template(filename=sys.argv[2], input_encoding="utf-8", output_encoding="utf-8", encoding_errors="replace")
  print t.render(config=config, instInfo = constructInstInfo(config))
