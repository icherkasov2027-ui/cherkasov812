class DomainException(Exception):
    """Базовий клас для всіх винятків нашої предметної області"""
    pass

class NotFoundException(DomainException):
    """Викидається, коли ресурс не знайдено (404)"""
    pass

class ConflictException(DomainException):
    """Викидається у разі конфлікту, наприклад, дублювання даних (409)"""
    pass

class ValidationException(DomainException):
    """Викидається при порушенні бізнес-правил валідації (422)"""
    pass