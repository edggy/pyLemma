#import proof

import util

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

tstPrf = util.defaultProofParser(prf)['Test Proof']
print tstPrf._inferences['MP']
print tstPrf
print tstPrf.isValid()

