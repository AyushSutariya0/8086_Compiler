import streamlit as st
import pandas as pd
import numpy as np
import base64
import re

st.set_page_config(layout="wide")
st.markdown("""<style>body {background-color:white;}</style>""",unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: Black;'>21BEC122-Ayush Sutariya <br/> 21BEC131-Mahekkumar Varasada</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: Black;'>Computer Architecture Special Assignment</h4>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: red;'>8086 Assembler</h1>", unsafe_allow_html=True)
st.markdown("---")
c1,c2=st.columns((2,1))

REGISTERS_INFO={"AH":"00","AL":"00","BH":"00","BL":"00","CH":"00","CL":"00","DH":"00","DL":"00"}
Registers16=("AX","BX","CX","DX")
Registers8=("AL","BL","CL","DL","AH","BH","CH","DH")
FLAG_INFO={'OF':'0','DF':'0','IF':'0','TF':'0','SF':'0','ZF':'0','AC':'0','PF':'0','CF':'0'}
LABEL = {}

OPCODE = {'MOV':'000000','INC':'000001','DEC':'000010','ADD':'000011','SUB':'000100','ADC':'000101','SBB':'000110','CLC':'010010','STC':'010011','CMC':'010100','STD':'010101','CLD':'010110','STI':'010111','SHL':'011000','CLI':'011001','SHR':'011010','SAR':'011011','ROL':'011100','ROR':'011101','RCR':'011110','RCL':'011111','MUL':'000111','DIV':'001000','CMP':'001001','CBW':'001010','CWD':'001011','NEG':'001100','AND':'001101','OR':'001110','NOT':'001111','XOR':'010000','XCHG':'010001'}
REGISTERS8_ADDRESS={"AL":"000","CL":"001","DL":"010","BL":"011","AH":"100","CH":"101","DH":"110","BH":"111"}
REGISTERS16_ADDRESS={"AX":"000","CX":"001","DX":"010","BX":"011","SP":"100","BP":"101","SI":"110","DI":"111"}
D_bit_selection={'MOV':'1','INC':'0','DEC':'0','ADD':'1','SUB':'1','ADC':'1','SBB':'1','MUL':'0','DIV':'0','CMP':'0','CBW':'0','CWD':'0','NEG':'0','AND':'1','OR':'1','NOT':'1','XOR':'1','XCHG':'0'}  # first operand register is dest - 1,source-0
W_bit_select ={"AL":"0","CL":"0","DL":"0","BL":"0","AH":"0","CH":"0","DH":"0","BH":"0","AX":"1","CX":"1","DX":"1","BX":"1","SP":"1","BP":"1","SI":"1","DI":"1"}

prevCarry = '-1'
#-------------------------------------------------------------------------------------------------------------------



#---------------------------------------------------Conversion-------------------------------------------
def hexToBinary(val,size):
    output = "{0:04b}".format(int(val,base=16))
    while len(output)<size :
        output = '0' + output
    return output

def binaryToHex(val,size):
    n = int(val,base=2)
    hexn = str(hex(n))
    hexn = hexn.upper()
    hexn = hexn[2:]
    while len(hexn)<size :
        hexn = '0' + hexn
    return hexn
#-------------------------------------------------------------------------------------------------------


#--------------------------------------------Getting 8 and 16 bit values--------------------------------
def getValueOf8(x):
    if x=='AL':
        data = REGISTERS_INFO['AL']
        return data 
    elif x=='AH':
        return REGISTERS_INFO['AH']
    elif x=='BL':
        return REGISTERS_INFO['BL']
    elif x=='BH':
        return REGISTERS_INFO['BH']
    elif x=='CL':
        return REGISTERS_INFO['CL']
    elif x=='CH':
        return REGISTERS_INFO['CH']
    elif x=='DL':
        return REGISTERS_INFO['DL']
    elif x=='DH':
        return REGISTERS_INFO['DH']

def getValueOf16(x):
    if x=='AX':
        return REGISTERS_INFO['AH']+REGISTERS_INFO['AL']
    elif x=='BX':
        return REGISTERS_INFO['BH']+REGISTERS_INFO['BL']
    elif x=='CX':
        return REGISTERS_INFO['CH']+REGISTERS_INFO['CL']
    elif x=='DX':
        return REGISTERS_INFO['DH']+REGISTERS_INFO['DL']
#------------------------------------------------------------------------------------------------------------------


#------------------------------------------------UPDATE-----------------------------------------------------------
def update_16(reg,val):
    upper=val[:2]
    lower=val[2:]
    if reg=="AX":
        REGISTERS_INFO['AL'] = lower
        REGISTERS_INFO['AH'] = upper
    elif reg=="BX":
        REGISTERS_INFO['BL'] = lower
        REGISTERS_INFO['BH'] = upper
    elif reg=="CX":
        REGISTERS_INFO['CL'] = lower
        REGISTERS_INFO['CH'] = upper
    elif reg=="DX":
        REGISTERS_INFO['DL'] = lower
        REGISTERS_INFO['DH'] = upper
        
def update_8(reg,val):
    if reg=='AL':
        REGISTERS_INFO['AL'] = val
    elif reg=='BL':
        REGISTERS_INFO['BL'] = val
    elif reg=='CL':
        REGISTERS_INFO['CL'] = val
    elif reg=='DL':
        REGISTERS_INFO['DL'] = val
    elif reg=='AH':
        REGISTERS_INFO['AH'] = val
    elif reg=='BH':
        REGISTERS_INFO['BH'] = val
    elif reg=='CH':
        REGISTERS_INFO['CH'] = val
    elif reg=='DH':
        REGISTERS_INFO['DH'] = val
#------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------- w-bit Selection------------------------------------------
def W_bit_selection2(fi_reg,se_reg):
    if(W_bit_select[fi_reg]=='0' and W_bit_select[se_reg]=="0"):
        W_bit = "0"
    elif(W_bit_select[fi_reg]=='1' and W_bit_select[se_reg]=="1"):
        W_bit = "1"
    else:
        error = "Both operand are not of same size!"
    return W_bit   

def W_bit_selection3or4(fi_reg):
    if(W_bit_select[fi_reg]=='0'):
        return "0"
    else:
        return "1"
#------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------Machine code generation--------------------------------------

#W big = 8 bit = 0 & 16 bit = 1
#D bit = first operand register is dest - 1,source-0
#2byte format = op_code 6 + D_bit 1 + W_bit 1 + mod 2 + reg 3 + rm 3
#3byte format = op_code 6 + D_bit 1 + W_bit 1 + mod 2 + reg 3 + rm 000 + high nibble 4 + lower nibble 4
#4byte format = op_code 6 + D_bit 1 + W_bit 1 + mod 2 + reg 3 + rm 000 + high byte 8 + lower byte 8

def gen_machine_code1(ins):
    op_code=OPCODE[ins]
    machine_code=op_code
    return machine_code
    
def gen_machine_code2(ins,fi_operand,se_operand):
    op_code = OPCODE[ins]
    D_bit=D_bit_selection[ins]
    W_bit=W_bit_selection2(fi_operand,se_operand)       # Logic 0 - 8 bits and 1 - 16 bits
    mod="11"
    if fi_operand in REGISTERS16_ADDRESS:
        reg = REGISTERS16_ADDRESS[fi_operand]
    else:
        reg = REGISTERS8_ADDRESS[fi_operand]
    
    if se_operand in REGISTERS16_ADDRESS:
        rm = REGISTERS16_ADDRESS[se_operand]
    else:
        rm = REGISTERS8_ADDRESS[se_operand]
    machine_code = op_code + D_bit + W_bit + mod + reg + rm +" "
    return machine_code

def gen_machine_code3(ins,fi_operand,se_operand):
    hi = se_operand[0:1]
    lo = se_operand[1:2]
    hi = hexToBinary(hi,4)
    lo = hexToBinary(lo,4)
    op_code = OPCODE[ins]
    D_bit=D_bit_selection[ins]
    W_bit=W_bit_selection3or4(fi_operand)       # Logic 0 - 8 bits and 1 - 16 bits
    mod="11"
    reg=REGISTERS8_ADDRESS[fi_operand]
    rm="000"
    hi_nibble = hi
    lo_nibble = lo
    machine_code = op_code + D_bit + W_bit + mod + reg + rm + hi_nibble + lo_nibble + " "
    return machine_code

def gen_machine_code4(ins,fi_operand,se_operand):
    hi = se_operand[0:2]
    lo = se_operand[2:4]
    hi = hexToBinary(hi,8)
    lo = hexToBinary(lo,8)
    op_code = OPCODE[ins]
    D_bit=D_bit_selection[ins]
    W_bit=W_bit_selection3or4(fi_operand)       # Logic 0 - 8 bits and 1 - 16 bits
    mod="11"
    reg=REGISTERS16_ADDRESS[fi_operand]
    rm="000"
    hi_byte = hi
    lo_byte = lo
    machine_code = op_code + D_bit + W_bit + mod + reg + rm + hi_byte + lo_byte + " "
    return machine_code
#------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------MOV-----------------------------------------------------------
def mov8RR(a,b):
    b = getValueOf8(b)
    # b=b[:-1]
    update_8(a,b)

def mov8RV(a,b):
    # b = getValueOf8(b)
    b=b[:-1]
    update_8(a,b)

def mov16RV(a,b):   
    # b = getValueOf16(b)
    b=b[:-1]
    update_16(a,b)

def mov16RR(a,b):
    # b=b[:-1]
    b = getValueOf16(b)

    update_16(a,b)
#------------------------------------------------------------------------------------------------------------------


#----------------------------------------------------ADDITION---------------------------------------------
def addit(a,b,c):
    if a=="1" and b=="1" and c=="1":
        return 1,1
    elif (a=="1" and b=="1") or (a=="1" and c=="1") or (b=="1" and c=="1"):
        return 0,1
    elif a=="1" or b=="1" or c=="1":
        return 1,0
    else:
        return 0,0

def add4VV(x,y,carry):
    global prevCarry
    x = x[:-1]
    y = y[:-1]
    
    binx = hexToBinary(x,4)
    biny = hexToBinary(y,4)
    
    ans = [0,0,0,0]
    for i in range(3,-1,-1):
        ans[i],tcarry = addBit(binx[i],biny[i],carry)
        carry = str(tcarry)
        if i==1:
            prevCarry = carry
    
    ansStr = ''.join([str(elem) for elem in ans])
    return ansStr,carry

def add8VV(a,b,carry):
    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    
    auxiCarry = 0
    
    # Performing 4 bit addition 4 times
    sum1,carry1 = add4VV(bit11,bit21,carry)
    sum2,carry2 = add4VV(bit12,bit22,str(carry1))

    auxiCarry = carry1
    carry = carry2
    sumV = sum2+sum1
    
    sumV = binaryToHex(sumV,2)
    
    return carry,auxiCarry,sumV

def add8RV(x,y,carry):
    # Getting Register Values
    xVal = getValueOf8(x)
    
    lowerNib1 = xVal[1:]+'H'
    lowerNib2 = y[1:2]+'H'
    higherNib1 = xVal[:1]+'H'
    higherNib2 = y[:1]+'H'
    
    sum1,carry = add4VV(lowerNib1,lowerNib2,carry)
    auxiCarry = carry
    sum2,carry = add4VV(higherNib1,higherNib2,carry)
    
    finSum = binaryToHex(sum2+sum1,2)
    if len(finSum)==1:
        finSum = '0' + finSum
   
    return carry,auxiCarry,finSum

def add8RR(x,y,carry):
    # Getting Register Values
    xVal = getValueOf8(x)
    yVal = getValueOf8(y)
    
    lowerNib1 = xVal[1:]+'H'
    lowerNib2 = yVal[1:]+'H'
    higherNib1 = xVal[:1]+'H'
    higherNib2 = yVal[:1]+'H'
    
    sum1,carry = add4VV(lowerNib1,lowerNib2,carry)
    auxiCarry = carry
    sum2,carry = add4VV(higherNib1,higherNib2,carry)
    
    finSum = binaryToHex(sum2+sum1,2)
    if len(finSum)==1:
        finSum = '0' + finSum

    return carry,auxiCarry,finSum

def add16VV(a,b,carry):
    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'
    bit13 = a[1:2]+'H'
    bit14 = a[:1]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    bit23 = b[1:2]+'H'
    bit24 = b[:1]+'H'
    
    auxiCarry = 0
    
    # Performing 4 bit addition 4 times
    sum1,carry1 = add4VV(bit11,bit21,carry)
    sum2,carry2 = add4VV(bit12,bit22,str(carry1))
    sum3,carry3 = add4VV(bit13,bit23,str(carry2))
    sum4,carry4 = add4VV(bit14,bit24,str(carry3))

    auxiCarry = carry2
    carry = carry4
    sumV = sum4+sum3+sum2+sum1
    
    sumV = binaryToHex(sumV,4)
    
    return carry,auxiCarry,sumV

def add16RV(a,b,carry):
    # Getting Register Values
    a = getValueOf16(a)
    
    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'
    bit13 = a[1:2]+'H'
    bit14 = a[:1]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    bit23 = b[1:2]+'H'
    bit24 = b[:1]+'H'
    
    auxiCarry = 0
    
    # Performing 4 bit addition 4 times
    sum1,carry1 = add4VV(bit11,bit21,carry)
    sum2,carry2 = add4VV(bit12,bit22,str(carry1))
    sum3,carry3 = add4VV(bit13,bit23,str(carry2))
    sum4,carry4 = add4VV(bit14,bit24,str(carry3))

    auxiCarry = carry2
    carry = carry4
    sumV = sum4+sum3+sum2+sum1
    
    sumV = binaryToHex(sumV,4)
    
    return carry,auxiCarry,sumV

def add16RR(a,b,carry):
    # Getting Register Values
    a = getValueOf16(a)
    b = getValueOf16(b)
    
    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'
    bit13 = a[1:2]+'H'
    bit14 = a[:1]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    bit23 = b[1:2]+'H'
    bit24 = b[:1]+'H'
    
    auxiCarry = 0

    # Performing 4 bit addition 4 times
    sum1,carry1 = add4VV(bit11,bit21,carry)
    sum2,carry2 = add4VV(bit12,bit22,str(carry1))
    sum3,carry3 = add4VV(bit13,bit23,str(carry2))
    sum4,carry4 = add4VV(bit14,bit24,str(carry3))

    auxiCarry = carry2
    carry = carry4
    sumV = sum4+sum3+sum2+sum1
    
    sumV = binaryToHex(sumV,4)

    return auxiCarry,carry,sumV
#-----------------------------------------------------------------------------------------------------------------


#----------------------------------------------------SUBTRACTION----------------------------------------------
def subBit(a,b,c):
    if a=="0" and b=="1" and c=="1":
        return 0,1
    elif a=="1" and b=="0" and c=="0":
        return 1,0
    elif (a=="0" and b=="0" and c=="0") or (a=="1" and b=="0" and c=="1") or (a=="1" and b=="1" and c=="0"):
        return 0,0
    else:
        return 1,1

def sub4VV(x,y,carry):
    global prevCarry
    x = x[:-1]
    y = y[:-1]

    binx = hexToBinary(x,4)
    biny = hexToBinary(y,4)
    
    ans = [0,0,0,0]
    for i in range(3,-1,-1):
        ans[i],tcarry = subBit(binx[i],biny[i],carry)
        carry = str(tcarry)
        if i==1:
            prevCarry = carry
    
    ansStr = ''.join([str(elem) for elem in ans])
    return ansStr,carry

def sub8RV(x,y,carry):
    xVal = getValueOf8(x)
    lowerNib1 = xVal[1:]+'H'
    lowerNib2 = y[1:2]+'H'
    higherNib1 = xVal[:1]+'H'
    higherNib2 = y[:1]+'H'
    
    sum1,carry = sub4VV(lowerNib1,lowerNib2,carry)
    auxiCarry = carry
    sum2,carry = sub4VV(higherNib1,higherNib2,carry)
    
    finSum = binaryToHex(sum2+sum1,2)
    if len(finSum)==1:
        finSum = '0' + finSum

    return carry,auxiCarry,finSum

def sub8RR(x,y,carry):
    xVal = getValueOf8(x)
    yVal = getValueOf8(y)
    
    lowerNib1 = xVal[1:]+'H'
    lowerNib2 = yVal[1:]+'H'
    higherNib1 = xVal[:1]+'H'
    higherNib2 = yVal[:1]+'H'
    
    sum1,carry = sub4VV(lowerNib1,lowerNib2,carry)
    auxiCarry = carry
    sum2,carry = sub4VV(higherNib1,higherNib2,carry)
    
    finSum = binaryToHex(sum2+sum1,2)
    if len(finSum)==1:
        finSum = '0' + finSum

    return carry,auxiCarry,finSum

def sub16RV(a,b,carry):
    a = getValueOf16(a)
    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'
    bit13 = a[1:2]+'H'
    bit14 = a[:1]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    bit23 = b[1:2]+'H'
    bit24 = b[:1]+'H'
    
    auxiCarry = 0
    
    # Performing 4 bit addition 4 times
    sum1,carry1 = sub4VV(bit11,bit21,carry)
    sum2,carry2 = sub4VV(bit12,bit22,str(carry1))
    sum3,carry3 = sub4VV(bit13,bit23,str(carry2))
    sum4,carry4 = sub4VV(bit14,bit24,str(carry3))

    auxiCarry = carry2
    carry = carry4
    sumV = sum4+sum3+sum2+sum1
    
    sumV = binaryToHex(sumV,4)

    return carry,auxiCarry,sumV

def sub16RR(a,b,carry):
    a = getValueOf16(a)
    b = getValueOf16(b)

    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'
    bit13 = a[1:2]+'H'
    bit14 = a[:1]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    bit23 = b[1:2]+'H'
    bit24 = b[:1]+'H'
    
    auxiCarry = 0

    # Performing 4 bit addition 4 times
    sum1,carry1 = sub4VV(bit11,bit21,carry)
    sum2,carry2 = sub4VV(bit12,bit22,str(carry1))
    sum3,carry3 = sub4VV(bit13,bit23,str(carry2))
    sum4,carry4 = sub4VV(bit14,bit24,str(carry3))

    auxiCarry = carry2
    carry = carry4
    sumV = sum4+sum3+sum2+sum1
    
    sumV = binaryToHex(sumV,4)

    return carry,auxiCarry,sumV
#------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------LOGICAL OPERATIONS (1-bit)--------------------------------------
def AND_OP(a,b):
    if a=='1' and b=="1":
        return "1"
    else:
        return "0"

def OR_OP(a,b):
    if a=='0' and b=='0':
        return "0"
    else:
        return "1"

def XOR_OP(a,b):
    if a==b:
        return '0'
    else:
        return '1'
    
def NOT_OP(a):
    if a=='1':
        return '0'
    else:
        return '1'

#---------------------------------------------------------------------------------------------------------------


#---------------------------------------------------AND---------------------------------------------------------
def AND_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + AND_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def AND_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + AND_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result

def AND_8RV(a,b):
    a = getValueOf8(a)
    b=b[:-1]
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + AND_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def AND_16RV(a,b):
    a = getValueOf16(a)
    b=b[:-1]

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + AND_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result    
#------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------OR---------------------------------------------------------
def OR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + OR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def OR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + OR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result

def OR_8RV(a,b):
    a = getValueOf8(a)
    b=b[:-1]
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + OR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def OR_16RV(a,b):
    a = getValueOf16(a)
    b=b[:-1]

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + OR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result   
#------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------NOT operation------------------------------------------------------
def NOT_8R(a):
    a=getValueOf8(a)
    
    bina=hexToBinary(a,8)
    
    result=""
    
    for i in range(8):
        result=result+NOT_OP(bina[i])
        
    result=binaryToHex(result,2)
    
    return result

def NOT_16R(a):
    a=getValueOf16(a)
    
    bina=hexToBinary(a,16)
    
    result=""
    
    for i in range(16):
        result=result+NOT_OP(bina[i])
        
    result=binaryToHex(result,4)
    
    return result
#------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------NEG operation------------------------------------------------------
def NEG_8R(a):
    result=NOT_8R(a)
    temp='01'
    
    a,b,result=add8VV(temp,result,'0')
    
    return result
    
def NEG_16R(a):
    result=NOT_16R(a)
    temp='0001'
    
    a,b,result=add16VV(temp,result,'0')
    
    return result 
#------------------------------------------------------------------------------------------------------------------


#----------------------------------------------------XOR operation--------------------------------------------------
def XOR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + XOR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def XOR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + XOR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result

def XOR_8RV(a,b):
    a = getValueOf8(a)
    b=b[:-1]
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + XOR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def XOR_16RV(a,b):
    a = getValueOf16(a)
    b=b[:-1]

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + XOR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result
#-------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------Left Shift operation--------------------------------------------------
def SHL_8RR(a,b):
    first = getValueOf8(a)             # Getting value of Register
    second = getValueOf8(b)            

    first = hexToBinary(first,8)          # Converting HEX to Binary
    second = hexToBinary(second,8)

    temp = first
    
    first = int(first,base=2)              # Converting Binary to Decimal
    second = int(second,base=2)
    
    carry = temp[min(second-1,len(temp)-1)]
    
    if second > len(temp):
        carry = 0
    
    first = first << second               # Shifting value

    first = bin(first)[-8:]              # Converting Decimal to Binary

    first = binaryToHex(first,2)         # Converting Binary to HEX
    
    return carry,first

def SHL_16RR(a,b):
    first = getValueOf16(a)             # Getting value of Register
    second = getValueOf16(b)            

    first = hexToBinary(first,16)          # Converting HEX to Binary
    second = hexToBinary(second,16)
    
    temp = first
    
    first = int(first,base=2)              # Converting Binary to Decimal
    second = int(second,base=2)
    
    carry = temp[min(second-1,len(temp)-1)]
    
    if second > len(temp):
        carry = 0
    
    first = first << second               # Shifting value

    first = bin(first)[-16:]              # Converting Decimal to Binary

    first = binaryToHex(first,4)         # Converting Binary to HEX
    
    return carry,first

def SHL_8RV(a,b):
    first = getValueOf8(a)             # Getting value of Register 
    b=b[:-1]
 
    first = hexToBinary(first,8)          # Converting HEX to Binary
    second = hexToBinary(b,8)

    temp = first
    
    first = int(first,base=2)              # Converting Binary to Decimal
    second = int(second,base=2)
    
    carry = temp[min(second-1,len(temp)-1)]
    
    if second > len(temp):
        carry = 0
    
    first = first << second               # Shifting value

    first = bin(first)[-8:]              # Converting Decimal to Binary

    first = binaryToHex(first,2)         # Converting Binary to HEX
    
    return carry,first

def SHL_16RV(a,b):
    first = getValueOf16(a)             # Getting value of Register 
    b=b[:-1]
 
    first = hexToBinary(first,16)          # Converting HEX to Binary
    second = hexToBinary(b,16)

    temp = first
    
    first = int(first,base=2)              # Converting Binary to Decimal
    second = int(second,base=2)
    
    carry = temp[min(second-1,len(temp)-1)]
    
    if second > len(temp):
        carry = 0

    first = first << second               # Shifting value

    first = bin(first)[-16:]              # Converting Decimal to Binary

    first = binaryToHex(first,4)         # Converting Binary to HEX
    
    return carry,first
#-------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------Right Shift operation--------------------------------------------------
def SHR(a,b,n):
    first = hexToBinary(a,n)
    second = hexToBinary(b,n)
    
    second = int(second,base=2)
    
    shift_str=''
    for i in range(second):
        shift_str += '0'
    
    first = shift_str + first
    finalVal = first[:n]
    carry=first[n]
    
    finalVal = binaryToHex(finalVal,n/4)
    return carry,finalVal

def SHR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    carry,finVal = SHR(a,b,8)
    return carry,finVal

def SHR_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    carry,finVal = SHR(a,b,8)
    return carry,finVal

def SHR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    carry,finVal = SHR(a,b,16)
    return carry,finVal

def SHR_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    carry,finVal = SHR(a,b,16)
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------Right Shift Arithmetic Operation--------------------------------------------------
def SAR(a,b,n):
    first = hexToBinary(a,n)
    second = hexToBinary(b,n)
    
    second = int(second,base=2)
    temp = first[0]
    shift_str=''
    for i in range(second):
        shift_str += temp
    
    first = shift_str + first
    finalVal = first[:n]
    carry=first[n]
    
    finalVal = binaryToHex(finalVal,n/4)
    return carry,finalVal

def SAR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    carry,finVal = SAR(a,b,8)
    return carry,finVal

def SAR_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    carry,finVal = SAR(a,b,8)
    return carry,finVal

def SAR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    carry,finVal = SAR(a,b,16)
    return carry,finVal

def SAR_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    carry,finVal = SAR(a,b,16)
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------Rotate Left Operation-------------------------------
def ROL(a,b,n):
    first = hexToBinary(a,n)
    second = hexToBinary(b,n)
    
    second = int(second,base=2)
    pos = second % n
    pos = pos
    finVal = ''
    for i in range(n):
        finVal = finVal + first[pos]
        pos = pos + 1
        pos = pos % (n)
    
    carry = finVal[n-1]
    finVal = binaryToHex(finVal,n/4)
    return carry,finVal

def ROL_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    carry,finVal = ROL(a,b,8)
    return carry,finVal

def ROL_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    carry,finVal = ROL(a,b,8)
    return carry,finVal

def ROL_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    carry,finVal = ROL(a,b,16)
    return carry,finVal

def ROL_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    carry,finVal = ROL(a,b,16)
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------Rotate Right Operation-------------------------------
def ROR(a,b,n):
    first = hexToBinary(a,n)
    second = hexToBinary(b,n)
    
    second = int(second,base=2)
    second=second%n
    
    temp_str=first[-second:]
    
    first = temp_str + first
    
    finVal=first[:n]
    carry = finVal[0]
    
    finVal = binaryToHex(finVal,n/4)
    
    return carry,finVal

def ROR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    carry,finVal = ROR(a,b,8)
    return carry,finVal

def ROR_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    carry,finVal = ROR(a,b,8)
    return carry,finVal

def ROR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    carry,finVal = ROR(a,b,16)
    return carry,finVal

def ROR_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    carry,finVal = ROR(a,b,16)
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#---------------------------------------Rotate Right with Carry----------------------------------------------
def RCR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,9)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCR_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,9)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,17)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCR_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,17)
    carry,finVal = val[0], val[1:]
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#---------------------------------------Rotate Left with Carry----------------------------------------------
def RCL_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,9)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCL_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,9)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCL_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,17)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCL_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,17)
    carry,finVal = val[0], val[1:]
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------MULTIPLY---------------------------------------------------
def mul(a,b,n):
    # converting it to Binary
    a = hexToBinary(a,n)
    b = hexToBinary(b,n)
    # converting value to decimal
    a = int(a,base=2)
    b = int(b,base=2)
    # Performing Multiplication Operation
    res = a*b

    # converting decimal to binary
    res = bin(res)
    
    # converting binary to HEX
    res = binaryToHex(res,n/2)
    tmp=int(n/4)
    return res[0:tmp],res[tmp:]

