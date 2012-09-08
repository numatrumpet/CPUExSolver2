#!/usr/bin/env python
# encoding: UTF-8

# XML から直接 GUI が生成するような tsv の仕様ファイルを生成する

import sys
from xml.etree.ElementTree import *

xmlroot = parse(sys.argv[1]).getroot()

def x(key, attribute = None):
  obj = xmlroot.find('.//' + key)
  if attribute is None:
    return xmlroot.find('.//' + key)
  else:
    return obj.get(attribute)

generalRegistePrefix = x('intRegs', 'prefix')

print 'アーキテクチャ名	%s' % (xmlroot.get("name"))
print 'バイナリファイルのエンディアン	%s' % ('リトルエンディアン' if x('binary', 'endian') == 'LITTLE' else 'ビッグエンディアン')
print 'ROM（命令メモリを格納する領域）サイズ	64KB(固定)'
print 'ROMアドレッシング	%sアドレッシング' % ('バイト' if x('binary', 'rom-addressing') == 'byte' else 'ワード')
print 'RAM（プログラム実行時の作業用領域）サイズ	%s' % (x('RAM', 'size'))
print 'RAMアドレッシング	%sアドレッシング' % ('バイト' if x('binary', 'addressing') == 'byte' else 'ワード')

print 'コメントアウト記号	%s' % (x('comment', 'text'))
print '整数レジスタ接頭辞	%s' % (generalRegistePrefix)
print '浮動小数レジスタ接頭辞	%s' % (x('floatRegs', 'prefix'))
print '整数レジスタ数	%s' % (x('intRegs', 'num'))
print '浮動小数レジスタ数	%s' % (x('floatRegs', 'num'))
print 'キャッシュに使う浮動小数レジスタ数	%s' % (x('constFloatRegs', 'num'))

print 'ゼロレジスタ	%s%s'     % (generalRegistePrefix, x('zeroReg', 'index'))
print 'フレームレジスタ	%s%s' % (generalRegistePrefix, x('frameReg', 'index'))
print 'ヒープレジスタ	%s%s'   % (generalRegistePrefix, x('heapReg', 'index'))
print 'リンクレジスタ	%s'     % ("なし(内部)" if x('linkReg', 'index') == "" else generalRegistePrefix + x('linkReg', 'index'))
print '1固定レジスタ	%s%s'   % (generalRegistePrefix, x('oneReg', 'index'))
print '-1固定レジスタ	%s%s'   % (generalRegistePrefix, x('minusOneReg', 'index'))

print '\n'

print '命令形式'
print 'R	op(6bit)	rs(5bit)	rt(5bit)	rd(5bit)	shamt(5bit)	funct(5bit)'
print 'I	op(6bit)	rs(5bit)	rt(5bit)	imm(16bit)'
print 'J	op(6bit)	target(26bit)'

print '\n'

