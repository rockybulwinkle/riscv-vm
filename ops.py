import util
import functools
import collections

decode_lru_size = None

class OpCode:
    def __init__(self):
        pass

    @classmethod
    def decode(cls, instr):
        """
        Decode the bit fields of the instruction
        """
        raise NotImlementedError()
    @classmethod
    def execute(cls, op, state):
        raise NotImlementedError()

    @classmethod
    def call(cls, state):
        instr = state.mem.peek(state.regs.pc, 4)
        op = cls.decode(instr)
        return cls.execute(op, state)

class RType(OpCode):
    Op = collections.namedtuple("RTypeOps", "op rd funct3 rs1 rs2 funct7")
    @classmethod
    @functools.lru_cache(maxsize=decode_lru_size)
    def decode(cls, instr):
        op = util.extract_bitfield(instr, 6, 0)
        rd = util.extract_bitfield(instr, 11, 7)
        funct3 = util.extract_bitfield(instr, 14, 12)
        rs1 = util.extract_bitfield(instr, 19, 15)
        rs2 = util.extract_bitfield(instr, 24, 20)
        funct7 = util.extract_bitfield(instr, 31, 25)

        return RType.Op(op, rd, funct3, rs1, rs2, funct7)

class IType(OpCode):
    Op = collections.namedtuple("ITypeOps", "op rd funct3 rs1 imm")
    @classmethod
    @functools.lru_cache(maxsize=decode_lru_size)
    def decode(cls, instr):
        op = util.extract_bitfield(instr, 6, 0)
        rd = util.extract_bitfield(instr, 11, 7)
        funct3 = util.extract_bitfield(instr, 14, 12)
        rs1 = util.extract_bitfield(instr, 19, 15)
        imm = util.extract_bitfield(instr, 31, 20)

        return IType.Op(op, rd, funct3, rs1, imm)

    @classmethod
    def sign_extend(cls, imm):
        return util.sign_extend(imm, 11)

class SType(OpCode):
    Op = collections.namedtuple("STypeOps", "op funct3 rs1 rs2 imm")
    @classmethod
    @functools.lru_cache(maxsize=decode_lru_size)
    def decode(cls, instr):
        op = util.extract_bitfield(instr, 6, 0)
        imm_4_0 = util.extract_bitfield(instr, 11, 7) << 0
        funct3 = util.extract_bitfield(instr, 14, 12)
        rs1 = util.extract_bitfield(instr, 19, 15)
        rs2 = util.extract_bitfield(instr, 24, 20)
        imm_11_5 = util.extract_bitfield(instr, 31, 25) << 5

        imm = imm_11_5 | imm_4_0

        return SType.Op(op, funct3, rs1, rs2, imm)

    @classmethod
    def sign_extend(cls, imm):
        return util.sign_extend(imm, 11)

class BType(OpCode):
    Op = collections.namedtuple("BTypeOps", "op funct3 rs1 rs2 imm")
    @classmethod
    @functools.lru_cache(maxsize=decode_lru_size)
    def decode(cls, instr):
        op = util.extract_bitfield(instr, 6, 0)
        imm_11 = util.extract_bitfield(instr, 7,7) << 11
        imm_4_1 = util.extract_bitfield(instr, 11, 8) << 1
        funct3 = util.extract_bitfield(instr, 14, 12)
        rs1 = util.extract_bitfield(instr, 19, 15)
        rs2 = util.extract_bitfield(instr, 24, 20)
        imm_10_5 = util.extract_bitfield(instr, 30, 25) << 5
        imm_12 = util.extract_bitfield(instr, 31, 31) << 12

        imm = imm_12 | imm_11 | imm_10_5 | imm_4_1

        return BType.Op(op, funct3, rs1, rs2, imm)

    @classmethod
    def sign_extend(cls, imm):
        return util.sign_extend(imm, 12)

class UType(OpCode):
    Op = collections.namedtuple("UTypeOps", "op rd imm")
    @classmethod
    @functools.lru_cache(maxsize=decode_lru_size)
    def decode(cls, instr):
        op = util.extract_bitfield(instr, 6, 0)
        rd = util.extract_bitfield(instr, 11, 7)
        imm = util.extract_bitfield(instr, 31, 12) << 12

        return UType.Op(op, rd, imm)

    @classmethod
    def sign_extend(cls, imm):
        return util.sign_extend(imm, 31)


