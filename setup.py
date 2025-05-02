"""
Setup Configuration

This module contains the package setup configuration for the chat application.
It defines package metadata, dependencies, and entry points for command-line scripts.
"""
from setuptools import setup, find_packages

setup(
    name="chat_app",
    version="0.1.0",
    description="A chat application with server and client components",
    author="Chat App Team",
    packages=find_packages(),
    install_requires=[
        "bcrypt==4.1.2",
        "colorama==0.4.6",
    ],
    entry_points={
        'console_scripts': [
            'chat-client=chat_app.client.__main__:main',
            'chat-server=chat_app.server.__main__:main',
            'chat-app=chat_app.__main__:main',
        ],
    },
    python_requires='>=3.8',
) 