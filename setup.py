from setuptools import setup

if __name__ == '__main__':
    setup(
        name='phase',
        version='0.0.1',
        description="Automatic Steve Reich phasing music.",
        author='Jonathan Marmor',
        author_email='jmarmor@gmail.com',
        url='https://github.com/jonathanmarmor/phase',
        packages=['phase'],
        long_description="""Automatic Steve Reich phasing music.""",
        classifiers=[
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Programming Language :: Python",
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
        ],
        keywords='music',
        license='GPL',
        install_requires=[
            'sox',
        ],
    )