class JType(OpCode):
    Op = collections.namedtuple("JTypeOps", "op rd imm")
    @classmethod
    @functools.lru_cache(maxsize=decode_lru_size)
    def decode(cls, instr):
        op = util.extract_bitfield(instr, 6, 0)
        rd = util.extract_bitfield(instr, 11, 7)

        imm_19_12 = util.extract_bitfield(instr, 19, 12) << 12
        imm_11    = util.extract_bitfield(instr, 20, 20) << 11
        imm_10_1  = util.extract_bitfield(instr, 30, 21) << 1
        imm_20    = util.extract_bitfield(instr, 31, 31) << 20

        imm = imm_20 | imm_19_12 | imm_11 | imm_10_1

        return JType.Op(op, rd, imm)

    @classmethod
    def sign_extend(cls, imm):
        return util.sign_extend(imm, 20)



class LUI(UType):
    @classmethod
    def execute(cls, op, state):
        state.regs.set(op.rd, op.imm)


class AUIPC(UType):
    @classmethod
    def execute(cls, op, state):
        state.regs.set(op.rd, op.imm + state.regs.pc)

class JAL(JType):
    @classmethod
    def execute(cls, op, state):
        pc = state.regs.pc
        state.regs.set(op.rd, pc+4)

        return pc + JType.sign_extend(op.imm)

class JALR(IType):
    @classmethod
    def execute(cls, op, state):
        pc = state.regs.pc
        state.regs.set(op.rd, pc+4)

        return IType.sign_extend(op.imm) + state.regs.get(op.rs1)

class Branch(BType):
    BEQ= 0b000
    BNE= 0b001
    BLT= 0b100
    BGE= 0b101
    BLTU=0b110
    BGEU=0b111

    branchfuncs = dict()
    branchfuncs[BEQ]  = lambda rs1, rs2: rs1 == rs2
    branchfuncs[BNE] = lambda rs1, rs2: rs1 != rs2
    branchfuncs[BLT] = lambda rs1, rs2: rs1 < rs2
    branchfuncs[BGE] = lambda rs1, rs2: rs1 >= rs2
    branchfuncs[BLTU]= lambda rs1, rs2: (rs1&0xFFFFFFFF) < (rs2&0xFFFFFFFF)
    branchfuncs[BGEU]= lambda rs1, rs2: (rs1&0xFFFFFFFF) >= (rs2&0xFFFFFFFF)

    @classmethod
    def execute(cls, op, state):
        s_imm = BType.sign_extend(op.imm)
        rs1 = state.regs.get_signed(op.rs1)
        rs2 = state.regs.get_signed(op.rs2)

        funct3 = op.funct3

        if Branch.branchfuncs[funct3](rs1, rs2):
            return state.regs.pc + s_imm


class Load(IType):
    """
    LB = 0b000
    LH = 0b001
    LW = 0b010
    LBU = 0b100
    LHU = 0b101
    """
    valid_ops = (0,1,2,4,5)

    @classmethod
    def execute(cls, op, state):
        assert op.funct3 in Load.valid_ops
        s_imm = IType.sign_extend(op.imm)
        addr = state.regs.get(op.rs1)+s_imm

        num_bytes = 1<<(op.funct3&0b11)
        unsigned = op.funct3 & 0b100

        rval = state.mem.peek(addr, num_bytes)

        if not unsigned:
            rval = util.sign_extend(rval, num_bytes*8-1)
        

        state.regs.set(op.rd, rval)

class Store(SType):
    valid_ops = (0, 1, 2)
    @classmethod
    def execute(cls, op, state):
        assert op.funct3 in Load.valid_ops
        s_imm = IType.sign_extend(op.imm)
        addr = state.regs.get(op.rs1)+s_imm

        num_bytes = 1<<(op.funct3&0b11)
        state.mem.poke(addr, state.regs.get(op.rs2), num_bytes)

