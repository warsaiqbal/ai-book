// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Introduction & Course Overview',
      items: ['intro'],
    },
    {
      type: 'category',
      label: 'Module 1 — ROS2: Robotic Nervous System',
      items: ['module1-ros2'],
    },
    {
      type: 'category',
      label: 'Module 2 — Gazebo & Unity: The Digital Twin',
      items: ['module2-digital-twin'],
    },
    {
      type: 'category',
      label: 'Module 3 — NVIDIA Isaac: AI-Robot Brain',
      items: ['module3-isaac'],
    },
    {
      type: 'category',
      label: 'Module 4 — Vision-Language-Action (VLA)',
      items: ['module4-vla'],
    },
    {
      type: 'category',
      label: 'Weekly Breakdown (Weeks 1–13)',
      items: ['weekly-breakdown'],
    },
    {
      type: 'category',
      label: 'Assessments & Capstone',
      items: ['assessments-capstone'],
    },
    {
      type: 'category',
      label: 'Hardware Requirements',
      items: ['hardware-requirements'],
    },
    {
      type: 'category',
      label: 'Robot Lab Options',
      items: ['robot-lab-options'],
    },
    {
      type: 'category',
      label: 'Cloud vs On-Prem Considerations',
      items: ['cloud-vs-onprem'],
    },
    {
      type: 'category',
      label: 'Deployment & Integrations',
      items: ['deployment-integrations'],
    },
    {
      type: 'category',
      label: 'Appendix',
      items: ['appendix'],
    },
  ],
};

module.exports = sidebars;