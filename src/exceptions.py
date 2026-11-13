# INF601 - Advanced Programming in Python
# Chase Coble
# Mini Project 7

#Emphasis that responses should be generalized, only internal identification, to prevent leaking.


#401
class BadTokenError(Exception):
    pass

#403
class ForbiddenError(Exception):
    pass

#404
class NotFoundError(Exception):
    pass

#409
class ConflictError(Exception):
    pass

#422
class MalformedError(Exception):
    pass

#423
class LockedError(Exception):
    pass

#429
class RateLimitedError(Exception):
    pass
