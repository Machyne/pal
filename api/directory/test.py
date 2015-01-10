from directory_api import Directory
from models import Building, Major, Student, FacStaff

d = Directory()
print d.find_people(first_name="Matt", last_name="Cotter")
d.cleanup()