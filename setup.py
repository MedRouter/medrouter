from setuptools import setup, find_packages

setup(
    name='medrouter',
    version='0.1.0',
    license='Apache2.0',
    license_files=['LICENSE'],
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='PYCAD',
    author_email='contact@pycad.co',
    description='A library for calling different APIs for medical AI usecases.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/MedRouter/medrouter',
    entry_points={
        'console_scripts': [
            'medrouter=medrouter.cli:main',
        ],
    },
    python_requires='>=3.6',
) 