print '命令名	説明	命令形式	アセンブリ形式	擬似コード	op						funct'
instructions = [
  {'type': 'MOV'  , 'description': "%(CODE)\t値の複製\tR\t%(CODE) rt, rs\trt <- rs"},
  {'type': 'ADD'  , 'description': "%(CODE)\tたし算\tR\t%(CODE) rd, rs, rt\trd <- rs + rt"},
  {'type': 'SUB'  , 'description': "%(CODE)\tひき算\tR\t%(CODE) rd, rs, rt\trd <- rs - rt"},
  {'type': 'MUL'  , 'description': "%(CODE)\tかけ算\tR\t%(CODE) rd, rs, rt\trd <- rs * rt"},
  {'type': 'DIV'  , 'description': "%(CODE)\tわり算\tR\t%(CODE) rd, rs, rt\trd <- rs / rt"},
  {'type': 'SLL'  , 'description': "%(CODE)\t論理左シフト\tR\t%(CODE) rd, rs, rt\trd <- rs << rt"},
  {'type': 'SLA'  , 'description': "%(CODE)\t論理右シフト\tR\t%(CODE) rd, rs, rt\trd <- rs >> rt"},
  {'type': 'SRL'  , 'description': "%(CODE)\t算術左シフト\tR\t%(CODE) rd, rs, rt\trd <- rs << rt"},
  {'type': 'SRA'  , 'description': "%(CODE)\t算術右シフト\tR\t%(CODE) rd, rs, rt\trd <- rs >> rt"},
  {'type': 'SHIFT', 'description': "%(CODE)\t論理シフト(値に応じて左右切替)\tR\t%(CODE) rd, rs, rt\trd <- rs shift rt"},
  {'type': 'AND'  , 'description': "%(CODE)\t論理積\tR\t%(CODE) rd, rs, rt\trd <- rs & rt"},
  {'type': 'OR'   , 'description': "%(CODE)\t論理和\tR\t%(CODE) rd, rs, rt\trd <- rs | rt"},
  {'type': 'NOR'  , 'description': "%(CODE)\t論理否定和\tR\t%(CODE) rd, rs, rt\trd <- rs nor rt"},
  {'type': 'XOR'  , 'description': "%(CODE)\t排他的論理和\tR\t%(CODE) rd, rs, rt\trd <- rs xor rt"},
  {'type': 'NOT'  , 'description': "%(CODE)\tビット反転\tR\t%(CODE) rt, rs\trt <- not rs"},

  {'type': 'SETLO', 'description': "%(CODE)\t下位16bitに即値代入\tI\t%(CODE) rs, imm\trs[0:15] <- imm"},
  {'type': 'SETHI', 'description': "%(CODE)\t上位16bitに即値代入\tI\t%(CODE) rs, imm\trs[16:31] <- imm"},
  {'type': 'ADDI'  , 'description':"%(CODE)\tたし算\tI\t%(CODE) rt, rs, imm\trt <- rs + imm"},
  {'type': 'SUBI'  , 'description':"%(CODE)\tひき算\tI\t%(CODE) rt, rs, imm\trt <- rs - imm"},
  {'type': 'MULI'  , 'description':"%(CODE)\tかけ算\tI\t%(CODE) rt, rs, imm\trt <- rs * imm"},
  {'type': 'DIVI'  , 'description':"%(CODE)\tわり算\tI\t%(CODE) rt, rs, imm\trt <- rs / imm"},
  {'type': 'SLLI'  , 'description':"%(CODE)\t論理左シフト\tI\t%(CODE) rt, rs, imm\trt <- rs << imm"},
  {'type': 'SLAI'  , 'description':"%(CODE)\t論理右シフト\tI\t%(CODE) rt, rs, imm\trt <- rs >> imm"},
  {'type': 'SRLI'  , 'description':"%(CODE)\t算術左シフト\tI\t%(CODE) rt, rs, imm\trt <- rs << imm"},
  {'type': 'SRAI'  , 'description':"%(CODE)\t算術右シフト\tI\t%(CODE) rt, rs, imm\trt <- rs >> imm"},
  {'type': 'SHIFTI', 'description':"%(CODE)\t論理シフト\n(値に応じて左右切替)\tI\t%(CODE) rt, rs, imm\trt <- rs shift imm"},
  {'type': 'ANDI'  , 'description':"%(CODE)\t論理積\tI\t%(CODE) rt, rs, imm\trt <- rs & imm"},
  {'type': 'ORI'   , 'description':"%(CODE)\t論理和\tI\t%(CODE) rt, rs, imm\trt <- rs | imm"},
  {'type': 'NORI'  , 'description':"%(CODE)\t論理否定和\tI\t%(CODE) rt, rs, imm\trt <- rs nor imm"},
  {'type': 'XORI'  , 'description':"%(CODE)\t排他的論理和\tI\t%(CODE) rt, rs, imm\trt <- rs xor imm"},

  {'type': 'FMOV'  , 'description': "%(CODE)\t値の複製\tR\t%(CODE) frt, frs\tfrt <- frs"},
  {'type': 'FNEG'  , 'description': "%(CODE)\t符号反転\tR\t%(CODE) frt, frs\tfrt <- -frs"},
  {'type': 'FSETLO', 'description': "%(CODE)\t下位16bitに即値代入\tI\t%(CODE) frs, imm\tfrs[0:15] <- imm"},
  {'type': 'FSETHI', 'description': "%(CODE)\t上位16bitに即値代入\tI\t%(CODE) frs, imm\tfrs[16:31] <- imm"},
  {'type': 'FADD'  , 'description': "%(CODE)\tたし算\tR\t%(CODE) frd, frs, frt\tfrd <- frs + frt"},
  {'type': 'FSUB'  , 'description': "%(CODE)\tひき算\tR\t%(CODE) frd, frs, frt\tfrd <- frs - frt"},
  {'type': 'FMUL'  , 'description': "%(CODE)\tかけ算\tR\t%(CODE) frd, frs, frt\tfrd <- frs * frt"},
  {'type': 'FMULN' , 'description': "%(CODE)\tかけ算して符号反転\tR\t%(CODE) frd, frs, frt\tfrd <- -(frs * frt)"},
  {'type': 'FDIV'  , 'description': "%(CODE)\tわり算\tR\t%(CODE) frd, frs, frt\tfrd <- frs / frt"},
  {'type': 'FINV'  , 'description': "%(CODE)\t逆数\tR\t%(CODE) frt, frs\tfrt <- 1 / frs"},
  {'type': 'FINVN' , 'description': "%(CODE)\t逆数のマイナス\tR\t%(CODE) frt, frs\tfrt <- - 1 / frs"},
  {'type': 'FSQRT' , 'description': "%(CODE)\t絶対値\tR\t%(CODE) frt, frs\tfrt <- fabs(frs)"},
  {'type': 'FABS'  , 'description': "%(CODE)\t平方根\tR\t%(CODE) frt, frs\tfrt <- fsqrt(frs)"},
  {'type': 'FLOOR' , 'description': "%(CODE)\t切り捨て\tR\t%(CODE) frt, frs\tfrt <- floor(frs)"},
  {'type': 'FSIN'  , 'description': "%(CODE)\t正弦\tR\t%(CODE) frt, frs\tfrt <- fsin(frs)"},
  {'type': 'FCOS'  , 'description': "%(CODE)\t余弦\tR\t%(CODE) frt, frs\tfrt <- fcos(frs)"},
  {'type': 'FTAN'  , 'description': "%(CODE)\t正接\tR\t%(CODE) frt, frs\tfrt <- ftan(frs)"},
  {'type': 'FATAN' , 'description': "%(CODE)\t逆正接\tR\t%(CODE) frt, frs\tfrt <- fatan(frs)"},

  {'type': 'ITOF'  , 'description': "%(CODE)\tintをfloatにキャスト\tR\t%(CODE) frt, rs\tfrt <- (float)rs"},
  {'type': 'IMOVF' , 'description': "%(CODE)\tfloatをintにキャスト\tR\t%(CODE) rt, frs\trt <- (int)frs"},
  {'type': 'FTOI'  , 'description': "%(CODE)\tバイナリ列をコピー\tR\t%(CODE) frt, rs\tfrt <- rs"},
  {'type': 'FMOVI' , 'description': "%(CODE)\tバイナリ列をコピー\tR\t%(CODE) rt, frs\trt <- frs"},
  {'type': 'LDI'   , 'description': "%(CODE)\tメモリから整数レジスタへロード\tI\t%(CODE) rt, rs, imm\trt <- RAM[rs + imm]"},
  {'type': 'STI'   , 'description': "%(CODE)\t整数レジスタをメモリへストア\tI\t%(CODE) rt, rs, imm\tRAM[rs + imm] <- rt"},
  {'type': 'LD'    , 'description': "%(CODE)\tメモリから整数レジスタへロード\tR\t%(CODE) rd, rs, rt\trd <- RAM[rs + rt]"},
  {'type': 'ST'    , 'description': "%(CODE)\t整数レジスタをメモリへストア\tR\t%(CODE) rd, rs, rt\tRAM[rs + rt] <- rd"},
  {'type': 'FLDI'  , 'description': "%(CODE)\tメモリから浮動小数レジスタへロード\tI\t%(CODE) frt, rs, imm\tfrt <- RAM[rs + imm]"},
  {'type': 'FSTI'  , 'description': "%(CODE)\t浮動小数レジスタをメモリへストア\tI\t%(CODE) frt, rs, imm\tRAM[rs + imm] <- frt"},
  {'type': 'FLD'   , 'description': "%(CODE)\tメモリから浮動小数レジスタへロード\tR\t%(CODE) frd, rs, rt\tfrd <- RAM[rs + rt]"},
  {'type': 'FST'   , 'description': "%(CODE)\t浮動小数レジスタをメモリへストア\tR\t%(CODE) frd, rs, rt\tRAM[rs + rt] <- frd"},
  {'type': 'BEQ'   , 'description': "%(CODE)\t等しい\tI\t%(CODE) rs, rt, imm\tif rs == rt then goto (pc + imm)"},
  {'type': 'BNE'   , 'description': "%(CODE)\t等しくない\tI\t%(CODE) rs, rt, imm\tif rs != rt then goto (pc + imm)"},
  {'type': 'BLT'   , 'description': "%(CODE)\tより小さい\tI\t%(CODE) rs, rt, imm\tif rs < rt then goto (pc + imm)"},
  {'type': 'BLE'   , 'description': "%(CODE)\tより大きい\tI\t%(CODE) rs, rt, imm\tif rs > rt then goto (pc + imm)"},
  {'type': 'BGT'   , 'description': "%(CODE)\t以下\tI\t%(CODE) rs, rt, imm\tif rs <= rt then goto (pc + imm)"},
  {'type': 'BGE'   , 'description': "%(CODE)\t以上\tI\t%(CODE) rs, rt, imm\tif rs >= rt then goto (pc + imm)"},
  {'type': 'FBEQ'  , 'description': "%(CODE)\t等しい\tI\t%(CODE) frs, frt, imm\tif frs == frt then goto (pc + imm)"},
  {'type': 'FBNE'  , 'description': "%(CODE)\t等しくない\tI\t%(CODE) frs, frt, imm\tif frs != frt then goto (pc + imm)"},
  {'type': 'FBLT'  , 'description': "%(CODE)\tより小さい\tI\t%(CODE) frs, frt, imm\tif frs < frt then goto (pc + imm)"},
  {'type': 'FBLE'  , 'description': "%(CODE)\tより大きい\tI\t%(CODE) frs, frt, imm\tif frs > frt then goto (pc + imm)"},
  {'type': 'FBGT'  , 'description': "%(CODE)\t以下\tI\t%(CODE) frs, frt, imm\tif frs <= frt then goto (pc + imm)"},
  {'type': 'FBGE'  , 'description': "%(CODE)\t以上\tI\t%(CODE) frs\tfrt\timm\tif frs >= frt then goto (pc + imm)"},
  {'type': 'BRANCH'      , 'description': "%(CODE)\tラベルへジャンプ\tJ\t%(CODE) labelName\tgoto labelName"},
  {'type': 'JMPREG'      , 'description': "%(CODE)\tレジスタ値へジャンプ\tR\t%(CODE) rs\tgoto rs"},
  {'type': 'JMP_LNK'     , 'description': "%(CODE)\tリンクしてラベルへジャンプ\tJ\t%(CODE) labelName\tlink register <- pc goto labelName"},
  {'type': 'JMPREG_LNK'  , 'description': "%(CODE)\tリンクしてレジスタ値へジャンプ\tR\t%(CODE) rs\tlink register <- pc goto rs"},
  {'type': 'CALL'        , 'description': "%(CODE)\tフレームポインタを減らして リンクしてラベルへジャンプ\tJ\t%(CODE) labelName\tRAM[frame pointer] <- link register; frame pointer--; link register <- pc goto labelName"},
  {'type': 'CALLREG'     , 'description': "%(CODE)\tフレームポインタを減らして リンクしてレジスタ値へジャンプ\tR\t%(CODE) reg\tRAM[frame pointer] <- link register; frame pointer--; link register <- pc goto rs"},
  {'type': 'RETURN'      , 'description': "%(CODE)\tフレームポインタを増やして リンクレジスタの値へジャンプ\tR\t%(CODE) op\tRAM[frame pointer] <- link register; frame pointer++; goto link register"},
  {'type': 'INPUTBYTE'   , 'description': "%(CODE)\t1byte読み込み\tR\t%(CODE) rs\trs <- ReadByte()"},
  {'type': 'INPUTWORD'   , 'description': "%(CODE)\t1word読み込み\tR\t%(CODE) rs\trs <- ReadWord()"},
  {'type': 'INPUTFLOAT'  , 'description': "%(CODE)\t1word浮動小数レジスタに読み込み\tR\t%(CODE) frs\tfrs <- ReadWord()"},
  {'type': 'OUTPUTBYTE'  , 'description': "%(CODE)\t1byte書き出し\tR\t%(CODE) rs\tWriteByte(rs & 0xf)"},
  {'type': 'OUTPUTWORD'  , 'description': "%(CODE)\t1word書き出し\tR\t%(CODE) rs\tWriteWord(rs)"},
  {'type': 'OUTPUTFLOAT' , 'description': "%(CODE)\t1word浮動小数レジスタから書き出し\tR\t%(CODE) frs\tWriteWord(frs)"},
  {'type': 'HALT'        , 'description': "%(CODE)\tプログラムを終了\tR\t%(CODE)\tstop"}
]

for inst in instructions:
  inXml = x(inst['type'])
  if inXml.get('use') != "false":

    # assume prefix: 0b
    # TODO: CONST is not supported
    op = "\t" + "\t".join(list(inXml.get("op")[2:]))
    funct = "" if inXml.get("funct") is None else "\t" + "\t".join(list(inXml.get("funct")[2:]))
    print inst['description'].replace('%(CODE)', inXml.get('name')) + op + funct
