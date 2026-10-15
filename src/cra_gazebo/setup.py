from glob import glob
from setuptools import setup
setup(name='cra_gazebo', version='0.1.0', packages=['cra_gazebo'],
      data_files=[('share/ament_index/resource_index/packages', ['resource/cra_gazebo']),
                  ('share/cra_gazebo', ['package.xml', 'LICENSE']),
                  ('share/cra_gazebo/launch', glob('launch/*.launch.py')),
                  ('share/cra_gazebo/worlds', glob('worlds/*.sdf'))],
      install_requires=['setuptools'], zip_safe=True,
      maintainer='Jiwoon Choi', maintainer_email='zzjoe4115@gmail.com',
      description='CRA minimal Gazebo differential drive demo', license='MIT',
      entry_points={'console_scripts': ['executor_node = cra_gazebo.executor_node:main']})
