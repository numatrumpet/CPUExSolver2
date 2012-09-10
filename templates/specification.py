#!/usr/bin/env python
# encoding: UTF-8

# XML から直接 GUI が生成するような tsv の仕様ファイルを生成する

import sys
from xml.etree.ElementTree import *
from renderer import Config
from instInfo import constructInstInfo

xmlroot = parse(sys.argv[1]).getroot()
config = Config(sys.argv[1])
instInfo = constructInstInfo(config)

def x(key, attribute = None):
  obj = xmlroot.find('.//' + key)
  if attribute is None:
    return xmlroot.find('.//' + key)
  else:
    return obj.get(attribute)

def instInfoFor(type):
  for i in instInfo:
    if i['type'] == type:
      return i

generalRegistePrefix = x('intRegs', 'prefix')

print 'アーキテクチャ名\t%s' % (xmlroot.get("name"))
print 'バイナリファイルのエンディアン\t%s' % ('リトルエンディアン' if x('binary', 'endian') == 'LITTLE' else 'ビッグエンディアン')
print 'ROM（命令メモリを格納する領域）サイズ\t64KB(固定)'
print 'ROMアドレッシング\t%sアドレッシング' % ('バイト' if x('binary', 'rom-addressing') == 'byte' else 'ワード')
print 'RAM（プログラム実行時の作業用領域）サイズ\t%s' % (x('RAM', 'size'))
print 'RAMアドレッシング\t%sアドレッシング' % ('バイト' if x('binary', 'addressing') == 'byte' else 'ワード')

print 'コメントアウト記号\t%s' % (x('comment', 'text'))
print '整数レジスタ接頭辞\t%s' % (generalRegistePrefix)
print '浮動小数レジスタ接頭辞\t%s' % (x('floatRegs', 'prefix'))
print '整数レジスタ数\t%s' % (x('intRegs', 'num'))
print '浮動小数レジスタ数\t%s' % (x('floatRegs', 'num'))
print 'キャッシュに使う浮動小数レジスタ数\t%s' % (x('constFloatRegs', 'num'))

print 'ゼロレジスタ\t%s%s'     % (generalRegistePrefix, x('zeroReg', 'index'))
print 'フレームレジスタ\t%s%s' % (generalRegistePrefix, x('frameReg', 'index'))
print 'ヒープレジスタ\t%s%s'   % (generalRegistePrefix, x('heapReg', 'index'))
print 'リンクレジスタ\t%s'     % ("なし(内部)" if x('linkReg', 'index') == "" else generalRegistePrefix + x('linkReg', 'index'))
print '1固定レジスタ\t%s%s'   % (generalRegistePrefix, x('oneReg', 'index'))
print '-1固定レジスタ\t%s%s'   % (generalRegistePrefix, x('minusOneReg', 'index'))

print '\n'

print '命令形式'
print 'R\top(6bit)\trs(5bit)\trt(5bit)\trd(5bit)\tshamt(5bit)\tfunct(5bit)'
print 'I\top(6bit)\trs(5bit)\trt(5bit)\timm(16bit)'
print 'J\top(6bit)\ttarget(26bit)'

print '\n'

