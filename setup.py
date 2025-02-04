from setuptools import setup, find_packages

setup(
    name='medrouter',
    version='0.1.0',
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
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache 2.0 License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
) 