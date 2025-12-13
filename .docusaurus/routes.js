import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/qwen/login',
    component: ComponentCreator('/qwen/login', 'fbd'),
    exact: true
  },
  {
    path: '/qwen/docs',
    component: ComponentCreator('/qwen/docs', '686'),
    routes: [
      {
        path: '/qwen/docs',
        component: ComponentCreator('/qwen/docs', 'f24'),
        routes: [
          {
            path: '/qwen/docs/tags',
            component: ComponentCreator('/qwen/docs/tags', '608'),
            exact: true
          },
          {
            path: '/qwen/docs/tags/action',
            component: ComponentCreator('/qwen/docs/tags/action', '839'),
            exact: true
          },
          {
            path: '/qwen/docs/tags/ai',
            component: ComponentCreator('/qwen/docs/tags/ai', '3ef'),
            exact: true
          },
          {
            path: '/qwen/docs/tags/gazebo',
            component: ComponentCreator('/qwen/docs/tags/gazebo', 'f1c'),
            exact: true
          },
          {
            path: '/qwen/docs/tags/isaac',
            component: ComponentCreator('/qwen/docs/tags/isaac', 'c3e'),
            exact: true
          },
          {
            path: '/qwen/docs/tags/language',
            component: ComponentCreator('/qwen/docs/tags/language', '9d5'),
            exact: true
          },
          {
            path: '/qwen/docs/tags/ros-2',
            component: ComponentCreator('/qwen/docs/tags/ros-2', '855'),
            exact: true
          },
          {
            path: '/qwen/docs/tags/unity',
            component: ComponentCreator('/qwen/docs/tags/unity', 'f17'),
            exact: true
          },
          {
            path: '/qwen/docs/tags/vision',
            component: ComponentCreator('/qwen/docs/tags/vision', '4ae'),
            exact: true
          },
          {
            path: '/qwen/docs/tags/vla',
            component: ComponentCreator('/qwen/docs/tags/vla', '6f7'),
            exact: true
          },
          {
            path: '/qwen/docs',
            component: ComponentCreator('/qwen/docs', 'af9'),
            routes: [
              {
                path: '/qwen/docs/appendix',
                component: ComponentCreator('/qwen/docs/appendix', '33d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/qwen/docs/assessments-capstone',
                component: ComponentCreator('/qwen/docs/assessments-capstone', 'c18'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/qwen/docs/cloud-vs-onprem',
                component: ComponentCreator('/qwen/docs/cloud-vs-onprem', '96d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/qwen/docs/deployment-integrations',
                component: ComponentCreator('/qwen/docs/deployment-integrations', '860'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/qwen/docs/hardware-requirements',
                component: ComponentCreator('/qwen/docs/hardware-requirements', '009'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/qwen/docs/intro',
                component: ComponentCreator('/qwen/docs/intro', '75e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/qwen/docs/module1-ros2',
                component: ComponentCreator('/qwen/docs/module1-ros2', 'b20'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/qwen/docs/module2-digital-twin',
                component: ComponentCreator('/qwen/docs/module2-digital-twin', '58c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/qwen/docs/module3-isaac',
                component: ComponentCreator('/qwen/docs/module3-isaac', 'c41'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/qwen/docs/module4-vla',
                component: ComponentCreator('/qwen/docs/module4-vla', '4b2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/qwen/docs/robot-lab-options',
                component: ComponentCreator('/qwen/docs/robot-lab-options', 'dd0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/qwen/docs/weekly-breakdown',
                component: ComponentCreator('/qwen/docs/weekly-breakdown', '236'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/qwen/',
    component: ComponentCreator('/qwen/', '47c'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
