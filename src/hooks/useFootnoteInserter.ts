import { useState, useCallback, useEffect } from 'react';

// Office.js 全局类型声明（通过 CDN 加载）
declare global {
  interface Window {
    Office: typeof Office;
  }
}

// Office.js 的 Common API 类型定义
declare namespace Office {
  let onReady: (callback: (info: { host: string; platform: string }) => void) => void;
  interface Context {
    document: {
      body: {
        footnotes: {
          add: (content: string) => void;
        };
      };
    };
  }
  let context: Context;
}

export function useFootnoteInserter() {
  const [isInserting, setIsInserting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOfficeReady, setIsOfficeReady] = useState(false);

  // 等待 Office.js 初始化完成
  useEffect(() => {
    // 如果 Office 已经就绪，直接标记
    if (typeof window.Office !== 'undefined' && window.Office.context) {
      setIsOfficeReady(true);
      return;
    }

    // 否则等待 onReady 回调
    const timer = setInterval(() => {
      if (typeof window.Office !== 'undefined' && window.Office.context) {
        setIsOfficeReady(true);
        clearInterval(timer);
      }
    }, 200);

    return () => clearInterval(timer);
  }, []);

  const insertFootnote = useCallback(async (citationText: string): Promise<boolean> => {
    setIsInserting(true);
    setError(null);

    try {
      // 检查 Office.js 是否可用
      if (typeof window.Office === 'undefined' || !window.Office.context) {
        throw new Error('Word API 未就绪，请在 Word 中打开此插件');
      }

      const office = window.Office;

      // 通过 Common API 在光标位置插入脚注
      // Office.context.document.body.footnotes.add() 会自动在光标位置创建脚注引用标记
      // 并在页面底部添加脚注内容
      office.context.document.body.footnotes.add(citationText);

      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '插入脚注时发生未知错误';
      setError(errorMessage);
      return false;
    } finally {
      setIsInserting(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    insertFootnote,
    isInserting,
    error,
    clearError,
    isOfficeReady
  };
}