def mul8(b):
    a = getValueOf8('AL')
    b = getValueOf8(b)
    ah,al = mul(a,b,8)
    return ah,al

def mul16(b):
    a = getValueOf16('AX')
    b = getValueOf16(b)
    dx,ax = mul(a,b,16)
    return dx,ax
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------DIVISION---------------------------------------------------
def div(a,b,n):
    # converting it to Binary
    a = hexToBinary(a,2*n)
    b = hexToBinary(b,n)
    # converting value to decimal
    a = int(a,base=2)
    b = int(b,base=2)
    # Performing Multiplication Operation
    quot = int(a / b)
    rem = a % b

    # converting decimal to binary
    quot = bin(quot)
    rem = bin(rem)
    # converting binary to HEX
    tmp=int(n/4)
    quot = binaryToHex(quot,tmp)
    rem = binaryToHex(rem,tmp)
    print(tmp)

    return rem,quot

def div8(b):
    a = getValueOf16('AX')
    b = getValueOf8(b)
    ah,al = div(a,b,8)
    return ah,al

def div16(b):
    a = getValueOf16('DX') + getValueOf16('AX')
    b = getValueOf16(b)
    dx,ax = div(a,b,16)
    return dx,ax
#-------------------------------------------------------------------------------------------------------------------

def cbw():
    a = getValueOf8('AL')
    a = hexToBinary(a,8)
    s = ''
    for i in range(8):
        s = s + a[0]
    return s

