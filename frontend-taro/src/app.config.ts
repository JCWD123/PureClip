export default {
  pages: [
    'pages/profile/index',
    'pages/persona/index',
    'pages/rest/index',
    'pages/meal/index',
    'pages/weather/index',
    'pages/health-tip/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#fff',
    navigationBarTitleText: '健康档案助手',
    navigationBarTextStyle: 'black'
  },
  tabBar: {
    color: '#666',
    selectedColor: '#1890ff',
    backgroundColor: '#fff',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/profile/index',
        text: '健康档案'
      },
      {
        pagePath: 'pages/rest/index',
        text: '作息提醒'
      },
      {
        pagePath: 'pages/meal/index',
        text: '饮食建议'
      },
      {
        pagePath: 'pages/weather/index',
        text: '天气推送'
      },
      {
        pagePath: 'pages/health-tip/index',
        text: '养生妙招'
      }
    ]
  }
}