print '命令名\t説明\t命令形式\tアセンブリ形式\t擬似コード\top\t\t\t\t\t\tfunct'
instructions = [
  {'type': 'MOV'  , 'description': "%(CODE)\t値の複製\tR\t%(CODE) rt, rs\t%(arg0)s <- %(arg1)s"},
  {'type': 'ADD'  , 'description': "%(CODE)\tたし算\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s + %(arg2)s"},
  {'type': 'SUB'  , 'description': "%(CODE)\tひき算\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s - %(arg2)s"},
  {'type': 'MUL'  , 'description': "%(CODE)\tかけ算\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s * %(arg2)s"},
  {'type': 'DIV'  , 'description': "%(CODE)\tわり算\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s / %(arg2)s"},
  {'type': 'SLL'  , 'description': "%(CODE)\t論理左シフト\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s << %(arg2)s"},
  {'type': 'SLA'  , 'description': "%(CODE)\t論理右シフト\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s >> %(arg2)s"},
  {'type': 'SRL'  , 'description': "%(CODE)\t算術左シフト\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s << %(arg2)s"},
  {'type': 'SRA'  , 'description': "%(CODE)\t算術右シフト\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s >> %(arg2)s"},
  {'type': 'SHIFT', 'description': "%(CODE)\t論理シフト(値に応じて左右切替)\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s shift %(arg2)s"},
  {'type': 'AND'  , 'description': "%(CODE)\t論理積\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s & %(arg2)s"},
  {'type': 'OR'   , 'description': "%(CODE)\t論理和\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s | %(arg2)s"},
  {'type': 'NOR'  , 'description': "%(CODE)\t論理否定和\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s nor %(arg2)s"},
  {'type': 'XOR'  , 'description': "%(CODE)\t排他的論理和\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- %(arg1)s xor %(arg2)s"},
  {'type': 'NOT'  , 'description': "%(CODE)\tビット反転\tR\t%(CODE) rt, rs\t%(arg0)s <- not %(arg1)s"},

  {'type': 'SETLO', 'description': "%(CODE)\t下位16bitに即値代入\tI\t%(CODE) rs, imm\t%(arg0)s[0:15] <- imm"},
  {'type': 'SETHI', 'description': "%(CODE)\t上位16bitに即値代入\tI\t%(CODE) rs, imm\t%(arg0)s[16:31] <- imm"},
  {'type': 'ADDI'  , 'description':"%(CODE)\tたし算\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s + imm"},
  {'type': 'SUBI'  , 'description':"%(CODE)\tひき算\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s - imm"},
  {'type': 'MULI'  , 'description':"%(CODE)\tかけ算\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s * imm"},
  {'type': 'DIVI'  , 'description':"%(CODE)\tわり算\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s / imm"},
  {'type': 'SLLI'  , 'description':"%(CODE)\t論理左シフト\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s << imm"},
  {'type': 'SLAI'  , 'description':"%(CODE)\t論理右シフト\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s >> imm"},
  {'type': 'SRLI'  , 'description':"%(CODE)\t算術左シフト\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s << imm"},
  {'type': 'SRAI'  , 'description':"%(CODE)\t算術右シフト\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s >> imm"},
  {'type': 'SHIFTI', 'description':"%(CODE)\t論理シフト\n(値に応じて左右切替)\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s shift imm"},
  {'type': 'ANDI'  , 'description':"%(CODE)\t論理積\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s & imm"},
  {'type': 'ORI'   , 'description':"%(CODE)\t論理和\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s | imm"},
  {'type': 'NORI'  , 'description':"%(CODE)\t論理否定和\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s nor imm"},
  {'type': 'XORI'  , 'description':"%(CODE)\t排他的論理和\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- %(arg1)s xor imm"},

  {'type': 'FMOV'  , 'description': "%(CODE)\t値の複製\tR\t%(CODE) frt, frs\t%(arg0)s <- %(arg1)s"},
  {'type': 'FNEG'  , 'description': "%(CODE)\t符号反転\tR\t%(CODE) frt, frs\t%(arg0)s <- -%(arg1)s"},
  {'type': 'FSETLO', 'description': "%(CODE)\t下位16bitに即値代入\tI\t%(CODE) frs, imm\t%(arg0)s[0:15] <- imm"},
  {'type': 'FSETHI', 'description': "%(CODE)\t上位16bitに即値代入\tI\t%(CODE) frs, imm\t%(arg0)s[16:31] <- imm"},
  {'type': 'FADD'  , 'description': "%(CODE)\tたし算\tR\t%(CODE) frd, frs, frt\t%(arg0)s <- %(arg1)s + %(arg2)s"},
  {'type': 'FSUB'  , 'description': "%(CODE)\tひき算\tR\t%(CODE) frd, frs, frt\t%(arg0)s <- %(arg1)s - %(arg2)s"},
  {'type': 'FMUL'  , 'description': "%(CODE)\tかけ算\tR\t%(CODE) frd, frs, frt\t%(arg0)s <- %(arg1)s * %(arg2)s"},
  {'type': 'FMULN' , 'description': "%(CODE)\tかけ算して符号反転\tR\t%(CODE) frd, frs, frt\t%(arg0)s <- -(%(arg1)s * %(arg2)s)"},
  {'type': 'FDIV'  , 'description': "%(CODE)\tわり算\tR\t%(CODE) frd, frs, frt\t%(arg0)s <- %(arg1)s / %(arg2)s"},
  {'type': 'FINV'  , 'description': "%(CODE)\t逆数\tR\t%(CODE) frt, frs\t%(arg0)s <- 1 / %(arg1)s"},
  {'type': 'FINVN' , 'description': "%(CODE)\t逆数のマイナス\tR\t%(CODE) frt, frs\t%(arg0)s <- - 1 / %(arg1)s"},
  {'type': 'FSQRT' , 'description': "%(CODE)\t絶対値\tR\t%(CODE) frt, frs\t%(arg0)s <- fabs(%(arg1)s)"},
  {'type': 'FABS'  , 'description': "%(CODE)\t平方根\tR\t%(CODE) frt, frs\t%(arg0)s <- fsqrt(%(arg1)s)"},
  {'type': 'FLOOR' , 'description': "%(CODE)\t切り捨て\tR\t%(CODE) frt, frs\t%(arg0)s <- floor(%(arg1)s)"},
  {'type': 'FSIN'  , 'description': "%(CODE)\t正弦\tR\t%(CODE) frt, frs\t%(arg0)s <- fsin(%(arg1)s)"},
  {'type': 'FCOS'  , 'description': "%(CODE)\t余弦\tR\t%(CODE) frt, frs\t%(arg0)s <- fcos(%(arg1)s)"},
  {'type': 'FTAN'  , 'description': "%(CODE)\t正接\tR\t%(CODE) frt, frs\t%(arg0)s <- ftan(%(arg1)s)"},
  {'type': 'FATAN' , 'description': "%(CODE)\t逆正接\tR\t%(CODE) frt, frs\t%(arg0)s <- fatan(%(arg1)s)"},

  {'type': 'ITOF'  , 'description': "%(CODE)\tintをfloatにキャスト\tR\t%(CODE) frt, rs\t%(arg0)s <- (float)%(arg1)s"},
  {'type': 'IMOVF' , 'description': "%(CODE)\tバイナリ列をコピー\tR\t%(CODE) frt, rs\t%(arg0)s <- %(arg1)s"},
  {'type': 'FTOI'  , 'description': "%(CODE)\tfloatをintにキャスト\tR\t%(CODE) rt, frs\t%(arg0)s <- (int)%(arg1)s"},
  {'type': 'FMOVI' , 'description': "%(CODE)\tバイナリ列をコピー\tR\t%(CODE) rt, frs\t%(arg0)s <- %(arg1)s"},
  {'type': 'LDI'   , 'description': "%(CODE)\tメモリから整数レジスタへロード\tI\t%(CODE) rt, rs, imm\t%(arg0)s <- RAM[%(arg1)s + imm]"},
  {'type': 'STI'   , 'description': "%(CODE)\t整数レジスタをメモリへストア\tI\t%(CODE) rt, rs, imm\tRAM[%(arg1)s + imm] <- %(arg0)s"},
  {'type': 'LD'    , 'description': "%(CODE)\tメモリから整数レジスタへロード\tR\t%(CODE) rd, rs, rt\t%(arg0)s <- RAM[%(arg1)s + %(arg2)s]"},
  {'type': 'ST'    , 'description': "%(CODE)\t整数レジスタをメモリへストア\tR\t%(CODE) rd, rs, rt\tRAM[%(arg1)s + %(arg2)s] <- %(arg0)s"},
  {'type': 'FLDI'  , 'description': "%(CODE)\tメモリから浮動小数レジスタへロード\tI\t%(CODE) frt, rs, imm\t%(arg0)s <- RAM[%(arg1)s + imm]"},
  {'type': 'FSTI'  , 'description': "%(CODE)\t浮動小数レジスタをメモリへストア\tI\t%(CODE) frt, rs, imm\tRAM[%(arg1)s + imm] <- %(arg0)s"},
  {'type': 'FLD'   , 'description': "%(CODE)\tメモリから浮動小数レジスタへロード\tR\t%(CODE) frd, rs, rt\t%(arg0)s <- RAM[%(arg1)s + %(arg2)s]"},
  {'type': 'FST'   , 'description': "%(CODE)\t浮動小数レジスタをメモリへストア\tR\t%(CODE) frd, rs, rt\tRAM[%(arg1)s + %(arg2)s] <- %(arg0)s"},
  {'type': 'BEQ'   , 'description': "%(CODE)\t等しい\tI\t%(CODE) rs, rt, imm\tif %(arg0)s == %(arg1)s then goto (pc + imm)"},
  {'type': 'BNE'   , 'description': "%(CODE)\t等しくない\tI\t%(CODE) rs, rt, imm\tif %(arg0)s != %(arg1)s then goto (pc + imm)"},
  {'type': 'BLT'   , 'description': "%(CODE)\tより小さい\tI\t%(CODE) rs, rt, imm\tif %(arg0)s < %(arg1)s then goto (pc + imm)"},
  {'type': 'BLE'   , 'description': "%(CODE)\tより大きい\tI\t%(CODE) rs, rt, imm\tif %(arg0)s > %(arg1)s then goto (pc + imm)"},
  {'type': 'BGT'   , 'description': "%(CODE)\t以下\tI\t%(CODE) rs, rt, imm\tif %(arg0)s <= %(arg1)s then goto (pc + imm)"},
  {'type': 'BGE'   , 'description': "%(CODE)\t以上\tI\t%(CODE) rs, rt, imm\tif %(arg0)s >= %(arg1)s then goto (pc + imm)"},
  {'type': 'FBEQ'  , 'description': "%(CODE)\t等しい\tI\t%(CODE) frs, frt, imm\tif %(arg0)s == %(arg1)s then goto (pc + imm)"},
  {'type': 'FBNE'  , 'description': "%(CODE)\t等しくない\tI\t%(CODE) frs, frt, imm\tif %(arg0)s != %(arg1)s then goto (pc + imm)"},
  {'type': 'FBLT'  , 'description': "%(CODE)\tより小さい\tI\t%(CODE) frs, frt, imm\tif %(arg0)s < %(arg1)s then goto (pc + imm)"},
  {'type': 'FBLE'  , 'description': "%(CODE)\tより大きい\tI\t%(CODE) frs, frt, imm\tif %(arg0)s > %(arg1)s then goto (pc + imm)"},
  {'type': 'FBGT'  , 'description': "%(CODE)\t以下\tI\t%(CODE) frs, frt, imm\tif %(arg0)s <= %(arg1)s then goto (pc + imm)"},
  {'type': 'FBGE'  , 'description': "%(CODE)\t以上\tI\t%(CODE) frs\tfrt\timm\tif %(arg0)s >= %(arg1)s then goto (pc + imm)"},
  {'type': 'BRANCH'      , 'description': "%(CODE)\tラベルへジャンプ\tJ\t%(CODE) labelName\tgoto labelName"},
  {'type': 'JMPREG'      , 'description': "%(CODE)\tレジスタ値へジャンプ\tR\t%(CODE) rs\tgoto %(arg0)s"},
  {'type': 'JMP_LNK'     , 'description': "%(CODE)\tリンクしてラベルへジャンプ\tJ\t%(CODE) labelName\tlink register <- pc goto labelName"},
  {'type': 'JMPREG_LNK'  , 'description': "%(CODE)\tリンクしてレジスタ値へジャンプ\tR\t%(CODE) rs\tlink register <- pc goto %(arg0)s"},
  {'type': 'CALL'        , 'description': "%(CODE)\tフレームポインタを減らして リンクしてラベルへジャンプ\tJ\t%(CODE) labelName\tRAM[frame pointer] <- link register; frame pointer--; link register <- pc goto labelName"},
  {'type': 'CALLREG'     , 'description': "%(CODE)\tフレームポインタを減らして リンクしてレジスタ値へジャンプ\tR\t%(CODE) reg\tRAM[frame pointer] <- link register; frame pointer--; link register <- pc goto %(arg0)s"},
  {'type': 'RETURN'      , 'description': "%(CODE)\tフレームポインタを増やして リンクレジスタの値へジャンプ\tR\t%(CODE) op\tRAM[frame pointer] <- link register; frame pointer++; goto link register"},
  {'type': 'INPUTBYTE'   , 'description': "%(CODE)\t1byte読み込み\tR\t%(CODE) rs\t%(arg0)s <- ReadByte()"},
  {'type': 'INPUTWORD'   , 'description': "%(CODE)\t1word読み込み\tR\t%(CODE) rs\t%(arg0)s <- ReadWord()"},
  {'type': 'INPUTFLOAT'  , 'description': "%(CODE)\t1word浮動小数レジスタに読み込み\tR\t%(CODE) frs\t%(arg0)s <- ReadWord()"},
  {'type': 'OUTPUTBYTE'  , 'description': "%(CODE)\t1byte書き出し\tR\t%(CODE) rs\tWriteByte(%(arg0)s & 0xf)"},
  {'type': 'OUTPUTWORD'  , 'description': "%(CODE)\t1word書き出し\tR\t%(CODE) rs\tWriteWord(%(arg0)s)"},
  {'type': 'OUTPUTFLOAT' , 'description': "%(CODE)\t1word浮動小数レジスタから書き出し\tR\t%(CODE) frs\tWriteWord(%(arg0)s)"},
  {'type': 'HALT'        , 'description': "%(CODE)\tプログラムを終了\tR\t%(CODE)\tstop"}
]

for inst in instructions:
  inXml = x(inst['type'])
  formAsm = dict(zip(["arg" + str(v) for v in range(1000)], [signal.lower() for signal in instInfoFor(inst['type'])['formAsm'] if signal != "IMM" and signal != "LABEL" ]))

  if inXml.get('use') != "false":

    # assume prefix: 0b
    # TODO: CONST is not supported
    op = "\t" + "\t".join(list(inXml.get("op")[2:]))
    funct = "" if inXml.get("funct") is None else "\t" + "\t".join(list(inXml.get("funct")[2:]))
    print (inst['description'].replace('%(CODE)', inXml.get('name'))) % (formAsm) + op + funct