def cwd():
    a = getValueOf16('AX')
    a = hexToBinary(a,16)
    s = ''
    for i in range(16):
        s = s + a[0]
    return s

#-------------------------------------------------------------------------------------------------------------------
def HashLabels():
    file = open('Assembly_code.txt','r')
    code = file.readlines()
    for i in range(len(code)):
        if code[i].find(':') != -1 :
            pos = code[i].find(':')
            LABEL[code[i][:pos]] = i

def Reg_update():
    global prevCarry
    
    main_f=open("Assembly_code.txt",'r')
    code=main_f.readlines()
    mcode_file = open("Machine_code.txt",'w')
    for i in range(len(code)):
        a=re.split(',| ',code[i])
        a = list(filter(None, a))             # Remove null strings from list
        
        a=[x.upper() for x in a]
        
        if len(a)==3:
            a[2]=a[2].strip()                   # Length of instruction can be of 2 or 3
        else:
            a[1]=a[1].strip()

        
        # Instructions Implemented
        if a[0]=="ADD":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = add16RR(a[1],a[2],'0')
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = add16RV(a[1],a[2],'0')
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = add8RR(a[1],a[2],'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = add8RV(a[1],a[2],'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
             
        elif a[0]=="SUB":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub16RR(a[1],a[2],'0')
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub16RV(a[1],a[2],'0')
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub8RR(a[1],a[2],'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub8RV(a[1],a[2],'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
        
        elif a[0]=="ADC":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = add16RR(a[1],a[2],FLAG_INFO['CF'])
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = add16RV(a[1],a[2],FLAG_INFO['CF'])
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = add8RR(a[1],a[2],FLAG_INFO['CF'])
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = add8RV(a[1],a[2],FLAG_INFO['CF'])
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
        
        elif a[0]=="SBB":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub16RR(a[1],a[2],FLAG_INFO['CF'])
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub16RV(a[1],a[2],FLAG_INFO['CF'])
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub8RR(a[1],a[2],FLAG_INFO['CF'])
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub8RV(a[1],a[2],FLAG_INFO['CF'])
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
                
        elif a[0]=="INC":
            if a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],"0001H")
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = add16RV(a[1],"0001H",'0')
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                update_16(a[1],sumV)
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                machine_code=gen_machine_code3(a[0],a[1],"01H")
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = add8RV(a[1],"01H",'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
        
        elif a[0]=="DEC":
            if a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],"0001H")
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub16RV(a[1],"0001H",'0')
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                machine_code=gen_machine_code3(a[0],a[1],"01H")
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub8RV(a[1],"01H",'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
        
        elif a[0]=="MOV":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                mov16RR(a[1],a[2])
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                mov16RV(a[1],a[2])
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                mov8RR(a[1],a[2])
            elif a[1] in Registers8:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                mov8RV(a[1],a[2])
        
        elif a[0]=="CLC":
            machine_code=gen_machine_code1(a[0])
            mcode_file.write(machine_code)
            FLAG_INFO['CF'] = '0'
          
        elif a[0]=="STC":
            machine_code=gen_machine_code1(a[0])
            mcode_file.write(machine_code)
            FLAG_INFO['CF']='1'
        
        elif a[0]=="CMC":
            machine_code=gen_machine_code1(a[0])
            mcode_file.write(machine_code)
            if FLAG_INFO['CF']=='1':
                FLAG_INFO['CF'] = '0'
            else:
                FLAG_INFO['CF'] = '1'

        elif a[0]=="STD":
            machine_code=gen_machine_code1(a[0])
            mcode_file.write(machine_code)
            FLAG_INFO['DF'] = '1'
        
        elif a[0]=="CLD":
            machine_code=gen_machine_code1(a[0])
            mcode_file.write(machine_code)
            FLAG_INFO['DF'] = '0'

        elif a[0]=="STI":
            machine_code=gen_machine_code1(a[0])
            mcode_file.write(machine_code)
            FLAG_INFO['IF'] = '1'
        
        elif a[0]=='CLI':
            machine_code=gen_machine_code1(a[0])
            mcode_file.write(machine_code)
            FLAG_INFO['IF'] = '0'
               
        elif a[0]=="AND":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = AND_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = AND_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = AND_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = AND_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            
        elif a[0]=='OR':
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = OR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = OR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = OR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = OR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
               
        elif a[0]=='NOT':
            if a[1] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],"AX")
                mcode_file.write(machine_code)
                result=NOT_16R(a[1])
                update_16(a[1],result)
            else:
                machine_code=gen_machine_code2(a[0],a[1],"AL")
                mcode_file.write(machine_code)   
                result=NOT_8R(a[1])
                update_8(a[1],result)
                
        elif a[0]=='XOR':
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = XOR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = XOR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = XOR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                result = XOR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
        
        elif a[0]=='NEG':
            if a[1] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],"AX")
                mcode_file.write(machine_code)
                result=NEG_16R(a[1])
                update_16(a[1],result)
            else:
                machine_code=gen_machine_code2(a[0],a[1],"AL")
                mcode_file.write(machine_code)
                result=NEG_8R(a[1])
                update_8(a[1],result)
                
        elif a[0]=="CMP":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub16RR(a[1],a[2],'0')
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub16RV(a[1],a[2],'0')
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub8RR(a[1],a[2],'0')
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,auxiCarry,sumV = sub8RV(a[1],a[2],'0')
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
                
        elif a[0]=="XCHG":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                temp1=getValueOf16(a[1])
                temp2=getValueOf16(a[2])
                update_16(a[1],temp2)
                update_16(a[2],temp1)  
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                temp1=getValueOf8(a[1])
                temp2=getValueOf8(a[2])
                update_8(a[1],temp2)
                update_8(a[2],temp1)
                
        elif a[0]=="SHL" or a[0]=='SAL':
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SHL_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SHL_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SHL_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SHL_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
                
        elif a[0]=="SHR":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SHR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SHR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SHR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SHR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
                
        elif a[0]=="SAR":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SAR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SAR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SAR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=SAR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
                
        elif a[0]=="ROL":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=ROL_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=ROL_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=ROL_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=ROL_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
                
        elif a[0]=="ROR":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=ROR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
                FLAG_INFO['SF'] = result[0]
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=ROR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['SF'] = result[0]
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=ROR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['SF'] = result[0]
                FLAG_INFO['CF'] = carry
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=ROR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['SF'] = result[0]
                FLAG_INFO['CF'] = carry
        
        elif a[0]=="RCR":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=RCR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=RCR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=RCR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=RCR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
        
        elif a[0]=="RCL":
            if a[1] in Registers16 and a[2] in Registers16:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=RCL_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                machine_code=gen_machine_code4(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=RCL_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                machine_code=gen_machine_code2(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=RCL_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                machine_code=gen_machine_code3(a[0],a[1],a[2])
                mcode_file.write(machine_code)
                carry,result=RCL_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry              

        elif a[0]=='MUL':
            if a[1] in Registers16:
                machine_code=gen_machine_code2(a[0],"AX",a[1])
                mcode_file.write(machine_code)
                dx,ax = mul16(a[1])
                update_16('DX',dx)
                update_16('AX',ax)
            elif a[1] in Registers8:
                machine_code=gen_machine_code2(a[0],"AL",a[1])
                mcode_file.write(machine_code)
                ah,al = mul8(a[1])
                update_8('AH',ah)
                update_8('AL',al)

        elif a[0]=='DIV':
            if a[1] in Registers16:
                machine_code=gen_machine_code2(a[0],"AX",a[1])
                mcode_file.write(machine_code)
                dx,ax = div16(a[1]) 
                update_16('DX',dx)
                update_16('AX',ax)
            elif a[1] in Registers8:
                machine_code=gen_machine_code2(a[0],"AL",a[1])
                mcode_file.write(machine_code)
                ah,al = div8(a[1])
                update_8('AH',ah)
                update_8('AL',al)

        elif a[0]=='CBW':
            machine_code=gen_machine_code2(a[0],"AH","AL")
            mcode_file.write(machine_code)
            val = cbw()
            update_8('AH',val)
        
        elif a[0]=='CWD':
            machine_code=gen_machine_code2(a[0],"DX","AX")
            mcode_file.write(machine_code)
            val = cwd()
            update_16('DX',val)
    
    c21,c22 =st.columns((1,1))
    
    with c21:     
        c21.markdown("<h4 style='text-align: left; color: Black;'>REGISTERS</h4>", unsafe_allow_html=True)
        for key, value in REGISTERS_INFO.items():
            st.write(key, ":", value)
    
    with c22:
        c22.markdown("<h4 style='text-align: left; color: Black;'>PSW</h4>", unsafe_allow_html=True)
        for key, value in FLAG_INFO.items():
            st.write(key, ":", value)
    
    # st.markdown("<h4 style='text-align: left; color: Blue;'>Machine Code</h4>", unsafe_allow_html=True)
    # file = open('Machine_code.txt','r')
    # code = file.readlines()
    # for i in range(len(code)):
    #     print(code[i])    
#-------------------------------------------------------------------------------------------------------------------
with c1:
    c1.markdown("<h2 style='text-align: left; color: Blue;'>Code:</h2>", unsafe_allow_html=True)
    Compile=st.button("Compile Code")
    code=st.text_area("",height=400)
    
    if Compile:
        file=open("Assembly_code.txt","w")
        file.write(code)
        file.close()
        HashLabels()

with c2:
   
    c2.markdown("<h2 style='text-align: center; color: Blue;'>Result :</h2>", unsafe_allow_html=True)
    Reg_update()

st.markdown("---")

c31,c32=st.columns((1,1))
with c31:
    c31.markdown("<h4 style='text-align: left; color: Blue;'>Short Terms</h4>", unsafe_allow_html=True) 
    display1={'OF':'Overflow Flag','DF':'Direction Flag','IF':'Interrupt Flag','TF':'Trap Flag','SF':'Sign Flag','ZF':'Zero Flag','AF':'Auxiliary Flag','PF':'Parity Flag','CF':'Carry Flag'}
    for key, value in display1.items():
        st.write(key, ":", value)

with c32:
    c32.markdown("<h4 style='text-align: left; color: Blue;'>Instructions can be compile</h4>", unsafe_allow_html=True)   
    display2={"ADD","SUB","ADC","SBB","INC","DEC","MOV","CTC","STC","CMC","STD","CLD","STI","CLI","AND","OR","NOT","XOR","NEG","CMP","XCHG","SHL","SAL","SHR","SLR","ROL","ROR","RCR","RCL","MUL","DIV","CBW","CWD"}
    st.table(display2)
    # for value in display2:
    #     st.write(value)
    
st.markdown("<h4 style='text-align: left; color: Blue;'>Machine Code</h4>", unsafe_allow_html=True)
file = open('Machine_code.txt','r')
code = file.readlines()
for i in range(len(code)):
    st.write(code[i])
