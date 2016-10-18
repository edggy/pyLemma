import sentence

class Operator(sentence.Sentence):

    def __len__(self):
        return 1

    def __contains__(self, item):
        return self == item

    def mapInto(self, other):
        '''
        e.g.
        '?P[?x]'.mapInto('if(A(y),B(y))')
        -> {'?P[@]':'if(A(@),B(@))', '?x':'y'}

        '?P[@a]'.mapInto('if(A(s(a)),B(s(a)))')
        -> {'?P[@]':'if(A(@),B(@))', '@a':'s(a)'}
        -> {'?P[@]':'if(A(s(@),B(s(@))))', '@a':'a'}

        '?P[@a]'.mapInto('if(A(s(a)),B(s(b)))')
        -> {'?P[@]':'if(@,B(s(b)))', '@a':'A(s(a))'}
        -> {'?P[@]':'if(A(@),B(s(b)))', '@a':'s(a)'}
        -> {'?P[@]':'if(A(s(@)),B(s(b)))', '@a':'a'}
        -> {'?P[@]':'if(A(s(a)),@)', '@a':'B(s(b))'}
        -> {'?P[@]':'if(A(s(a)),B(@))', '@a':'s(b)'}
        -> {'?P[@]':'if(A(s(a)),B(s(@)))', '@a':'b'}

        '?P[@Q(?x)]'.mapInto('if(A(s(a)),B(s(b)))')
        -> {'?P[@]':'if(A(@),B(s(b)))', '@Q':'s', '?x':'a'}
        -> {'?P[@]':'if(A(s(a)),B(@))', '@Q':'s', '?x':'b'}

        '?P[@Q(@x)]'.mapInto('if(A(s(a)),B(s(b)))')
        -> {'?P[@]':'if(@,B(s(b)))', '@Q':'A', '@x':'s(a)'}
        -> {'?P[@]':'if(A(@),B(s(b)))', '@Q':'s', '@x':'a'}
        -> {'?P[@]':'if(A(s(a)),@)', '@Q':'B', '@x':'s(b)'}
        -> {'?P[@]':'if(A(s(a)),B(@))', '@Q':'s', '@x':'b'}
        '''

        results = []

        # Example 1 -> '?P[@a]'.mapInto('if(A(s(a)),B(s(b)))')
        # Example 2 -> '?P[@Q(@x)]'.mapInto('if(A(s(a)),B(s(b)))')

        # Example 1 -> '?P'
        # Example 2 -> '?P'
        op = self[0]

        # Example 1 -> '?x'
        # Example 2 -> '@Q(@x)
        arg = self[1]

        # Example 1 & 2-> other = 'if(A(s(a)),B(s(b)))'
        for s in other.subSentences():
            # Example 1 & 2 -> 
            # s = 'if(A(s(a)),B(s(b)))'
            #   = 'A(s(a))'
            #   = 'B(s(b))'
            #   = 's(a)'
            #   = 's(b)'
            #   = 'a'
            #   = 'b'

            for mapping in arg.mapInto(s):
                # Example 1->
                # mapping = {'?x':'if(A(s(a)),B(s(b)))'}
                # ...
    
                # Example 2 -> 
                # mapping = None
                #          = {'@Q':'A', '@x:'s(a)}
                #          = {'@Q':'B', '@x:'s(b)}
                #          = {'@Q':'s', '@x:'a'}
                #          = {'@Q':'s', '@x:'b'}
                #          = None
                #          = None    
    
                # Ensure a mapping exists
                if mapping is None:
                    continue
    
                subs = arg.subsitute(mapping)
                # Example 1 -> 
                # subs = 'if(A(s(a)),B(s(b)))'
                #      = 'A(s(a))'
                # ...
    
                # Example 2 ->
                # subs = N/A
                #      = 'A(s(a))'
                # ...            
    
                structure = other.subsitute({subs:sentence.SentenceFactory.generateWff('')})
                # Example 1 ->
                # structure = '@'
                #           = 'if(@,B(s(b)))'
                #           = ...
    
                # Example 2 -> 
                # structure = N/A
                #           = 'if(@,B(s(b)))'
                # ...
    
                # Ensure that we can map the operators
                if not op < structure.op():
                    continue
                
                mapping[op] = structure
                results.append(mapping)
                
        return results





