from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='requester',
    version='0.1',
    packages=['requester'],
    url='',
    license='',
    author='Yerodin Richards',
    author_email='yerodin.richards@mymona.uwi.edu',
    description='Python tool to download web resources (bye bye wget & curl)',
    entry_points={
        'console_scripts': ['reqr=requester.command_line:main'],
    },
    include_package_data=True,
    zip_safe=False
)
