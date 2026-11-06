#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比格多栋 - 桌面宠物 安装脚本
Beagle Desktop Pet Setup Script
"""

from setuptools import setup

setup(
    name="beagle_pet",
    version="1.0.0",
    description="比格多栋桌面宠物 - A cute Beagle that walks around your screen",
    author="BeaglePet",
    py_modules=["beagle_pet"],
    python_requires=">=3.7",
    install_requires=[
        "PyQt5>=5.15.0",
    ],
    entry_points={
        "console_scripts": [
            "beagle_pet=beagle_pet:main",
        ],
    },
)
