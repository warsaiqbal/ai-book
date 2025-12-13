from setuptools import setup

package_name = 'ros2_nervous_system'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='maintainer',
    maintainer_email='maintainer@todo.todo',
    description='ROS2 Nervous System for robot control',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'basic_publisher = ros2_nervous_system.basic_publisher:main',
            'basic_subscriber = ros2_nervous_system.basic_subscriber:main',
            'simple_decision_maker = ros2_nervous_system.simple_decision_maker:main',
        ],
    },
)