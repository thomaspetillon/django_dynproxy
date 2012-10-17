import copy
from django.db.models.base import ModelBase
from django.db.models.fields.related import ForeignKey
from django.db.models.fields import CharField, TextField

def dynproxy_metaclass_factory(mandatory_fields,fields_to_exclude):
    class _DynProxyMetaclass(ModelBase):
        """ A Model Metaclass adding dynamic proxy possibilities """  
        def __new__(cls, name, bases, attrs):            
            model_class = super(_DynProxyMetaclass, cls).__new__(cls, name, bases, attrs)            
            # Create fake attribute for fields we are about to exclude
            for name in fields_to_exclude:
                attr_name = name
                model_field = model_class._meta.get_field_by_name(name)[0]                
                if type(model_field) is ForeignKey:                
                    attr_name += "_id"
                if model_field.null:
                    attr_value = None                
                if type(model_field) in [CharField,TextField]:                    
                    attr_value = ""                                            
                setattr(model_class,attr_name,attr_value)
            # Clone of field caches, excluding specified fields
            # and making mandatory specified fields
            new_field_cache = ()    
            for item in model_class._meta._field_cache:
                field_name = item[0].name
                if field_name in fields_to_exclude:
                    continue
                new_item = copy.deepcopy(item)                
                if field_name in mandatory_fields:
                    new_item[0].blank = False
                    new_item[0].null = False
                new_field_cache += (new_item,)                
            model_class._meta._field_cache =  new_field_cache
            model_class._meta._field_name_cache = [item[0] for item in model_class._meta._field_cache]
            # Return updated model class
            return model_class
    return _DynProxyMetaclass