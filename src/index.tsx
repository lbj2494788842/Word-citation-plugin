import React from 'react';
import ReactDOM from 'react-dom/client';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { App } from './App';

// 等待 Office.js 加载完成后再渲染（但保留预览能力）
const renderApp = () => {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <FluentProvider theme={webLightTheme}>
        <App />
      </FluentProvider>
    </React.StrictMode>
  );
};

// 如果 Office.js 已可用，注册 onReady
if (typeof (window as any).Office !== 'undefined') {
  (window as any).Office.onReady = (info: any) => {
    console.log('✅ Office.js 已就绪', info.host, info.platform);
    renderApp();
  };
} else {
  // 不在 Word 环境中（浏览器调试），直接渲染
  console.log('ℹ️ 非 Word 环境，以预览模式运行');
  renderApp();
}
