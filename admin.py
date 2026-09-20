from exceptions import MissingDataError , VaildDataError
from ORM import Database


class Admin:
    def __init__(self, db:Database):
        self.db = db
    #==============pagination==============
        #data: Data retrieved from the database
        #page: The current page
        #Number of data items per page
    def paginate(self, data: list, page: int = 1, per_page: int = 10):
        if page < 1 or per_page < 1:
            raise ValueError('page and per_page must be greater than 0')

        total = len(data)
        pages = (total + per_page - 1) // per_page

        start = (page - 1) * per_page
        end = start + per_page

        return {
            'items': data[start:end],
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages,
            'has_next': page < pages,
            'has_previous': page > 1
        }

    #==============get all==============
    def get_all(self, model= None):
        if not model:
            raise MissingDataError('the model is not defined')
        return self.db.get_all(model)

    #==============get first==============
    def get_first(self, model= None, **data:dict):
        if not model:
            raise MissingDataError('the model is not defined')
        return model.query.filter_by(**data).first()

    #==============count all==============
    def count_all(self, model= None):
        if not model:
            raise MissingDataError('the model is not defined')
        return self.db.count(model)

    #==============create==============
    def create(self, model= None, **data:dict):
        if not model:
            raise MissingDataError('the model is not defined')
        model = model(**data)
        self.db.add(model)
        return model

    #==============update==============
    def update(self, model= None, id:int = None, **data:dict):
        if not model or not id:
            raise MissingDataError('the model or id is not defined')
        elif id <= 0:
            raise VaildDataError('the id is not valid')
        self.db.update(model, id, **data)

    #==============delete==============
    def delete(self, model= None, id:int = None):
        if not model or not id:
            raise MissingDataError('the model or id is not defined')
        self.db.delete(model, id)

    #==============delete all==============
    def delete_all(self, model= None, **data:dict):
        if not model:
            raise MissingDataError('the model is not defined')
        self.db.delete_all(model, **data)

    #==============select==============
    def select(self, model= None, *columns:str):
        if not model:
            raise MissingDataError('the model is not defined')
        return self.db.select(model, *columns)

    #==============order==============
    def order(self, data:list , order_by:str):
        if not data or not order_by:
            raise MissingDataError('the data or order_by is not defined')
        return sorted(data, key=lambda x: getattr(x, order_by))

    #==============search==============
    def search(self, model= None, search:str = None):
        if not model or not search:
            raise MissingDataError('the model or search is not defined')
        return model.query.with_entities(model).all()