class ArithImm(IType):
    ADDI = 0b000
    SLTI = 0b010
    SLTIU= 0b011
    XORI = 0b100
    ORI  = 0b110
    ANDI = 0b111
    SLLI = 0b001
    SRI = 0b101 #SRLI vs SRAI is dependent on imm

    arithfuncts=[None]*8
    arithfuncts[ADDI] = lambda rs1, imm: rs1+imm
    arithfuncts[SLTI] = lambda rs1, imm: 1 if rs1<imm else 0
    arithfuncts[SLTIU] = lambda rs1, imm: 1 if (rs1&0xFFFFFFFF)<(imm&0xFFFFFFFF) else 0
    arithfuncts[XORI] = lambda rs1, imm: rs1^imm
    arithfuncts[ORI] = lambda rs1, imm: rs1|imm
    arithfuncts[ANDI] = lambda rs1, imm: rs1&imm

    def slli(rs1, imm):
        #This function is too complex to be written cleanly as a oneliner
        shamt = imm&0b11111
        if imm&0b111111100000 != 0:
            raise Exception("Invalid funct7 in slli")
        rs1 <<= shamt
        return rs1

    arithfuncts[SLLI] = slli

    def sri(rs1, imm):
        #This function is too complex to be written cleanly as a oneliner
        shamt = imm&0b11111
        if imm&0b111111100000 == 0:
            rs1 &= 0xFFFFFFFF
        elif imm&0b111111100000 != 0b010000000000:
            raise Exception("Invalid funct7 in sri: "+bin(imm>>5))
        rs1 >>= shamt
        return rs1

    arithfuncts[SRI] = sri
    arithfuncts=tuple(arithfuncts)

    @classmethod
    def execute(cls, op, state):
        s_imm = IType.sign_extend(op.imm)
        rs1 = state.regs.get_signed(op.rs1)
        val = ArithImm.arithfuncts[op.funct3](rs1, s_imm)
        state.regs.set(op.rd, val)


class ArithReg(RType):
    ADDSUB  =  0b000
    SLL     =  0b001
    SLT     =  0b010
    SLTU    =  0b011
    XOR     =  0b100
    SR      =  0b101
    OR      =  0b110
    AND     =  0b111

    arithfuncts=[None]*8

    def addsub(rs1, rs2, funct7):
        if funct7 == 0b0100000:
            return rs1-rs2
        else:
            return rs1+rs2
    arithfuncts[ADDSUB] = addsub
    arithfuncts[SLL] = lambda rs1, rs2, funct7: rs1 << (rs2&0b11111)
    arithfuncts[SLT] = lambda rs1, rs2, funct7: 1 if rs1 < rs2 else 0
    arithfuncts[SLTU] = lambda rs1, rs2, funct7:  1 if (rs1&0xFFFFFFFF) < (rs2&0xFFFFFFFF) else 0
    arithfuncts[XOR] = lambda rs1, rs2, funct7: rs1 ^ rs2
    def sr(rs1, rs2, funct7):
        #This function is too complex to be written cleanly as a oneliner
        shamt = rs2&0b11111
        if funct7 == 0:
            rs1 &= 0xFFFFFFFF
        elif funct7!= 0b0100000:
            raise Exception("Invalid funct7 in sr")
        rs1 >>= shamt
        return rs1


    arithfuncts[SR] = sr
    arithfuncts[OR] = lambda rs1, rs2, funct7: rs1 | rs2
    arithfuncts[AND] = lambda rs1, rs2, funct7: rs1 & rs2
    arithfuncts=tuple(arithfuncts)


    @classmethod
    def execute(cls, op, state):
        rs1 = state.regs.get_signed(op.rs1)
        rs2 = state.regs.get_signed(op.rs2)
        val = ArithReg.arithfuncts[op.funct3](rs1, rs2, op.funct7)
        state.regs.set(op.rd, val)


class Fence(IType):
    @classmethod
    def execute(cls, op, state):
        pass

class ECall(RType):
    @classmethod
    def execute(cls, op, state):
        #Machine class checks for return value "exit" and stops if it sees it
        return "exit"

op_lookup = dict()
op_lookup[0b0110111] = LUI
op_lookup[0b0010111] = AUIPC
op_lookup[0b1101111] = JAL
op_lookup[0b1100111] = JALR
op_lookup[0b1100011] = Branch
op_lookup[0b0000011] = Load
op_lookup[0b0100011] = Store
op_lookup[0b0010011] = ArithImm
op_lookup[0b0110011] = ArithReg
op_lookup[0b0001111] = Fence
op_lookup[0b1110011] = ECall


