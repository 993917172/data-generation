import os
import sys
import generator

def process(conf):
    gen = generator.Generator(conf)
    gen.generate()

if __name__ == "__main__":
    conf = sys.argv[1]
    process(conf)
