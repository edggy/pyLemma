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

with open(sys.argv[1]) as f:
    prf = f.read()

#try:
tstPrf = util.defaultProofParser(prf)
#print tstPrf._inferences
print tstPrf['Test Proof']
print tstPrf['Test Proof'].verify()
#except Exception as e:
#    print e.message

for i in tstPrf:
    print tstPrf[i]
    print tstPrf[i].verify()
