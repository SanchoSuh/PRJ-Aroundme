class EmptyQuerySetException(Exception) :
    def __str__(self) :
        return "EmptyQuerySetException"