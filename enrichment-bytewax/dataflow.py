from bytewax import operators as op
from bytewax.connectors.kafka import operators as kop
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow

flow = Dataflow("test")
inp = kop.input("in", flow, brokers=["kafka:9092"], topics=["orders"])
op.output("out", inp.oks, StdOutSink())
