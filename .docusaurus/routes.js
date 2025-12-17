import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/login',
    component: ComponentCreator('/login', 'a8c'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '67b'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '8ee'),
        routes: [
          {
            path: '/docs/tags',
            component: ComponentCreator('/docs/tags', 'fce'),
            exact: true
          },
          {
            path: '/docs/tags/action',
            component: ComponentCreator('/docs/tags/action', '29f'),
            exact: true
          },
          {
            path: '/docs/tags/ai',
            component: ComponentCreator('/docs/tags/ai', 'bd3'),
            exact: true
          },
          {
            path: '/docs/tags/gazebo',
            component: ComponentCreator('/docs/tags/gazebo', 'a4c'),
            exact: true
          },
          {
            path: '/docs/tags/isaac',
            component: ComponentCreator('/docs/tags/isaac', '56d'),
            exact: true
          },
          {
            path: '/docs/tags/language',
            component: ComponentCreator('/docs/tags/language', '21b'),
            exact: true
          },
          {
            path: '/docs/tags/ros-2',
            component: ComponentCreator('/docs/tags/ros-2', '361'),
            exact: true
          },
          {
            path: '/docs/tags/unity',
            component: ComponentCreator('/docs/tags/unity', 'd98'),
            exact: true
          },
          {
            path: '/docs/tags/vision',
            component: ComponentCreator('/docs/tags/vision', '0f7'),
            exact: true
          },
          {
            path: '/docs/tags/vla',
            component: ComponentCreator('/docs/tags/vla', '3dd'),
            exact: true
          },
          {
            path: '/docs',
            component: ComponentCreator('/docs', '5cf'),
            routes: [
              {
                path: '/docs/appendix',
                component: ComponentCreator('/docs/appendix', '2b5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/assessments-capstone',
                component: ComponentCreator('/docs/assessments-capstone', '42b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/cloud-vs-onprem',
                component: ComponentCreator('/docs/cloud-vs-onprem', '475'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/deployment-integrations',
                component: ComponentCreator('/docs/deployment-integrations', '4b3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/hardware-requirements',
                component: ComponentCreator('/docs/hardware-requirements', '663'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module1-ros2',
                component: ComponentCreator('/docs/module1-ros2', '5ef'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module2-digital-twin',
                component: ComponentCreator('/docs/module2-digital-twin', 'e77'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module3-isaac',
                component: ComponentCreator('/docs/module3-isaac', 'e20'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module4-vla',
                component: ComponentCreator('/docs/module4-vla', '01b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/robot-lab-options',
                component: ComponentCreator('/docs/robot-lab-options', '415'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/weekly-breakdown',
                component: ComponentCreator('/docs/weekly-breakdown', '776'),
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
    path: '/',
    component: ComponentCreator('/', '2bc'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
