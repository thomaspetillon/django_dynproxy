django_dynproxy
===============

Dynamic proxy models for Django

WARNING : THIS IS AN ALPHA RELEASE. NOT RECOMMENDED FOR PRODUCTION USE

Installation :
--------------

pip install django_dynproxy

Usage :
---------

1) Create a concrete model
2) Create a Django proxy model deriving from the concrete model
3) Define a metaclass using dynproxy_metaclass_factory
4) Add the __metaclass__ to your proxy model class


Sample :
---------

from dynproxy.utils import dynproxy_metaclass_factory

TRAVELER_TYPE_PILOT = '1'
TRAVELER_TYPE_PASSENGER = '2'

TRAVELER_TYPES = (
    (TRAVELER_TYPE_PILOT,_(u"Pilot")),
    (TRAVELER_TYPE_PASSENGER,_(u"Passenger"))
)

class Traveler(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    type = models.CharField(max_length=200,choices=TRAVELER_TYPES)        
    passport_number = models.CharField(max_length=200,blank=True)
    trigram = models.CharField(max_length=200,blank=True)
    pilot_category = models.ForeignKey(PilotCategory,null=True,blank=True)
    
    
    def __unicode__(self):
        return "%s %s" % (self.first_name,self.last_name)
    
def traveler_manager_factory(traveler_type):
    class _TravelerManager(Manager):
        def get_query_set(self):        
            return super(_TravelerManager,self).get_query_set().filter(type=traveler_type)
    return _TravelerManager

PilotManager = traveler_manager_factory(TRAVELER_TYPE_PILOT)
PassengerManager = traveler_manager_factory(TRAVELER_TYPE_PASSENGER)

                
PilotMetaclass = dynproxy_metaclass_factory(    
    mandatory_fields=['trigram','pilot_category'],
    fields_to_exclude=['passport_number']
    )

PassengerMetaclass = dynproxy_metaclass_factory(    
    mandatory_fields = ['passport_number'],
    fields_to_exclude =['trigram','pilot_category']
    )

        
class Pilot(Traveler):
    __metaclass__ = PilotMetaclass
    objects = PilotManager()
    class Meta:
        proxy = True
        
class Passenger(Traveler):
    __metaclass__ = PassengerMetaclass
    objects = PassengerManager()
    class Meta:
        proxy = True


