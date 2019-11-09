import pkgutil
import sys

class Base(object):
    def __init__(self):
        print("Base created")

class ChildA(Base):
    def __init__(self):
        Base.__init__(self)

class ChildB(Base):
    def __init__(self):
        super(ChildB, self).__init__()

ChildA()
ChildB()



def load_all_modules_from_dir(dirname):
    modules = []
    for importer, package_name, _ in pkgutil.iter_modules([dirname]):
        full_package_name = '%s.%s' % (dirname, package_name)
        if full_package_name not in sys.modules:
            module = importer.find_module(package_name).load_module(package_name)
            print(module)
            modules.append(module)
    return modules

loaded_particle_modules = load_all_modules_from_dir("particles")

for each in loaded_particle_modules:
    test = each.Particle()
    #print(test.id)