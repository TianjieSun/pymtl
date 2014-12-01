#=========================================================================
# TestRandomDelay_test.py
#=========================================================================

from pymtl      import *
from pclib.test import TestRandomDelay

from TestSimpleSource import TestSimpleSource
from TestSimpleSink   import TestSimpleSink

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, nbits, msgs, delay ):

    s.nbits = nbits
    s.msgs  = msgs
    s.delay = delay

  def elaborate_logic( s ):

    # Instantiate models

    s.src   = TestSimpleSource ( s.nbits, s.msgs  )
    s.delay = TestRandomDelay  ( s.nbits, s.delay )
    s.sink  = TestSimpleSink   ( s.nbits, s.msgs  )

    # Connect chain

    s.connect( s.src.out,   s.delay.in_ )
    s.connect( s.delay.out, s.sink.in_  )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()   + " | " + \
           s.delay.line_trace() + " | " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_test_random_delay( dump_vcd, delay ):

  # Test messages

  test_msgs = [
    0x0000,
    0x0a0a,
    0x0b0b,
    0x0c0c,
    0x0d0d,
    0xf0f0,
    0xe0e0,
    0xd0d0,
  ]

  # Instantiate and elaborate the model

  model = TestHarness( 16, test_msgs, delay )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( dump_vcd )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done() and sim.ncycles < 1000:
    sim.print_line_trace()
    sim.cycle()
  assert model.done()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# TestRandomDelay unit test with delay = 0
#-------------------------------------------------------------------------

def test_delay0( dump_vcd ):
  run_test_random_delay( get_vcd_filename() if dump_vcd else None, 0 )

#-------------------------------------------------------------------------
# TestRandomDelay unit test with delay = 1
#-------------------------------------------------------------------------

def test_delay1( dump_vcd ):
  run_test_random_delay( get_vcd_filename() if dump_vcd else None, 1 )

#-------------------------------------------------------------------------
# TestRandomDelay unit test with delay = 5
#-------------------------------------------------------------------------

def test_delay5( dump_vcd ):
  run_test_random_delay( get_vcd_filename() if dump_vcd else None, 5 )

#-------------------------------------------------------------------------
# TestRandomDelay unit test with delay = 20
#-------------------------------------------------------------------------

def test_delay20( dump_vcd ):
  run_test_random_delay( get_vcd_filename() if dump_vcd else None, 20 )
