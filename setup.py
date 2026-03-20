from setuptools import setup

setup(
    name='table-differ',
    description='Excel table difference generator tool',
    long_description='Excel table difference generator tool',
    author='Ferenc Nandor Janky & Attila Gombos',
    author_email='info@effective-range.com',
    scripts=['bin/table-differ.py'],
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=['openpyxl', 'pandas']
)
