from setuptools import setup, find_packages

setup(
    name="ToolsTranslator",
    version="0.1.0",
    description="Una librería de soporte para traducir archivos i18n u otros formatos ademas de dar soporte para traducción eficiente.",
    author="Walter Cun Bustamante",
    author_email="waltercunbustamante@gmail.com",
    url="https://github.com/waltercun/ToolsTranslator",
    packages=find_packages(),  # Encuentra automáticamente los paquetes.
    install_requires=[
        "requests",  # Por ejemplo, si usas requests
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
