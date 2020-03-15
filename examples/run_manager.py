import pathlib
import nebula
import os

p = pathlib.Path(__file__).parent.absolute()
p = os.path.split(p)
# p = os.path.join(p[0], "resources", "nebula-zed.yaml")
p = os.path.join(p[0], p[1], "resources", "nebula-zed.yaml")

m = nebula.manager(configfilename=p)
m.run_test()