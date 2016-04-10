#import proof

import util
import sys

prf = '''
inference
MP
if(P,Q)
P
Q
done

proof
Test Proof
5\tif(A,B)
6\tA
7\tB\tMP\t5,6
done
'''

#with open(sys.argv[1]) as f:
    #prf = f.read()

try:
    tstPrf = util.defaultProofParser(sys.argv[1])
    print tstPrf
    [tstPrf[i].setNumbering(lambda x: x+1) for i in tstPrf]
    print tstPrf['Test Proof']
    valid = tstPrf['Test Proof'].verify()
    if valid > 0:
        print 'Valid'
    else:
        print 'Invalid:\tError on line %d' % -valid
except Exception as e:
    print e.message

#for i in tstPrf:
    #print str(tstPrf[i].verify()) + ': ' + repr(tstPrf[i])
