from django.db.models.base import ModelBase
from django.db.models.fields.related import ForeignKey
from django.db.models.fields import CharField, TextField

def clone_field_cache_for_dynproxy(model_class,fields_to_exclude):
    result = ()    
    for item in model_class._meta._field_cache:
        if item[0].name not in fields_to_exclude:
            result += (item,)
    return result

def clone_field_name_cache_for_dynproxy(model_class,fields_to_exclude):
    result = []    
    for item in model_class._meta._field_name_cache:
        if item.name not in fields_to_exclude:
            result.append(item)
    return result


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
            # Exclude specified fields            
            model_class._meta._field_cache =  clone_field_cache_for_dynproxy(model_class,fields_to_exclude)
            model_class._meta._field_name_cache = clone_field_name_cache_for_dynproxy(model_class,fields_to_exclude)            
            # Make specified fields mandatory
            for f in model_class._meta.fields:
                if f.name in mandatory_fields:
                    f.blank = False
                    f.null = False
            # Return updated model class
            return model_class
    return _DynProxyMetaclass
