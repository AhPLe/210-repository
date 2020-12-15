#import enum

class Event_Enum():  #enum.Enum# Enum class used as base class for individual implementation
    #while this used to be an enum, some tests worked better with a generic object
    # and 'type-checking' idea for python 3
    pass

class Executive():
    def __init__(self, args):
        self.message_count = 0
        self.LP_dict = {}

    def insert_LP(self, LP, value_hash: int=-1):
        # while this is similar to any functions below,
        # this function does not have the correct 'type checking'
        # this function does not have reproducible has values
        # but it does not seem to be a necessary step in reproducibility
        if value_hash == -1:
            value_hash = hash(LP)
        if value_hash in self.LP_dict:
            raise KeyError('key {} already in LP_dict'.format(value_hash))
        self.LP_dict[value_hash] = LP
        return value_hash
    
