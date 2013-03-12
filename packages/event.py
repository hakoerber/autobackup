class Event(object):
    """C#-like Event class with multiple handlers."""
    
    def __init__(self):
        self.__handlers = set()
    
    
    def add_handler(self, handler):
        self.__handlers.add(handler)
        
        
    def remove_handler(self, handler):
        if not handler in self.__handlers:
            raise ValueError("Handler not found.")
        else:
            self.handlers.remove(handler)
            
            
    def has_handler(self, handler):
        return handler in self.__handlers
            
            
    def count_handlers(self):
        return len(self.__handlers)
            
            
    def raise_event(self, *args, **kargs):
        for handler in self.__handlers:
            handler(*args, **kargs)
    
    
    # Override the += operator
    __iadd__ = add_handler
    # Override the -= operator
    __isub__ = remove_handler
    # Executed when the event is called with ()
    __call__ = raise_event
    __len__ = count_handlers
