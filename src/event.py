class Event(object):
    """C#-like Event class with multiple handlers."""
    
    def __init__(self):
        self.__handlers = set()
    
    
    def addHandler(self, handler):
        self.__handlers.add(handler)
        
        
    def removeHandler(self, handler):
        if not handler in self.__handlers:
            raise ValueError("Handler not found.")
        else:
            self.handlers.remove(handler)
            
            
    def isHandler(self, handler):
        return handler in self.__handlers
            
            
    def countHandlers(self):
        return len(self.__handlers)
            
            
    def raiseEvent(self, *args, **kargs):
        for handler in self.__handlers:
            handler(*args, **kargs)
    
    # Override the += operator
    __iadd__ = addHandler
    # Override the -= operator
    __isub__ = removeHandler
    # Called when the event is called with ()
    __call__ = raiseEvent
    __len__ = countHandlers
