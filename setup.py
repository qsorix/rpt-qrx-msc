from distutils.core import setup

setup(
    name = 'arete',
    version = '1.0',
    description = 'Network testing tool',
    author = 'Krzysztof Rutka & Tomasz Rydzynski',
    packages = ['AreteMaster', 'AreteMaster/command', 'AreteMaster/common', 'AreteMaster/config', 'AreteMaster/controller', 'AreteMaster/utils',
        'AreteMaster/plugins', 'AreteMaster/plugins/connections', 'AreteMaster/plugins/drivers', 'AreteMaster/plugins/frontends',
        'AreteSlave', 'AreteSlave/modules', 'AreteSlave/common', 'AreteSlave/database'],
    scripts = ['arete', 'arete-slave', 'arete-poker']
)

