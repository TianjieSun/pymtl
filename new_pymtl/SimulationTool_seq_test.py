#=========================================================================
# SimulationTool_seq_test.py
#=========================================================================
# Sequential logic tests for the SimulationTool class.

from Model          import *
from SimulationTool import *
from Bits           import Bits

#-------------------------------------------------------------------------
# Setup Sim
#-------------------------------------------------------------------------

def setup_sim( model ):
  model.elaborate()
  sim = SimulationTool( model )
  return sim

#-------------------------------------------------------------------------
# Register Tester
#-------------------------------------------------------------------------

def register_tester( model_type ):
  model = model_type( 16 )
  sim = setup_sim( model )
  model.in_.v = 8
  assert model.out == 0
  sim.cycle()
  assert model.out == 8
  model.in_.v = 9
  assert model.out == 8
  model.in_.v = 10
  sim.cycle()
  assert model.out == 10
  model.in_.v = 2
  sim.cycle()
  assert model.out == 2

#-------------------------------------------------------------------------
# RegisterOld
#-------------------------------------------------------------------------

class RegisterOld( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      s.out.next = s.in_.value

def test_RegisterOld():
  register_tester( RegisterOld )

#-------------------------------------------------------------------------
# RegisterBits
#-------------------------------------------------------------------------

class RegisterBits( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort  ( Bits( nbits ) )
    s.out = OutPort ( Bits( nbits ) )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      s.out.next = s.in_

def test_RegisterBits():
  register_tester( RegisterBits )

#-------------------------------------------------------------------------
# Register
#-------------------------------------------------------------------------

class Register( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      s.out.n = s.in_

def test_Register():
  register_tester( Register )

#-------------------------------------------------------------------------
# RegisterWrapped
#-------------------------------------------------------------------------

class RegisterWrapped( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )
  def elaborate_logic( s ):
    # Submodules
    # TODO: cannot use keyword "reg" for variable names when converting
    #       To! Check for this?
    s.reg0 = Register( s.nbits )
    # s.connections
    s.connect( s.in_, s.reg0.in_ )
    s.connect( s.out, s.reg0.out )

def test_RegisterWrapped():
  register_tester( RegisterWrapped )

#-------------------------------------------------------------------------
# RegisterWrappedChain
#-------------------------------------------------------------------------

class RegisterWrappedChain( Model ):
  def __init__( s, nbits ):
    s.nbits = nbits
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )
  def elaborate_logic( s ):
    # Submodules
    s.reg0 = Register( s.nbits )
    s.reg1 = Register( s.nbits )
    s.reg2 = Register( s.nbits )
    # s.connections
    s.connect( s.in_     , s.reg0.in_ )
    s.connect( s.reg0.out, s.reg1.in_ )
    s.connect( s.reg1.out, s.reg2.in_ )
    s.connect( s.reg2.out, s.out      )

def test_RegisterWrappedChain():
  model = RegisterWrappedChain( 16 )
  sim = setup_sim( model )
  sim.reset()
  model.in_.value = 8
  assert model.reg0.out.v ==  0
  assert model.reg1.out.v ==  0
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  sim.cycle()
  assert model.reg0.out.v ==  8
  assert model.reg1.out.v ==  0
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  model.in_.value = 9
  assert model.reg0.out.v ==  8
  assert model.reg1.out.v ==  0
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  model.in_.value = 10
  sim.cycle()
  assert model.reg0.out.v == 10
  assert model.reg1.out.v ==  8
  assert model.reg2.out.v ==  0
  assert model.out.v      ==  0
  sim.cycle()
  assert model.reg0.out.v == 10
  assert model.reg1.out.v == 10
  assert model.reg2.out.v ==  8
  assert model.out.v      ==  8
  sim.cycle()
  assert model.reg0.out.v == 10
  assert model.reg1.out.v == 10
  assert model.reg2.out.v == 10
  assert model.out.v      == 10

#-------------------------------------------------------------------------
# RegisterReset
#-------------------------------------------------------------------------

class RegisterReset( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort  ( nbits )
    s.out = OutPort ( nbits )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      if s.reset:
        s.out.n = 0
      else:
        s.out.n = s.in_

def test_RegisterReset():
  model = RegisterReset( 16 )
  sim   = setup_sim( model )
  model.in_.v = 8
  assert model.out.v == 0
  sim.reset()
  assert model.out.v == 0
  sim.cycle()
  assert model.out.v == 8
  model.in_.v = 9
  assert model.out.v == 8
  model.in_.v = 10
  sim.cycle()
  assert model.out.v == 10
  sim.reset()
  assert model.out.v == 0

#-------------------------------------------------------------------------
# SliceWriteCheck
#-------------------------------------------------------------------------
# Test updates to slices.
class SliceWriteCheck( Model ):

  def __init__( s, nbits ):
    assert nbits == 16
    s.in_ = InPort  ( 16 )
    s.out = OutPort ( 16 )

  def elaborate_logic( s ):
    s.connect( s.in_, s.out )

def test_SliceWriteCheck():
  import pytest

  model = SliceWriteCheck( 16 )
  model.elaborate()
  sim = setup_sim( model )
  assert model.out == 0

  # Test regular write
  model.in_.n = 8
  sim.cycle()
  assert model.out == 0b1000

  # Slice then .n, should pass
  model.in_[0].n = 1
  sim.cycle()
  assert model.out == 0b1001
  model.in_[4:8].n = 0b1001
  sim.cycle()
  assert model.out == 0b10011001

  # Test regular write
  model.in_.n = 8
  sim.cycle()
  assert model.out == 0b1000

  # .n then slice, should fail
  model.in_.n[0] = 1
  sim.cycle()
  with pytest.raises( AssertionError ):
    assert model.out == 0b1001
  model.in_.n[4:8] = 0b1001
  sim.cycle()
  with pytest.raises( AssertionError ):
    assert model.out == 0b10011001

#-------------------------------------------------------------------------
# SliceLogicWriteCheck
#-------------------------------------------------------------------------
# Test storing a Bits slice to a temporary, then writing it
class SliceTempWriteCheck( Model ):

  def __init__( s, nbits ):
    assert nbits == 16
    s.in_ = InPort  ( 16 )
    s.out = OutPort ( 16 )

  def elaborate_logic( s ):

    @s.posedge_clk
    def logic():
      s.out[0:8].n = s.in_[0:8]
      x = s.out[8:16]
      x.n          = s.in_[8:16]

def test_SliceTempWriteCheck():
  model = SliceTempWriteCheck( 16 )
  model.elaborate()
  sim = setup_sim( model )
  assert model.out == 0

  model.in_.value = 0x00AA
  sim.cycle()
  assert model.out == 0x00AA

  model.in_.value = 0xAA00
  sim.cycle()
  assert model.out == 0xAA00

#-------------------------------------------------------------------------
# MultipleWrites
#-------------------------------------------------------------------------
# Test to catch strange simulator behavior
class MultipleWrites( Model ):
  def __init__( s ):
    s.out = OutPort ( 16 )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      s.out.next = 4
      s.out.next = 1

def test_MultipleWrites():
  model = MultipleWrites()
  model.elaborate()
  sim = setup_sim( model )

  assert model.out == 0   # passes
  sim.cycle()
  assert model.out == 1   # passes
  sim.cycle()
  #assert model.out == 4  # passes
  assert model.out == 1   # FAILS
  sim.cycle()
  assert model.out == 1   # passes

#-------------------------------------------------------------------------
# BuiltinFuncs
#-------------------------------------------------------------------------
from new_pymtl import zext, sext
class BuiltinFuncs( Model ):
  def __init__( s ):
    s.in_  = InPort ( 4 )
    s.zout = OutPort( 8 )
    s.sout = OutPort( 8 )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      s.zout.next = zext( s.in_, 8 )
      s.sout.next = sext( s.in_, 8 )

def test_BuiltinFuncs():
  model = BuiltinFuncs()
  model.elaborate()
  sim = setup_sim( model )

  model.in_.value = 0x1
  sim.cycle()
  assert model.zout == 0x1
  assert model.sout == 0x1

  model.in_.value = 0xF
  sim.cycle()
  assert model.zout == 0x0F
  assert model.sout == 0xFF

#-------------------------------------------------------------------------
# GetMSB
#-------------------------------------------------------------------------
# Verify using params as slices works.
class GetMSB( Model ):
  def __init__( s, nbits ):
    s.msb = nbits - 1
    s.in_ = InPort ( nbits )
    s.out = OutPort(     1 )

  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      s.out.next = s.in_[s.msb]

def test_GetMSB():
  model = GetMSB( 5 )
  model.elaborate()
  sim = setup_sim( model )

  model.in_.value = 0b01010; sim.cycle(); assert model.out == 0
  model.in_.value = 0b11010; sim.cycle(); assert model.out == 1
  model.in_.value = 0b10000; sim.cycle(); assert model.out == 1
  model.in_.value = 0b00001; sim.cycle(); assert model.out == 0

