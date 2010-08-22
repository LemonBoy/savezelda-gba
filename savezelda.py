# The Legend Of Zelda : A Link To The Past (GBA)
# Save checksum cracked by The Lemon Man (C) 2010

import sys, struct

# Put a NOP (thumb) to disable the save checksum check.
# USA : 0x08067e40 0x08067e4C
# EUR : 0x08068a08 0x08068a14

# 0x08067e24
def checksum (data):
	pos = 0
	i = len(data)
	sum = 0
	
	if not i or (i % 2) != 0:
		raise ValueError("The data lenght must be > 0 and an even number")
	
	while (i > 0):
		sum += (ord(data[pos]) | (ord(data[pos+1]) << 8)) ^ i
		pos += 2
		i   -= 2
		
	sum &= 0xFFFF
	
	return sum
	
def finalize (chksum1, chksum2):
	first = (chksum1 + chksum2) & 0xFFFF
	result = first << 16
	second = ~first & 0xFFFF
	second += 1
	result += second
	return result
	
def ask (msg, default):
	res = raw_input(msg)
	if len(res) is 0:
		return default
	return (res[0] == 'Y' or res[0] == 'y')

def check (save):
	try:
		fp = open(save, 'r+b')
	except:
		raise IOError	
	if fp.read(0x20) != 'A LINK TO THE PAST & 4 SWORDS,64':
		raise ValueError
	for slot in range(3):
		fp.seek(0x70 + (slot * 0x20))
		sum = struct.unpack("<H", fp.read(2))[0] << 16
		sum += struct.unpack("<H", fp.read(2))[0]
		type = fp.read(4)
		
		print 'Slot : %i\n\tType : %s' % (slot + 1, type)
		
		if sum == 0xffffffff:
			if type == 'INIT':
				print '\tUninitialized slot...skipping'
				continue
			elif type == 'DelF':
				print '\tDeleted slot...'
				if ask('\tRecover it ? [N] ', False):
					type = 'S4FT'
					fp.seek(0x74 + (slot * 0x20))
					fp.write(type)
					print '\tRecovered!'
				else:
					continue
			
		fp.seek(0x580 + (0x500 * slot))
		
		block = list(fp.read(0x40))

		print '\tCharacter name : %s\n\tText speed : %s\n\tBacklight intensity : %s' % \
			("".join(block[0x8:0xE]), \
			('Low', 'Mid', 'High', 'Err')[ord(block[0x24])], \
			('Low', 'Mid', 'High')[ord(block[0x25])])
			
		if ask('\tWould you like to change the character name [N] ', False):
			newname = raw_input('\tInsert the new name (if > 6 chars it will be cutted) ')
			newname = newname[:6]
			block[0x8:0xE] = struct.unpack('cccccc', newname + ('\x00' * (6 - len(newname))))
			fp.seek(0x580 + (0x500 * slot) + 8)
			fp.write(newname + ('\x00' * (6 - len(newname))))
			print '\tDone!'
			
		pbitmap = ord(block[0])
		powers = []
			
		if pbitmap == 0:
			powers.append('None')
		else:
			if pbitmap == 0x01 or pbitmap == 0x01 * 0x11:
				powers.append('Beam sword')
			elif pbitmap == 0x02 or pbitmap == 0x02 * 0x11:
				powers.append('Hurricane spin')
			elif pbitmap == (0x01 | 0x02) or pbitmap == (0x01 | 0x02) * 0x11:
				powers.append('Beam sword')
				powers.append('Hurricane spin')
				
		print '\tPowers : %s' % ", ".join(powers)
		
		if pbitmap is not (0x01 | 0x02) * 0x11:
			if ask('\tEnable the beam sword and hurricane spin ? [Y] ', True):
				block[0] = (0x01 | 0x02) * 0x11
				fp.seek(0x580 + (0x500 * slot))
				fp.write("\x33")
				print '\tDone!'
			
		shortchk = checksum(type)
		longchk = checksum(block)
		final = finalize(shortchk, longchk)
		
		print '\tChecksum : %x' % sum
		print '\tExpected : %x' % final
			
		if sum != final:
			print '\tChecksum mismatch!'
			if ask('\tCorrect the checksum? [Y] ', True):
				fp.seek(0x70 + (slot * 0x20))
				fp.write(struct.pack('<H', (final >> 16) & 0xFFFF))
				fp.write(struct.pack('<H', final & 0xFFFF))
				print '\tFixed!'
		else:
			print '\tChecksum correct!'
			
		if ask('\tDelete [N] ', False):
			fp.seek(0x70 + (slot * 0x20))
			fp.write(struct.pack('<I', 0xffffffff))
			fp.write('DelF')
			print '\tDeleted!'
			
	fp.close()
		
if __name__ == '__main__':
	print 'The Legend Of Zelda : A Link To The Past (GBA)\nSavegame Editor.\nCode/Checksum RE (C) 2010 The Lemon Man\n'
	if len(sys.argv) != 2:
		print 'Usage :\npython %s savename.sav\n' % sys.argv[0]
		sys.exit(0)
	
	try:
		check(sys.argv[1])
	except:
		print 'An error occurred while processing %s' % sys.argv[1]
